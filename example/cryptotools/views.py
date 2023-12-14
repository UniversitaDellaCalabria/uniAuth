import copy
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


def public_jwk(request):
    keys = copy.deepcopy(settings.PUBLIC_SIGNATURE_JWKS)
    keys['keys'].extend(settings.PUBLIC_ENCRYPTION_JWKS['keys'])
    return JsonResponse(
        keys, safe = False
    )
    
