import json

from django.core.management.base import BaseCommand, CommandError
from uniauth_saml2_idp.utils import get_idp_config

from uniauth_saml2_idp.models import MetadataStore


class Command(BaseCommand):
    help = 'Metadata Query protocol'

    def add_arguments(self, parser):
        parser.epilog = 'Example: ./manage.py mdquery -e https://auth.unical.it/idp/metadata/ -f json'
        parser.add_argument('-e', required=True,
                            help="Entity to request metadata for")
        parser.add_argument(
            '-f', default=['json', 'saml2'], help='output format')
        parser.add_argument('-debug', required=False, action="store_true",
                            help="see debug message")

    def handle(self, *args, **options):
        idp = get_idp_config()
        for md in MetadataStore.objects.filter(is_active=1,
                                               is_valid=1):
            if md.type in ('file', 'local'):
                idp.metadata.load(md.type, md.url)
            else:
                idp.metadata.load(md.type,
                                  url=md.url, ca_cert=md.file,
                                  **json.loads(md.kwargs))
        res = idp.metadata[options['e']]
        if options['f'] == 'json':
            print(json.dumps(res, indent=2))
        else:
            print(idp.metadata.dumps())
