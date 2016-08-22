from django.contrib.sessions.backends.cached_db import SessionStore as CachedStore
from tenant_schemas.utils import get_public_schema_name
from tenant_schemas.utils import get_tenant_model
from tenant_schemas.utils import tenant_context

def fake_public_tenant():
    return get_tenant_model()(schema_name=get_public_schema_name())

class SessionStore(CachedStore):
    def load(self):
        with tenant_context(fake_public_tenant()):
            ret = super(CachedStore, self).load()
        return ret

    def save(self, must_create=False):
        with tenant_context(fake_public_tenant()):
            ret = super(CachedStore, self).save(must_create)
        return ret

    def delete(self, session_key=None):
        with tenant_context(fake_public_tenant()):
            ret = super(CachedStore, self).delete(session_key)
        return ret

    def flush(self):
        with tenant_context(fake_public_tenant()):
            ret = super(CachedStore, self).flush()
        return ret
