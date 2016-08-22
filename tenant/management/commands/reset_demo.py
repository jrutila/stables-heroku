from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from tenant_schemas.utils import get_tenant_model

from stables.models import Participation
from stables.models import UserProfile
from stables.models import Horse
from stables.models import Accident

from django.contrib.comments.models import Comment
import random
import string
import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "etunimet.txt")) as f:
    first_names = f.readlines()

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "sukunimet.txt")) as f:
    last_names = f.readlines()

horse_names = [
        "Arenda", "Aukusti", "Chilla", "Diva", "Hopea", "Lady", "Melanie", "Susanna", "Vinkku",
        "Wilma", "Dodi", "Deniro", "Elrond", "Iivana", "Laukko", "Viima", "Pedro", "Kaapo",
        "Rurik", "Riko", "Ronny", "Sultan", "Nuoli", "Tahti", "Sepi", "Luikku", "Luiru",
        "Anka", "Salama", "Perttu", "Leisku", "Tuomi", "Malla"
        ]

def get_random(arr):
    return arr[random.randint(1, len(arr)-1)]

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        export_schema='suursuo'
        schema_name='demo'
        datadir='data'
        from django.core.management import call_command
        connection.set_schema_to_public()
        tenant = get_tenant_model().objects.get(schema_name=schema_name)
        call_command('export', schema=export_schema, datadir=datadir, time="weeks:2", interactive=False)
        call_command('import', schema=schema_name, datadir=datadir, interactive=False)
        connection.set_tenant(tenant, include_public=False)
        for u in User.objects.exclude(id=1):
            u.first_name = get_random(first_names)
            u.last_name = get_random(last_names)
            u.username = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
            u.email = ""
            u.save()
        print "Users scrambled"

        UserProfile.objects.all().update(phone_number=None)
        print "UserProfiles scrambled"

        Participation.objects.exclude(note="").update(note='Lorem ipsum solem dolor amet...')
        print "Participation notes scrambled"

        for h in Horse.objects.all():
            h.name = get_random(horse_names)
            horse_names.remove(h.name)
            h.save()
        print "Horse names scrambled"
        
        Comment.objects.all().update(comment='Lorem ipsum solem')
        print "Comments scrambled"

        Accident.objects.all().update(description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut lobortis libero non elit eleifend, sed rutrum erat ullamcorper. Aenean non elementum elit, ut mollis libero. Maecenas id neque quis sem fermentum pharetra sit amet sed metus.')
        print "Accidents scrambled"
