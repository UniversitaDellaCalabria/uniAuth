import base64
import datetime
import copy
import logging
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import (ImproperlyConfigured,
                                    PermissionDenied,
                                    SuspiciousOperation)
from django.http import (HttpResponse,
                         HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.authn_context import (PASSWORD,
                                 AuthnBroker,
                                 authn_context_class_ref)

from saml2.assertion import Policy
from saml2.config import IdPConfig
from saml2.ident import NameID
from saml2.metadata import entity_descriptor
from saml2.s_utils import (UnknownPrincipal,
                           UnsupportedBinding,
                           UnknownSystemEntity)
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_PERSISTENT
from saml2.response import (IncorrectlySigned,)
from six import text_type

from accounts.models import PersistentId
from . decorators import (_not_valid_saml_msg,
                          store_params_in_session,
                          store_params_in_session_func,
                          require_saml_request)
from . exceptions import (MetadataNotFound,
                          MetadataCorruption,
                          UnavailableRequiredAttributes,
                          DisabledSP)
from . forms import AgreementForm, LoginForm
from . models import AgreementRecord, ServiceProvider
from . processors import BaseProcessor
from . utils import (repr_saml,
                     get_idp_config,
                     get_idp_sp_config,
                     get_client_id)


logger = logging.getLogger(__name__)


@never_cache
@require_http_methods(["GET", "POST"])
@csrf_exempt
@store_params_in_session_func
def sso_entry(request, binding='POST'):
    """ Entrypoint view for SSO. Build the saml session and redirects
        the requester to the login_process view.
    """
    # decoratos do the most
    logger.info("SSO req from client {}".format(get_client_id(request)))
    binding = request.saml_session.get('Binding', BINDING_HTTP_POST)
    IDP = get_IDP()
    try:
        req_info = IDP.parse_authn_request(request.saml_session['SAMLRequest'],
                                           binding)
    except IncorrectlySigned as exp:
        logger.error('{}'.format(exp))
        return render(request, 'error.html',
                      {'exception_type': exp,
                       'exception_msg': _("Incorrectly signed"),
                       'extra_message': _('SP Metadata '
                                          'is changed, expired '
                                          'or unavailable.')},
                       status=403)
    except Exception as exp:
        logger.error('{}'.format(exp))
        return render(request, 'error.html',
                      {'exception_type': exp},
                       status=403)

    # later we'll check if the authnrequest is older then the IDP session age
    request.saml_session['issue_instant'] = req_info.message.issue_instant

    # these are not serializable ...
    #request.saml_session['IDP'] = IDP
    #request.saml_session['req_info'] = req_info

    # Force Authn check
    if req_info.message.force_authn:
        logout(request)
        msg = "SSO AuthnRequest [force_authn=True]: {} [{}]".format(req_info.message.issuer.text,
                                                                    req_info.message.id)
        logger.info(msg)

    request.saml_session['message_id'] = req_info.message.id
    request.saml_session['issue_instant'] = req_info.message.issue_instant

    sp_id = req_info.message.issuer.text
    sp = get_idp_sp_config().get(sp_id, {})

    mduui = {}
    if not IDP.config.metadata.service(sp_id,
                                       "spsso_descriptor",
                                       'assertion_consumer_service'):
        msg = _("{} is not present in any Metadata").format(sp_id)
        raise MetadataNotFound(msg)

    try:
        mduui = IDP.metadata[sp_id]['spsso_descriptor'][0]\
                 .get('extensions', {}).get('extension_elements', [{}])[0]
    except IndexError as excp:
        logger.error('MDUUI not available: "{}"'.format(excp))

    # name_id_format also here, as made in AAcli
    # IDP.metadata[sp_id]['spsso_descriptor'][0]['name_id_format'][0]['text']

    if sp_id:
        sp_display_name = sp.get('display_name') or \
                          mduui.get('display_name', [{}])[0].get('text')
        sp_display_description = sp.get('display_description', '') or \
                                 mduui.get('description', [{}])[0].get('text') or \
                                 sp_id
        request.saml_session['sp_display_name'] = sp_display_name
        request.saml_session['sp_display_description'] = sp_display_description
        request.saml_session['sp_logo'] = mduui.get('logo', [{}])[0].get('text')

    try:
        resp_args = IDP.response_args(req_info.message)
    except UnknownSystemEntity as exp:
        logger.error('{}'.format(exp))
        return render(request, 'error.html',
                      {'exception_type': exp,
                       'exception_msg': _("This SP is not federated"),
                       'extra_message': _('Metadata is missing')},
                       status=403)

    #sp_id = resp_args.get('sp_entity_id', sp_id)
    if settings.SAML_DISALLOW_UNDEFINED_SP:
        if sp_id not in get_idp_sp_config().keys():
            return render(request, 'error.html',
                          {'exception_type': _("This SP is not allowed to access to this Service"),
                           'exception_msg': _("Attribute Processor needs "
                                              "to be configured and undefined SP are not Allowed.")},
                          status=403)

    # check if the SP was defined but disabled
    if ServiceProvider.objects.filter(entity_id=sp_id, is_active=0):
        return render(request, 'error.html',
                          {'exception_type': _("This SP is not allowed to access to this Service"),
                           'exception_msg': _("{} was disabled".format(sp_id))},
                          status=403)
    # end check
    return HttpResponseRedirect(reverse('uniauth:saml_login_process'))


class ErrorHandler(object):
    error_view = import_string(getattr(settings,
                                       'SAML_IDP_ERROR_VIEW_CLASS',
                                       'uniauth.error_views.SamlIDPErrorView'))

    def handle_error(self, request, **kwargs):
        logger.error(kwargs)
        return self.error_view.as_view()(request, **kwargs)


def get_IDP(idp_conf=settings.SAML_IDP_CONFIG):
    # Check if SP is federated
    try:
        IDP = get_idp_config(idp_conf)
    except MetadataNotFound as exp:
        logger.error('{}'.format(exp))
        return render(request, 'error.html',
                      {'exception_type': _("Unable to find Service "
                                           "Provider Metadata"),
                       'exception_msg': "",
                       'extra_message': _('SP Metadata are expired '
                                          'or not found. Please contact '
                                          'IDP technical support for '
                                          'better acknowledge')},
                       status=403)

    except MetadataCorruption as exp:
        logger.error('{}'.format(exp))
        return render(request, 'error.html',
                      {'exception_type': _("Some Metadata "
                                           "seems to be corrupted"),
                       'exception_msg': "",
                       'extra_message': _('This is a security exception. '
                                          'Please contact IdP staff.')},
                       status=403)
    return IDP


class IdPHandlerViewMixin(ErrorHandler):
    """ Contains some methods used by multiple views
    """

    def dispatch(self, request, *args, **kwargs):
        """ Construct IDP server with config from settings dict
        """
        try:
            self.IDP = get_IDP()
        except Exception as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp)
        return super().dispatch(request, *args, **kwargs)

    def convert_attributes(self, attr_name_list):
        converted_attrs = []
        for attr_id in attr_name_list:
            if not attr_id: continue
            for acs in self.IDP.config.attribute_converters:
                attr = attr_id.lower()
                if attr in acs._fro:
                    converted_attrs.append(acs._fro[attr])
                elif attr in acs._to:
                    converted_attrs.append(attr)
        return converted_attrs

    def set_sp(self, sp_entity_id):
        """ Saves SP info to instance variable
            Raises an exception if sp matching
            the given entity id cannot be found.

            If undefined SP are allowed it handles its presence in metadatastore
            and the attribute release policy.
        """
        self.sp = {'id': sp_entity_id}
        self.sp['config'] = get_idp_sp_config().get(sp_entity_id)

        sp = ServiceProvider.objects.filter(entity_id = sp_entity_id).first()

        if not self.sp['config']:
            self.sp['config'] = copy.deepcopy(settings.DEFAULT_SPCONFIG)
            self.sp['config']['force_attribute_release'] = False

        if not sp:
            # TODO: get these information from sp's metadata
            sp = ServiceProvider.objects.create(entity_id = sp_entity_id,
                                                display_name = sp_entity_id,
                                                is_valid=True,
                                                is_active = True,
                                                last_seen = timezone.localtime())
        elif not sp.is_active:
            msg = _("{} was disabled. "
                    "Please contact technical staff for informations.")
            raise DisabledSP(msg.format(sp_entity_id))
        else:
            sp.last_seen = timezone.localtime()
            sp.save()

        if self.sp['config']['force_attribute_release']:
            # IdP ignores what SP requests for and release what you configured
            return

        # check if SP asks for required attributes
        req_attrs = self.IDP.config.metadata.attribute_requirement(sp_entity_id)
        if not req_attrs: return

        # clean up unrequested attributes
        # TODO a bettere generalization with SAML2 attr mapping here
        req_attr_list = [entry['name'] for entry in req_attrs['required']]
        opt_attr_list = [entry['name'] for entry in req_attrs['optional']]

        # conversion: avoids that some attrs have identifiers instead of names
        conv_req_attr_list = self.convert_attributes(req_attr_list)
        conv_opt_attr_list = self.convert_attributes(opt_attr_list)

        attr_list = [attr for attr in conv_req_attr_list]
        attr_list.extend(conv_opt_attr_list)

        # updates newly requested attrs
        for attr in attr_list:
            # if there's some configuration about mapping ...
            if attr in settings.DEFAULT_SPCONFIG['attribute_mapping']:
                self.sp['config']['attribute_mapping'][attr] = settings.DEFAULT_SPCONFIG['attribute_mapping'][attr]
            # .. otherwise map it as it come from sp's metadata
            else:
                self.sp['config']['attribute_mapping'][attr] = [attr]

        # clean up unrequired
        to_be_removed = []
        for attr in self.sp['config']['attribute_mapping']:
            if attr not in attr_list:
                to_be_removed.append(attr)
        for attr in to_be_removed:
            del self.sp['config']['attribute_mapping'][attr]

        # update SP's attribute map
        sp.attribute_mapping = json.dumps(self.sp['config']['attribute_mapping'],
                                          indent=2)
        sp.save()

        # check if some required are unavailable...
        if req_attrs['required']:
            msg = _("{} requested unavailable attribute '{}' to this IdP. "
                            "Please contact SP technical staff for support.")
            # if some required attributes are unavailable the IdP give this warning
            for req in conv_req_attr_list:
                if req not in self.sp['config']['attribute_mapping']:
                    logger.info(msg)
                    raise UnavailableRequiredAttributes(msg.format(sp_entity_id, req))

    def set_processor(self,request=None):
        """ Instantiate user-specified processor or
            default to an all-access base processor.
            Raises an exception if the configured processor
            class can not be found or initialized.
        """
        processor_string = self.sp['config'].get('processor', None)
        if processor_string:
            try:
                self.processor = import_string(processor_string)(self.sp['id'], request=request)
                return
            except Exception as e:
                logger.error('{}'.format(e))
                msg = _("Failed to instantiate processor: {} - {}")
                logger.error(msg.format(processor_string, e),
                                        exc_info=True)
                raise ImproperlyConfigured(_(msg.format(processor_string, e),
                                                        exc_info=True))
        self.processor = BaseProcessor(self.sp['id'], request=request)

    def verify_request_signature(self, req_info):
        """ Signature verification
            for authn request signature_check is at
            saml2.sigver.SecurityContext.correctly_signed_authn_request
        """
        # TODO: Add unit tests for this
        if not req_info.signature_check(req_info.xmlstr):
            raise ValueError(_("Message signature verification failure"))

    def check_access(self, request):
        """ Check if user has access to the service of this SP
        """
        if not self.processor.has_access(request):
            raise PermissionDenied(_("You do not have access to this resource"))

    def get_authn(self, req_info=None):
        if req_info:
            req_authn_context = req_info.message.requested_authn_context
        else:
             req_authn_context = PASSWORD
        broker = AuthnBroker()
        broker.add(authn_context_class_ref(req_authn_context), "")
        return broker.get_authn_by_accr(req_authn_context)

    def get_name_id_format(self, user, authn, resp_args):
        name_id_format = resp_args.get('name_id_policy')
        self.sp['name_id_format'] = name_id_format.format \
                                    if name_id_format else NAMEID_FORMAT_PERSISTENT
        idp_name_id_format_list = self.IDP.config.getattr("name_id_format",
                                                          "idp")

        # name_id format availability
        if idp_name_id_format_list and not self.sp['name_id_format']:
            name_id_format = idp_name_id_format_list[0]

        elif self.sp['name_id_format'] and not idp_name_id_format_list:
            name_id_format = self.sp['name_id_format']

        elif self.sp['name_id_format'] not in idp_name_id_format_list:
            return self.handle_error(request,
                                     exception=_('SP requested a name_id_format '
                                                 'that is not supported in the IDP'))
        elif self.sp['name_id_format'] in idp_name_id_format_list:
            name_id_format = self.sp['name_id_format']

        else:
            name_id_format = NAMEID_FORMAT_UNSPECIFIED

        # if SP doesn't request a specific name_id_format...
        if not self.sp['name_id_format']:
            self.sp['name_id_format'] = name_id_format

        user_id = self.processor.get_user_id(user, self.sp, self.IDP.config)
        name_id = NameID(format=name_id_format,
                         sp_name_qualifier=self.sp['id'],
                         text=user_id)
        return name_id, user_id

    def get_ava(self, user=None):
        # IDENTITY AND ATTR POLICY
        # Generate request session stuff needed for user agreement screen
        attrs_to_exclude = self.sp['config'].get('user_agreement_attr_exclude', []) + \
                           getattr(settings, "SAML_IDP_USER_AGREEMENT_ATTR_EXCLUDE", [])

        identity = {
            k: v
            for k, v in self.processor.create_identity(user or self.request.user,
                                                       self.sp).items()
            if k not in attrs_to_exclude
        }

        # entity categories and other pysaml2 policies could filter out some attributes
        policy = Policy(restrictions=settings.SAML_IDP_CONFIG['service']['idp'].get('policy'))
        ava = policy.filter(identity,
                            self.sp['id'],
                            self.IDP.config.metadata,
                            required=[])
        # remove None
        for attr in ava:
            if not ava[attr]:
                ava[attr] = ''

        # END IDENTITY AND ATTR POLICY
        return identity, policy, ava

    def apply_allow_create(self, name_id):
        name_id_policy = self.resp_args['name_id_policy']
        allow_create = False
        if name_id_policy and hasattr(name_id_policy, 'allow_create'):
            name_id_policy = name_id_policy.allow_create.lower()
        # allow create support
        if settings.SAML_ALLOWCREATE and \
           name_id_policy in ['true', '1'] and \
           name_id.format == NAMEID_FORMAT_PERSISTENT:
            if not PersistentId.objects.filter(user=self.request.user,
                                               recipient_id=self.sp['id']):
                PersistentId.objects.create(user=self.request.user,
                                            persistent_id=self.processor.eduPersonTargetedID,
                                            recipient_id=self.sp['id'])
        # allow create support end

    def build_authn_response(self, user, authn, resp_args):
        """ pysaml2 server.Server.create_authn_response wrapper
        """
        name_id, user_id = self.get_name_id_format(user, authn, resp_args)

        # get identity attributes with the policy that applied filters on them
        identity, policy, ava = self.get_ava()
        self.request.session['identity'] = identity
        # talking logs
        msg = ('SSO AuthnResponse [{}] to {} [{}]: {} attrs ({}) on {} filtered by policy')
        self.request.saml_session['authn_log'] = msg.format(name_id.format,
                                                               self.sp['id'],
                                                               self.request.saml_session.get('message_id'),
                                                               len(ava),
                                                               ','.join(ava.keys()),
                                                               len(identity))
        logger.info(self.request.saml_session['authn_log'])

        self.request.session['identity'] = ava
        self.request.saml_session['subject_id'] = self.processor.eduPersonTargetedID
        #

        # apply allow_create
        self.apply_allow_create(name_id)

        # ASSERTION ENCRYPTED
        # TODO: WHY Pysaml2 do not use SP cert available in its metadata...?
        # check if the SP supports encryption
        if self.IDP.has_encrypt_cert_in_metadata(self.sp['id']):
            sp_enc_cert = self.IDP.config.metadata.certs(self.sp['id'],
                                                         "spsso", use="encryption")
            if sp_enc_cert:
                encrypt_assertion = True
            elif getattr(settings, 'SAML_FORCE_ENCRYPTED_ASSERTION', False):
                encrypt_assertion = True
            if self.sp['config'].get('disable_encrypted_assertions', False):
                encrypt_assertion = False
            # TODO: investigate here
            if encrypt_assertion:
                resp_args['encrypt_cert_assertion'] = sp_enc_cert[0]
                resp_args['encrypt_cert_advice'] = sp_enc_cert[0]
                resp_args['pefim'] = 1
        # END ENCRYPTED ASSERTION

        authn_resp = self.IDP.create_authn_response(
            authn=authn,
            identity=self.request.session['identity'],
            userid=user_id,
            name_id=name_id,

            # signature
            sign_response=self.sp['config'].get("sign_response") or \
                          self.IDP.config.getattr("sign_response", "idp") or \
                          False,
            sign_assertion=self.sp['config'].get("sign_assertion") or \
                           self.IDP.config.getattr("sign_assertion", "idp") or \
                           False,

            # default is sha1 in pySAML2
            sign_alg=self.sp['config'].get("signing_algorithm") or \
                     getattr(settings, 'SAML_AUTHN_SIGN_ALG', False),
            digest_alg=self.sp['config'].get("digest_algorithm") or \
                       getattr(settings, 'SAML_AUTHN_DIGEST_ALG', False),

            # Encryption
            encrypt_assertion=encrypt_assertion,
            encrypt_advice_attributes=encrypt_assertion,
            encrypt_assertion_self_contained=encrypt_assertion,
            **resp_args
        )
        return authn_resp

    def create_html_response(self, request, binding,
                             authn_resp, destination, relay_state):
        """ Login form for SSO
        """
        if binding == BINDING_HTTP_POST:
            context = {
                "acs_url": destination,
                "saml_response": base64.b64encode(authn_resp.encode()).decode(),
                "relay_state": relay_state,
            }
            template = "saml_post.html"
            html_response = render_to_string(template, context=context,
                                             request=request)
        else:
            http_args = self.IDP.apply_binding(
                binding=binding,
                msg_str=authn_resp,
                destination=destination,
                relay_state=relay_state,
                response=True)

            logger.debug('http args are: %s' % http_args)
            html_response = http_args['data']
        return html_response

    def render_response(self, request, html_response):
        """ Return either as redirect to MultiFactorView
            or as html with self-submitting form.
        """
        if not hasattr(self, 'processor'):
            # In case of SLO, where processor isn't relevant
            return HttpResponse(html_response)

        request.saml_session['response'] = html_response

        request.saml_session['sp_display_info'] = {
            'display_name': request.saml_session['sp_display_description'],
            'display_description': request.saml_session['sp_display_description'],
            'display_agreement_message': self.sp['config'].get('display_agreement_message'),
            'display_agreement_consent_form': self.sp['config'].get('display_agreement_consent_form')
            }
        request.saml_session['sp_entity_id'] = self.sp['id']

        # Conditions for showing user agreement screen
        user_agreement_enabled_for_sp = self.sp['config'].get('show_user_agreement_screen',
                                                              getattr(settings,
                                                                      "SAML_IDP_SHOW_USER_AGREEMENT_SCREEN"))

        agreement_for_sp = AgreementRecord.objects.filter(user=request.user,
                                                          sp_entity_id=self.sp['id']).first()
        if agreement_for_sp:
            if agreement_for_sp.is_expired() or \
               agreement_for_sp.wants_more_attrs(request.session['identity'].keys()):
                agreement_for_sp.delete()
                already_agreed = False
            else:
                already_agreed = True
        else:
            already_agreed = False

        # Multifactor goes before user agreement because might result in user not being authenticated
        if self.processor.enable_multifactor(request.user):
            logger.debug("Redirecting to process_multi_factor")
            return HttpResponseRedirect(reverse('uniauth:saml_multi_factor'))

        # If we are here, there's no multifactor. Check whether to show user agreement
        if user_agreement_enabled_for_sp and not already_agreed:
            logger.debug("Redirecting to process_user_agreement")
            return HttpResponseRedirect(reverse('uniauth:saml_user_agreement'))

        # No multifactor or user agreement
        logger.debug("Performing SAML redirect")
        return HttpResponse(html_response)


