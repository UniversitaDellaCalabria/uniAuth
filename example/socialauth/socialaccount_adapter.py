import logging


from allauth.account.models import EmailAddress
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


from django.contrib.auth import get_user_model, login
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

logger = logging.getLogger("socialauth")


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse

        Why both an adapter hook and the signal? Intervening in
        e.g. the flow from within a signal handler is bad -- multiple
        handlers may be active and are executed in undetermined order.
        """
        acclink = EmailAddress.objects.filter(
            email__in = [i.email for i in sociallogin.email_addresses],
            verified = True
        ).first()
        if not acclink or not acclink.user.is_active:
            logger.warning(
                f"Any of the sociallogin.email_addresses {sociallogin.email_addresses} "
                "have been found in the preconfigured social login Email Addresses"
            )
            raise ImmediateHttpResponse(
                render(
                    request,
                    "socialaccount/account_linking_failed.html",
                )
            )
        else:
            login(
                request, 
                acclink.user, 
                backend="django.contrib.auth.backends.ModelBackend"
            )
            logger.info(
                f"{acclink.user} authenticated via sociallogin {sociallogin.account.provider}"
            )
            
            # required for SAML2 SLO
            request.saml_session["_auth_user_id"] = acclink.user.pk
            acclink.user.origin = f"Social login: {sociallogin.account.provider}"
            acclink.user.save()
            
            raise ImmediateHttpResponse(
                HttpResponseRedirect(
                    reverse("uniauth_saml2_idp:saml_login_process")
                )
            )
        
        
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        raise Exception("User creation with social login is not enabled.")
