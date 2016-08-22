from django.contrib import admin

from tenant.models import Client

import tenant_schemas

#if tenant_schemas.utils.connection.get_tenant().schema_name == 'public':
    #admin.site.register(Client)