@method_decorator(require_saml_request, name='dispatch')
class LoginAuthView(LoginView):
    """ First Login Form
    """
    template_name = "saml_login.html"
    form_class = LoginForm

    #  def dispatch(self, request, *args, **kwargs):
        #  import pdb; pdb.set_trace()
        #  return super().dispatch(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):
        # """Handle GET requests: instantiate a blank version of the form."""
        # import pdb; pdb.set_trace()
        # data = self.get_context_data()
        # data['sp_logo']
        # return self.render_to_response(data)

    # def post(self, request, *args, **kwargs):
        # import pdb; pdb.set_trace()
        # return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        """If the form is invalid, returns a generic message
        status code 200 to prevent brute force attack based to response code!
        """
        return render(self.request, 'error.html',
                      {'exception_type':_("You cannot access to this service"),
                       'exception_msg':_("Your Username or Password is invalid, "
                                         "your account could be expired or been "
                                         "disabled due to many login attempts."),
                       'extra_message':_("Please access to 'Forgot your Password' "
                                         "procedure, before contact the help desk.")},
                      status=200)

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        # check issue instant
        now = timezone.localtime()
        issue_instant = now
        for tformat in settings.SAML2_DATETIME_FORMATS:
            try:
                issue_instant = timezone.datetime.strptime(self.request.saml_session['issue_instant'],
                                                           tformat)
                break
            except Exception as e:
                logger.debug('{} not parseable with {}'.format(self.request.saml_session['issue_instant'],
                                                               tformat))
        # end check
        mins = getattr(settings, 'SESSION_COOKIE_AGE', 600)
        if issue_instant < timezone.make_naive((now-datetime.timedelta(minutes=mins)),
                                               timezone.get_current_timezone()):
            return render(request, 'error.html',
                          {'exception_type': _("You take too long to authenticate!"),
                           'exception_msg': _("Your request is expired"),
                           'extra_message': _('{} minutes are passed').format(mins)},
                           status=403)
        # end check issue instant

        user = form.get_user()
        auth_login(self.request, user)

        # bind the user id to saml_session (needed for SLO and SameSite workaround)
        self.request.saml_session['_auth_user_id'] = user.pk

        if self.request.POST.get('forget_agreement'):
            # TODO: also add the sp_nameid in the query?
            agr = AgreementRecord.objects.filter(user=self.request.user)
            agr.delete()

        if self.request.POST.get('forget_login'):
            self.request.session['forget_login'] = 1

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(never_cache, name='dispatch')
@method_decorator(require_saml_request, name='dispatch')
class LoginProcessView(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """ View which processes the actual SAML request and
        returns a self-submitting form with the SAML response.
        The login_required decorator ensures the user authenticates
        first on the IdP using 'normal' ways.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info('{}: already logged in.'.format(request.user.username))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            binding = request.saml_session.get('Binding', BINDING_HTTP_POST)
            # Parse incoming request
            req_info = self.IDP.parse_authn_request(request.saml_session['SAMLRequest'],
                                                    binding)
            # do it in pysaml2
            # check SAML request signature
            #self.verify_request_signature(req_info)

            # Compile Response Arguments
            self.resp_args = self.IDP.response_args(req_info.message)
            # Set SP and Processor
            self.set_sp(self.resp_args['sp_entity_id'])
            self.set_processor(request=request)
            # Check if user has access
            self.check_access(request)
            # Construct SamlResponse message
            self.authn_resp = self.build_authn_response(request.user,
                                                        self.get_authn(),
                                                        self.resp_args)
        except KeyError as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=400)
        except ValueError as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=400)
        except (UnknownPrincipal, UnsupportedBinding) as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=400)
        except ImproperlyConfigured as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=500)
        except UnknownSystemEntity as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request,
                                     exception=excp,
                                     exception_msg=_('This SP needs attribute mappings'),
                                     status=403)
        except PermissionDenied as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=403)
        except Exception as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=500)

        html_response = self.create_html_response(
            request,
            binding=self.resp_args['binding'],
            authn_resp=self.authn_resp,
            destination=self.resp_args['destination'],
            relay_state=request.saml_session['RelayState'])

        logger.debug("SAML Authn request Response [\n{}]".format(repr_saml(self.authn_resp)))
        return self.render_response(request, html_response)


