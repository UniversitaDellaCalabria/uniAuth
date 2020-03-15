import json

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from uniauth.views import IdPHandlerViewMixin, get_IDP
from uniauth.utils import get_idp_config, get_idp_sp_config


class Command(BaseCommand):
    help = 'Attribute release query'

    def add_arguments(self, parser):
        parser.epilog='Example: ./manage.py aacli -e https://auth.unical.it/idp/metadata/ -u joe'
        parser.add_argument('-e', required=True,
                            help="Entity to request metadata for")
        parser.add_argument('-u', required=True,
                            help="username to test")
        parser.add_argument('-debug', required=False, action="store_true",
                            help="see debug message")

    def handle(self, *args, **options):
        uid = options['u']
        eid = options['e']
        
        idph =  IdPHandlerViewMixin()
        idph.IDP = get_IDP()
        idph.set_sp(eid)

        idph.set_processor()
        idph.processor.create_identity(uid, idph.sp)

        user = get_user_model().objects.filter(username=uid).first()
        if not user:
            user = get_user_model().objects.create(username=uid,
                                                   origin='aacli')
        
        identity, policy, ava = idph.get_ava(user)
        print('SP Configuration:')
        print(json.dumps(idph.sp['config'], indent=2))
        print()
        print('TargetedID: {}'.format(idph.processor.eduPersonTargetedID))
        print(json.dumps(ava, indent=2))
