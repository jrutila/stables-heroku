from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from tenant_schemas.utils import tenant_context
from tenant_schemas.utils import get_tenant_model
from tenant_schemas.utils import get_public_schema_name
from django import db
from tenant import TENANT_KEY
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser

def get_user(request):
    if not hasattr(request, '_cached_user'):
        if TENANT_KEY in request.session:
            tenant = get_tenant_model().objects.get(pk=request.session[TENANT_KEY])
            if tenant.schema_name == get_public_schema_name() or db.connection.schema_name == get_public_schema_name():
                with tenant_context(tenant):
                    request._cached_user = auth.get_user(request)
            elif db.connection.tenant == tenant:
                    request._cached_user = auth.get_user(request)
            else:
                request._cached_user = AnonymousUser()
        elif db.connection.schema_name == get_public_schema_name():
            request._cached_user = auth.get_user(request)
        else:
            request._cached_user = AnonymousUser()
    return request._cached_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.user = SimpleLazyObject(lambda: get_user(request))

class RestrictTenantStaffToAdminMiddleware(object):
    def process_request(self, request):
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "Restrict staff to admin middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'tenant.middleware.AuthenticationMiddleware'"
                " before the RestrictStaffToAdminMiddleware class.")
        msg = u'Tenant staff members cannot access the public admin site.'
        if reverse('admin:index') in request.path:
            if TENANT_KEY in request.session:
                tenant = get_tenant_model().objects.get(pk=request.session[TENANT_KEY])
                if request.user.is_staff and tenant.schema_name != get_public_schema_name() and not request.session[TENANT_KEY] == db.connection.tenant.id:
                    return HttpResponseForbidden(msg)
            elif db.connection.schema_name == get_public_schema_name():
                pass
            else:
                return HttpResponseForbidden(msg)
        