@method_decorator(never_cache, name='dispatch')
class SSOInitView(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """ View used for IDP initialized login,
        doesn't handle any SAML authn request
    """

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        passed_data = request.POST or request.GET

        try:
            # get sp information from the parameters
            self.set_sp(passed_data['sp'])
            self.set_processor(request=request)
            # Check if user has access to SP
            self.check_access(request)
        except (KeyError, ImproperlyConfigured) as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=400)
        except PermissionDenied as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=403)

        binding_out, destination = self.IDP.pick_binding(
            service="assertion_consumer_service",
            entity_id=self.sp['id'])

        # ##Adding a few things that would have been added
        # if this were SP Initiated
        passed_data['destination'] = destination
        passed_data['in_response_to'] = "IdP_Initiated_Login"
        passed_data['sp_entity_id'] = self.sp['id']

        # ##Construct SamlResponse messages
        try:
            authn_resp = self.build_authn_response(request.user,
                                                   self.get_authn(),
                                                   passed_data)
        except Exception as excp:
            logger.error('{}'.format(excp))
            return self.handle_error(request, exception=excp, status=500)

        html_response = self.create_html_response(request, binding_out,
                                                  authn_resp, destination,
                                                  passed_data['RelayState'])
        return self.render_response(request, html_response)


@method_decorator(never_cache, name='dispatch')
@method_decorator(require_saml_request, name='dispatch')
class UserAgreementScreen(ErrorHandler, LoginRequiredMixin, View):
    """This view shows the user an overview of the data being sent to the SP.
    """

    def get(self, request, *args, **kwargs):
        template = 'user_agreement.html'
        context = dict()

        ses_disp_info = request.saml_session['sp_display_info']
        try:
            # prevents KeyError at /login/process_user_agreement/: 'sp_display_info'
            context['sp_display_name'] = ses_disp_info['display_name']
            context['sp_display_description'] = ses_disp_info['display_description']
            context['sp_display_agreement_message'] = ses_disp_info.get('display_agreement_message')
            context['sp_display_agreement_consent_form'] = ses_disp_info.get('display_agreement_consent_form')
            context['attrs_passed_to_sp'] = request.session['identity']
        except Exception as excp:
            logout(request)
            logging.error('{}'.format(excp))
            msg = _not_valid_saml_msg
            return self.handle_error(request, exception=excp,
                                     extra_message=msg)

        context['form'] = AgreementForm()
        html_response = render_to_string(template, context=context,
                                         request=request)
        return HttpResponse(html_response)

    def post(self, request, *args, **kwargs):
        form = AgreementForm(request.POST)
        if not form.is_valid():
            return render(request, 'error.html',
                          {'exception_type':_("Invalid submission")},
                          status=403)

        confirm = int(form.cleaned_data['confirm'])
        dont_show_again = form.cleaned_data['dont_show_again']

        if not confirm:
            logout(request)
            return render(request, 'error.html',
                          {'exception_type':_("You cannot access to this service")},
                          status=403)

        if dont_show_again:
            record = AgreementRecord(
                user=request.user,
                sp_entity_id=request.saml_session['sp_entity_id'],
                attrs=",".join(request.session['identity'].keys())
            )
            record.save()

        saml_response_data = request.saml_session.get('response')
        if request.session.get('forget_login'):
            logout(request)
        return HttpResponse(saml_response_data)


