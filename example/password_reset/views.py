import logging
import re

from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django_form_builder.forms import BaseDynamicForm
from django_form_builder.utils import get_labeled_errors
from django.core.exceptions import (
    BadRequest,
    ValidationError
)
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from cryptotools.tools import (
    iat_now, 
    exp_from_now, 
    create_jwe, 
    create_jws, 
    decrypt_jwe,
    verify_jws,
    secparams_check
)

logger = logging.getLogger(__name__)

# this is the dictionary that builds the DynamicForm
constructor_dict = OrderedDict([
    # CharField
    (_('e-mail'),
        ('CustomEmailField',
            {},
            ''
        )
    ),
    (_('new password'),
        ('CustomPasswordField',
            {},
            ''
        )
    ),
    (_('confirm new password'),
        ('CustomPasswordField',
            {},
            ''
        )
    ),
    # Captcha
    ('CaPTCHA',
        ('CustomCaptchaComplexField',
            {'label': 'CaPTCHA',
             'pre_text': ''},
        '')
    ),
])  


@csrf_exempt
def password_reset(request):
    dform_data = dict(
        constructor_dict=constructor_dict,
        # data=request.POST,
        # files=request.FILES,
        remove_filefields=False,
        remove_datafields=False
    )

    if request.method == 'GET':
        form = BaseDynamicForm.get_form(**dform_data)
        d = {'form': form}
    elif request.method == 'POST':
        dform_data['data'] = request.POST
        form = BaseDynamicForm.get_form(**dform_data)
        
        if form.data['new_password'] != form.data['confirm_new_password']:
            form.errors['confirm_new_password'] = 'Password do not match'
        
        if form.is_valid():
            
            messages.add_message(
                request, 
                messages.SUCCESS, 
                _(
                    """If the data you have provided are valid you'll 
                    receive an email with the link to activate 
                    your new password"""
                )
            )
            _user = get_user_model().objects.filter(
                email = form.data['e-mail'],
                is_active = True
            ).first()

            if _user.origin:
                _user = None
            
            host = getattr(
                settings, "ENTITY_BASE_URL", "https://xdrplus-iam.acsia.org"
            )
            
            if _user:
                data = dict(
                    user_pk = _user.pk,
                    new_pass = form.cleaned_data['new_password'],
                    iat = iat_now(),
                    exp = exp_from_now(
                        minutes= getattr(settings, "PASSWORD_RESET_EXP", 1440)
                    ),
                    iss = host,
                    sub = _user.email,
                    aud = ''.join(
                        (
                            request.get_host(),
                            reverse('password_reset:password_commit')
                        )
                    )
                )
                _jws = create_jws(
                    data, settings.PRIVATE_SIGNATURE_JWKS["keys"][0]
                )
                _jwe = create_jwe(
                    _jws, settings.PUBLIC_ENCRYPTION_JWKS["keys"][0]
                )
                _link = f"{host.strip('/')}{reverse('password_reset:password_commit')}?token={_jwe}"
                _msg = settings.EMAIL_MSG_PASSWD_RESET.format(
                    **{
                        'user': _user,
                        'host': host,
                        'link': _link
                    }
                )
                logger.debug(_link)
                send_mail(
                    settings.EMAIL_SUBJECT_PASSWD_RESET,
                    _msg,
                    settings.EMAIL_FROM,
                    [_user.email],
                    fail_silently=False,
                )
                d = {}
        else:
            d = {'form': form}
            # show all error messages
            for k,v in get_labeled_errors(form).items():
                messages.add_message(
                    request, messages.ERROR,
                    f"{k}: {strip_tags(v)}"
                )
    return render(request, "password_reset.html", d)


def password_commit(request):
    token = request.GET.get('token')
    if not token:
        raise BadRequest()
    
    data = {}
    try:
        _jws = decrypt_jwe(
            token,
            settings.PRIVATE_ENCRYPTION_JWKS['keys'][0]
        )
        data = verify_jws(
            _jws,
            settings.PUBLIC_SIGNATURE_JWKS['keys'][0]
        )
    except Exception as e:
        logger.error(
            f"Error validading password reset token {token}: {e}"
        )
        raise BadRequest()
    
    # security checks
    if not secparams_check(
        data, 
        aud = request.get_raw_uri().split('?')[0],
        allowed_clients = settings.ENTITY_BASE_URL
    ):
        raise ValidationError(
            f"{data} doesn't respect the security pattern"
        )
    
    _user = get_user_model().objects.filter(
        pk = data['user_pk'],
        is_active = True
    ).first()
    
    _user.set_password(data['new_pass'])
    _user.save()
    
    messages.add_message(
        request, 
        messages.SUCCESS, 
        _(
            """Password changed successfully!"""
        )
    )
    
    return render(request, "password_reset.html", {})
    

