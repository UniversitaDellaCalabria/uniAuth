from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _


class LoginForm(AuthenticationForm):
    # these are inherited
    # username = forms.CharField()
    # password = forms.CharField(widget=forms.PasswordInput())
    forget_agreement = forms.BooleanField(label=_("Cancella precedente "
                                                  "consenso ai dati"),
                                          required=False)
    forget_login = forms.BooleanField(label=_("Non ricordare l'accesso"),
                                      required=False)

class AgreementForm(forms.Form):
    CHOICES = ((1, _('Do il mio consenso')),
               (0, _('Nego il mio consenso')))

    confirm = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    dont_show_again = forms.BooleanField(label=_("Non presentare questa schermata "
                                                 "la prossima volta che "
                                                 "effettuerò l'accesso"),
                                         required=False)