@method_decorator(never_cache, name='dispatch')
@method_decorator(require_saml_request, name='dispatch')
class ProcessMultiFactorView(LoginRequiredMixin, View):
    """ This view is used in an optional step is to perform 'other'
        user validation, for example 2nd factor checks.
        Override this view per the documentation if using this
        functionality to plug in your custom validation logic.
    """

    def multifactor_is_valid(self, request):
        """ The code here can do whatever it needs to validate your
            user (via request.user or elsewise).
            It must return True for authentication
            to be considered a success.
        """
        return True

    def get(self, request, *args, **kwargs):
        if self.multifactor_is_valid(request):
            logger.debug('MultiFactor succeeded for %s' % request.user)

            # Check if user agreement redirect needed
            if request.saml_session.get('sp_display_info'):
                # Arbitrary value that's only set if user agreement needed.
                return HttpResponseRedirect(reverse('uniauth:saml_user_agreement'))
            return HttpResponse(request.saml_session['response'])
        logger.debug(_("MultiFactor failed; %s will not be able to log in") % request.user)
        logout(request)
        raise PermissionDenied(_("MultiFactor authentication factor failed"))


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_saml_request, name='dispatch')
class LogoutProcessView(IdPHandlerViewMixin, View):
    """ View which processes the actual SAML Single Logout request
        The login_required decorator ensures the user authenticates
        first on the IdP using 'normal' way.

        LoginRequiredMixin cannot be used here due to
        SameSite=strict prevention
    """
    __service_name = 'Single LogOut'

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    @method_decorator(store_params_in_session_func)
    def get(self, request, *args, **kwargs):
        logger.debug("{} Service".format(self.__service_name))
        # do not assign a variable that overwrite request object
        # if it will fail the return with HttpResponseBadRequest trows naturally
        # store_params_in_session(request) -> now is a decorator
        binding = request.saml_session['Binding']
        relay_state = request.saml_session['RelayState']
        logger.debug("{} requested [\n{}] to IDP".format(self.__service_name, binding))

        # adapted from pysaml2 examples/idp2/idp_uwsgi.py
        try:
            req_info = self.IDP.parse_logout_request(request.saml_session['SAMLRequest'], binding)
        except Exception as excp:
            expc_msg = "{} Bad request: {}".format(self.__service_name, excp)
            logger.error(expc_msg)
            return self.handle_error(request, exception=expc_msg, status=400)

        logger.info("{} from {} for [{}]".format(self.__service_name,
                                                 req_info.message.name_id.sp_name_qualifier,
                                                 req_info.message.name_id.text))
        logger.debug("{} SAML request [\n{}]".format(self.__service_name,
                                                     repr_saml(req_info.xmlstr, b64=False)))

        resp = self.IDP.create_logout_response(req_info.message, [binding])

        try:
            # hinfo returns request or response, it depends by request arg
            hinfo = self.IDP.apply_binding(binding, resp.__str__(),
                                           resp.destination,
                                           relay_state, response=True)
        except Exception as excp:
            logger.error("ServiceError: {}".format(excp))
            return self.handle_error(request, exception=excp, status=400)

        logger.debug("{} Response [\n{}]".format(self.__service_name,
                                                 repr_saml(resp.__str__().encode())))
        logger.debug("binding: {} destination:{} relay_state:{}".format(binding,
                                                                        resp.destination,
                                                                        relay_state))

        # logout user from IDP, this won't work in crossdomains because of SameSite
        user = get_user_model().objects.filter(pk = request.saml_session['_auth_user_id'])
        if user:
            user.first().clear_sessions()
        else:
            logger.warn('{}: logging out an unauthenticated user?'.format(self.__service_name))

        if hinfo['method'] == 'GET':
            return HttpResponseRedirect(hinfo['headers'][0][1])
        else:
            html_response = self.create_html_response(
                request,
                binding=binding,
                authn_resp=resp.__str__(),
                destination=resp.destination,
                relay_state=relay_state)
        return self.render_response(request, html_response)


@never_cache
def get_metadata(request):
    if hasattr(settings, "SAML_IDP_MULTIFACTOR_VIEW"):
        multifactor_class = import_string(getattr(settings,
                                                  "SAML_IDP_MULTIFACTOR_VIEW"))
    else:
        multifactor_class = ProcessMultiFactorView
    return multifactor_class.as_view()(request)


@never_cache
def metadata(request):
    """ Returns an XML with the SAML 2.0 metadata for this Idp.
        The metadata is constructed on-the-fly based on the
        config dict in the django settings.
    """
    conf = IdPConfig()
    conf.load(copy.deepcopy(settings.SAML_IDP_CONFIG))
    metadata = entity_descriptor(conf)

    # removed ...
    # metadata.extensions = None

    return HttpResponse(content=text_type(metadata).encode('utf-8'),
                        content_type="text/xml; charset=utf8")


def test500(request):
    # this avoid conflicts with unit tests
    if not hasattr(request, 'META'):
        return HttpResponse(status=500)
    raise Exception()
