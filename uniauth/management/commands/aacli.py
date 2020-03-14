from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from uniauth.utils import get_idp_config


class Command(BaseCommand):
    help = 'Attribute release query'

    def add_arguments(self, parser):
        # parser.add_argument('-test', required=False, action="store_true",
                            # help="do send any email, just test")
        parser.add_argument('-debug', required=False, action="store_true",
                            help="see debug message")

    def handle(self, *args, **options):
        pass
