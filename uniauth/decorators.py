import logging

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseBadRequest
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext as _
from django.shortcuts import render_to_response
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT

from .utils import repr_saml, get_idp_config


logger = logging.getLogger(__name__)


def store_params_in_session(request):
    """ Entrypoint view for SSO. Gathers the parameters from the
        HTTP request and stores them in the session

        It do not return anything because request come as pointer
    """
    if request.method == 'POST':
        passed_data = request.POST
        binding = BINDING_HTTP_POST
    else:
        passed_data = request.GET
        binding = BINDING_HTTP_REDIRECT

    saml_request = passed_data.get('SAMLRequest')
    if saml_request:
        msg = "--- SAML request [\n{}] ---"
        logger.debug(msg.format(repr_saml(saml_request,
                                b64=True)))
    else:
        msg = _('not a valid SAMLRequest: {}').format(e)
        return render_to_response('error.html',
                                  {'exception_type':msg,
                                   'exception_msg':_('Please renew your SAML Request'),
                                   'extra_message': _('Not a valid SAML Session, Probably your request is '
                                                      'expired or you refreshed your page getting in a stale '
                                                      'request. Please come back to your SP and renew '
                                                      'the authentication request')},
                                   status=403)
    
    # try to parse an authn request to get force_authn if available
    try:
        # force_authn check
        IDP = get_idp_config(settings.SAML_IDP_CONFIG)
        req_info = IDP.parse_authn_request(saml_request,
                                           binding)
        if req_info.message.force_authn:
            logout(request)

        logger.info("SSO AuthnRequest: {} [{}]".format(req_info.message.issuer.text,
                                                       req_info.message.id))
    except Exception as e:
        # it's a SLO request...
        pass
    # end force_authn check
    
    request.session['SAMLRequest'] = saml_request
    request.session['Binding'] = binding
    request.session['RelayState'] = passed_data.get('RelayState', '')


def store_params_in_session_func(func_to_decorate):
    """ store_params_in_session as a funcion decorator
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        try:
            store_params_in_session(request)
            return func_to_decorate(*original_args, **original_kwargs)
        except Exception as e:
            msg = _('not a valid SAMLRequest: {}').format(e)
            return render_to_response('error.html',
                                      {'exception_type':msg,
                                       'exception_msg':_('Please renew your SAML Request'),
                                       'extra_message': _('Not a valid SAML Session, Probably your request is '
                                                          'expired or you refreshed your page getting in a stale '
                                                          'request. Please come back to your SP and renew '
                                                          'the authentication request')},
                                      status=403)
    return new_func


def require_saml_request(func_to_decorate):
    """ store_params_in_session as a funcion decorator
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        if not request.session.get('SAMLRequest'):
            return render_to_response('error.html',
                                      {'exception_type':_("You cannot access to this service directly"),
                                       'exception_msg':_('Please renew your SAML Request'),
                                       'extra_message': _('Not a valid SAML Session, Probably your request is '
                                                          'expired or you refreshed your page getting in a stale '
                                                          'request. Please come back to your SP and renew '
                                                          'the authentication request')},
                                      status=403)
        return func_to_decorate(*original_args, **original_kwargs)
    return new_func
