from allauth.account.adapter import DefaultAccountAdapter

from django.contrib.auth import get_user_model


class CustomAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse

        (Comment reproduced from the overridden method.)
        """
        # allauth workaround
        # faccio finta che il signup vada avanti eppoi filtro in seguito in .save_user()
        return False

    def clean_email(self, email):
        """
        Validates an email value. You can hook into this if you want to
        (dynamically) restrict what email addresses can be chosen.
        """
        # RestrictedList = ['Your restricted list goes here.']
        # if email in RestrictedList
            # raise ValidationError('You are restricted from registering. Please contact admin.')
        return email
