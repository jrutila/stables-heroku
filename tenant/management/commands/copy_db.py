from io import StringIO
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.db import connections
from django.utils import timezone

from tenant.models import Client

__author__ = 'jorutila'

from collections import namedtuple, OrderedDict


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class Command(BaseCommand):
    help = 'Copy old stables database to the new one'
    def customerfororder(self, old, new, **kwargs):
        sql = """
            select user_id from %(schema)s.stables_shop_ticketproductactivator tpa
                INNER JOIN %(schema)s.stables_shop_productactivator pa ON pa.id = tpa.productactivator_ptr_id
                INNER JOIN %(schema)s.stables_userprofile up ON up.rider_id = tpa.rider_id
                WHERE order_id = %(id)d;
            """
        old.execute(sql % kwargs)
        user_id = old.fetchone()
        if user_id == None:
            self.stdout.write("No dice with order id %d" % kwargs["id"])
            return 0
        return user_id[0]

    def insertorderextra(self, new, data, schema):
        for d in data:
            d['schema'] = schema
            new.execute("update %(schema)s.stables_shop_order set extra = regexp_replace(regexp_replace('{ \"message\": \"%(text)s\" }', E'[\\n]', '\\n', 'g'), E'[\\r]', '', 'g') where id = %(order_id)d" % d)

    def add_arguments(self, parser):
         # Named (optional) arguments
        parser.add_argument('--skip',
            dest='skip',
            default=False,
            help='Skip the db tables till')
        parser.add_argument('--tenant',
            dest='tenant',
            default=False,
            help='Run only this tenant')
        parser.add_argument('--tenant-only',
            action='store_true',
            dest='tenantonly',
            default=False)
        parser.add_argument('--domain',
                           dest='domain',
                           default=False,
                           help="Give the string format for domain e.g.: %s.localhost")
        #parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        c = connections['old'].cursor()
        w = connections['default'].cursor()
        c.execute("SELECT * FROM customers_client WHERE schema_name != 'public'")
        result = dictfetchall(c)

        tables = OrderedDict()
        tables['stables_accidenttype'] = {}
        tables['stables_tickettype'] = {}
        tables['auth_user'] = {}
        tables['stables_shop_customer'] = {
            "new": "insert into %(schema)s.stables_shop_customer select id, 0, '', date '1900-01-01', '{}' from %(schema)s.auth_user;"
        }
        tables['schedule_calendar'] = {}
        tables['schedule_rule'] = {}
        tables['schedule_event'] = { "missing": ["priority"]}
        tables['schedule_occurrence'] = {}
        tables['shop_order'] = {
            "table": "stables_shop_order",
            "where": "status = 50",
            "rename": {
                "order_subtotal": "_subtotal", "order_total": "_total",
                "created": "created_at", "modified": "updated_at",
            },
            "convert": { "status": lambda x: x },
            "script": {
                "customer_id": self.customerfororder
            },
            "missing": ["cart_pk", "user_id", "billing_address_text"],
            "defaults": { "currency": "EUR", "extra": "{}", "stored_request": "{}" }
        }
        tables['stables_shop_product'] = {
            "rename": { "name": "product_name", "date_added": "created_at", "last_modified": "updated_at" },
            "convert": { "polymorphic_ctype_id": "content_type" }}
        """
        tables['shop_cart'] = {
            "table": "stables_shop_cart",
            "rename": { "date_created": "created_at", "last_updated": "updated_at", "user_id": "customer_id" },
            "defaults": { "extra": "{}" },
            "convert": {
                "customer_id": ""
            }
        }
        tables['shop_cartitem'] = {
            "table": "stables_shop_cartitem"
        }
        """
        tables['shop_orderitem'] = {
            "table": "stables_shop_orderitem",
            "rename": { "line_total": "_line_total", "unit_price": "_unit_price", "product_reference": "product_code",
                        },
            "where": "order_id in (select id from %(schema_name)s.shop_order where status = 50)",
            "missing": ["line_subtotal"],
            "defaults": {"extra": "{}"}
        }
        #tables['shop_extraorderpricefield'] = { }
        #tables['shop_extraorderitempricefield'] = {}
        tables['shop_orderextrainfo'] = {
            "data": self.insertorderextra
        }
        tables['shop_orderpayment'] = {
            "table": "stables_shop_orderpayment",
            "defaults": { "created_at": timezone.now()},
            "where": "order_id in (select id from %(schema_name)s.shop_order where status = 50)",
        }
        tables['stables_course'] = {}
        tables['stables_horse'] = {}
        tables['stables_instructorinfo'] = {}
        tables['stables_customerinfo'] = {}
        tables['stables_riderinfo'] = {}
        tables['stables_accident'] = {}
        tables['stables_riderlevel'] = {}
        tables['stables_course_allowed_levels'] = {}
        tables['stables_course_events'] = {}
        tables['stables_course_ticket_type'] = {}
        tables['stables_userprofile'] = {}
        tables['stables_enroll'] = {}
        tables['stables_courseparticipationactivator'] = {}
        #tables['stables_coursetransactionactivator'] = {}
        tables['stables_eventmetadata'] = {}
        tables['stables_instructorparticipation'] = {}
        tables['stables_participation'] = {}
        tables['stables_participationtransactionactivator'] = {}
        tables['stables_participationtransactionactivator_ticket_type'] = {}
        tables['stables_riderinfo_levels'] = {}
        tables['stables_riderlevel_includes'] = {}
        #tables['stables_shop_address'] = {}
        #tables['stables_shop_digitalshippingaddressmodel'] = {}
        tables['stables_shop_enrollproduct'] = {}
        tables['stables_shop_enrollproductactivator'] = {}
        tables['stables_shop_partshorturl'] = {}
        tables['stables_shop_productactivator'] = {}
        tables['stables_shop_ticketproduct'] = {}
        tables['stables_shop_ticketproductactivator'] = {}
        tables['stables_transaction'] = { "convert": { "content_type_id": "content_type" }}
        tables['stables_ticket'] = { "convert": { "owner_type_id": "content_type" }}
        tables['django_settings_setting'] = { "convert": { "setting_type_id": "content_type" }}
        tables['django_settings_email'] = {}
        tables['django_settings_integer'] = {}
        #tables['django_settings_longstring'] = { "table": "stables_shop_longstring" }
        tables['stables_shop_longstring'] = { "table": "stables_shop_longstring" }
        tables['django_settings_positiveinteger'] = {}
        tables['django_settings_string'] = {}

        tenant_opts = {
            "tahko": {
                "tables": {"stables_transaction": { "preconvert": { "content_type_id": lambda x: 49 if x == 29 else x } } }
            }
        }

        for tenant in result:

            if "tenant" in options:
                if (options["tenant"] and tenant["schema_name"] != options["tenant"]):
                    continue
            topts = tenant_opts[tenant["schema_name"]] if tenant["schema_name"] in tenant_opts else None

            connections["default"].set_schema("public")
            if not options["skip"]:
                #if (tenant["schema_name"] != "demo"): break
                del tenant["id"]
                t = Client(**tenant)
                if options["domain"]:
                    t.domain_url = options["domain"] % t.schema_name
                t.save()
                self.stdout.write("Created client "+tenant['domain_url'])

            if options['tenantonly']: return

            connections["old"].set_schema(tenant["schema_name"])
            connections["default"].set_schema(tenant["schema_name"])

            skipping = False
            if isinstance(options["skip"], str):
                skipping = options["skip"]
            for (name, t) in tables.items():
                tname = "%s.%s" % (tenant['schema_name'], name)
                ttopts = topts["tables"][name] if topts and name in topts["tables"] else None
                if skipping and skipping != "True":
                    if skipping == name: skipping = False
                    self.stdout.write("Skipped "+tname)
                    continue
                toname = tenant["schema_name"]+"."+t["table"] if "table" in t else tname
                opts = t

                if not "new" in opts:
                    qq = "SELECT * FROM %s" % tname
                    if "where" in opts:
                        qq = qq + " WHERE %s" % (opts["where"] % tenant)
                    self.stdout.write("Fetch data with %s" % qq)
                    c.execute(qq)
                    data = dictfetchall(c)
                fd = ""
                conv = opts["convert"] if "convert" in opts else None
                pconv = ttopts["preconvert"] if ttopts and "preconvert" in ttopts else None
                counter = 0
                ctcache = {}
                if "new" in opts:
                    w.execute(opts["new"] % {"schema": tenant['schema_name']})
                elif (len(data)) and "data" not in opts:
                    self.stdout.write("Writing %s to %s" % (tname, toname))
                    colnames = [x for x in data[0].keys() if "missing" not in opts or x not in opts["missing"]]
                    for d in data:
                        counter = counter + 1
                        vals = []
                        # iterate colnames
                        for x in colnames:
                            dd = d[x]
                            val = None
                            if pconv and x in pconv:
                                dd = pconv[x](dd)
                            if conv and x in conv and val == None:
                                if (conv[x] == "content_type"):
                                    if dd not in ctcache:
                                        oldct = ContentType.objects.using("old").get(id=dd)
                                        self.stdout.write("Try to find CT: %s" % oldct.model)
                                        newct = ContentType.objects.using("default").get(model=oldct.model)
                                        ctcache[dd] = newct.id
                                    val = ctcache[dd]
                                else:
                                    val = conv[x](dd)
                            if val == None:
                                val = default_conv(dd)
                            if val != None:
                                vals.append(val)
                        if "defaults" in opts:
                            for (dk,df) in opts["defaults"].items():
                                vals.append(df)
                        if "script" in opts:
                            for (sk,sf) in opts["script"].items():
                                vals.append(sf(c,w,schema=tenant["schema_name"], **d))

                        fd = unicode(fd) + "\t".join([unicode(x) for x in vals]) + "\n"
                    if "defaults" in opts:
                        for (dk,df) in opts["defaults"].items():
                            colnames.append(dk)
                    if "script" in opts:
                        for (sk,sf) in opts["script"].items():
                            colnames.append(sk)

                    newcolnames = [x if "rename" not in opts or x not in opts["rename"] else opts["rename"][x] for x in colnames]
                    self.stdout.write(",".join(newcolnames) + " -> "+toname)
                    #self.stdout.write(fd)
                    w.copy_from(StringIO(unicode(fd)), toname, columns=['"'+x+'"' for x in newcolnames])
                    params = {"tbl": toname, "tblsc": toname.replace(tenant["schema_name"]+".", "")}
                    check = "SELECT relname FROM pg_class WHERE relname='%(tblsc)s_id_seq';" % params
                    w.execute(check)
                    if w.fetchone() != None:
                        id_seq = "SELECT setval('%(tbl)s_id_seq', COALESCE((SELECT MAX(id)+1 FROM %(tbl)s), 1), false)" % params
                        self.stdout.write(id_seq)
                        w.execute(id_seq)
                elif (len(data)) and "data" in opts:
                    opts["data"](w, data, tenant["schema_name"])
                else:
                    self.stdout.write("No data for %s" % toname)

def default_conv(value):
    if unicode(value) == "True":
        return "t"
    if unicode(value) == "False":
        return "f"
    if value == None:
        return "\\N"
    return unicode(value).strip().replace("\r", "").replace("\n", "\\n")
