import os
from django.core.management.base import BaseCommand
from tenant.models import Client
from django.db import connection
import tablib
from optparse import make_option
from tenant_schemas.utils import get_tenant_model

deps = [
  'User',
  'RiderLevel',
  'CustomerInfo',
  'RiderInfo',
  'InstructorInfo',
  'UserProfile',
  'TicketType',
  'Transaction',
  'Ticket',
  'Calendar',
  'Rule',
  'Event',
  'Course',
  'Horse',
  'AccidentType',
  'Participation',
    ]

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option("-d", "--data", dest="datadir"),
            make_option("-s", "--schema", dest="schema"),)

    def handle(self, *args, **kwargs):
        if not kwargs['schema']:
            print "You should use schema"
        connection.set_schema_to_public()
        tenant = get_tenant_model().objects.get(schema_name=kwargs['schema'])
        print "Importing for %s..." % tenant
        schema_name = tenant.schema_name
        datadir = kwargs['datadir']

        # Reset the whole schema
        connection.set_schema_to_public()
        cursor = connection.cursor()
        cursor.execute('DROP SCHEMA %s CASCADE' % schema_name)
        cursor.execute('CREATE SCHEMA %s' % schema_name)
        from django.core.management import call_command
        call_command('sync_schemas', schema_name=schema_name, interactive=False)
        call_command('migrate_schemas', schema_name=schema_name, interactive=False)
        connection.set_tenant(tenant, include_public=False)
        print "Schema reseted for %s" % schema_name

        # Import the resources

        # Disconnect signals
        from stables.models.user import create_user_profile
        from django.db.models.signals import post_save
        from stables.models import User, Participation
        post_save.disconnect(create_user_profile, sender=User, dispatch_uid="users-profilecreation-signal")
        post_save.disconnect(create_user_profile, sender=Participation)
        post_save.receivers = None

        # Resolve resources
        mod = __import__('resources')
        mods = [ x[0] for x in mod.__dict__.items() if 'Resource' in x[0]]

        modules = []
        for d in deps:
            resname = "%sResource" % d
            modules.append((resname, mod.__dict__[resname]))
            mods.remove(resname)

        for m in mods:
            modules.append((m, mod.__dict__[m]))

        # Actual import
        for m in modules:
            mname = m[0]
            if 'Resource' in mname:
                print mname
                res = m[1]
                filename = os.path.join(datadir, '%s.csv' % mname)
                if os.path.exists(filename):
                    f = open(filename, 'r')
                    data = tablib.Dataset()
                    data.csv = f.read()
                    res().import_data(data, raise_errors=True)
                    f.close()
                else:
                    print "Skipped %s" % filename

        # reset sequences
        cursor = connection.cursor()
        with open('seq_update.sql', 'r') as func_file:
            func = func_file.read()
            func = func.replace('%', '%%')
            cursor.execute(func)
        cursor.execute("select * from seq_update('%s')" % schema_name)
