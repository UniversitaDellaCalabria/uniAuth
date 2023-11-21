import importlib

from django.apps import AppConfig
from django.db.models.signals import post_save
from . import signals


class SocialauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socialauth'

    def ready(self):
        

        myapp_models = importlib.import_module('allauth.account.models')
        model_a = getattr(myapp_models, 'EmailAddress')
        
        
        post_save.connect(
            signals.update_principal_email_if_none, 
            sender = model_a
        )
