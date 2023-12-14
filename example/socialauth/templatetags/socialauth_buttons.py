import logging

from allauth.socialaccount.models import SocialApp

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString


logger = logging.getLogger("socialauth")
register = template.Library()


@register.simple_tag
def is_social_auth_enabled():
    res = SocialApp.objects.count()
    if res:
        return True


@register.simple_tag
def is_google_enabled():
    return SocialApp.objects.filter(provider="google").count()


@register.simple_tag
def is_azure_enabled():
    return  SocialApp.objects.filter(provider="azure").count()


@register.simple_tag
def is_microsoft_enabled():
    return  SocialApp.objects.filter(provider="microsoft").count()
