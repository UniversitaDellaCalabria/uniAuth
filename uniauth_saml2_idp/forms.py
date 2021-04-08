from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    # these are inherited
    # username = forms.CharField()
    # password = forms.CharField(widget=forms.PasswordInput())
    forget_agreement = forms.BooleanField(label=_("Delete previous agreement"),
                                          required=False,
                                          localize=True)
    forget_login = forms.BooleanField(label=_("Forget access"),
                                      required=False,
                                      localize=True)


class AgreementForm(forms.Form):
    CHOICES = ((1, _('I give my consent')),
               (0, _('I deny my consent')))

    confirm = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    dont_show_again = forms.BooleanField(label=_("Don't show this screen "
                                                 "on next login."),
                                         required=False,
                                         localize=True)
