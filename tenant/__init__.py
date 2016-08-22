from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
TENANT_KEY='_tenant_id'

@receiver(user_logged_in)
def addTenantToSession(**kwargs):
    from django import db
    from django.contrib.auth.models import User
    from tenant_schemas.utils import get_tenant_model
    from tenant_schemas.utils import get_public_schema_name
    from tenant_schemas.utils import tenant_context

    try:
        User.objects.get(pk=kwargs['user'].pk, username=kwargs['user'].username)
        kwargs['request'].session[TENANT_KEY] = db.connection.tenant.id
    except User.DoesNotExist:
        tenant = get_tenant_model().objects.get(schema_name=get_public_schema_name())
        with tenant_context(tenant):
            User.objects.get(pk=kwargs['user'].pk, username=kwargs['user'].username)
        kwargs['request'].session[TENANT_KEY] = tenant.id
