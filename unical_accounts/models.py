import pycountry

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class User(AbstractUser):
    GENDER= (
                ( 'male', _('Maschio')),
                ( 'female', _('Femmina')),
                ( 'other', _('Altro')),
            )

    first_name = models.CharField(_('Name'), max_length=30,
                                  blank=True, null=True)
    last_name = models.CharField(_('Surname'), max_length=30,
                                 blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    email = models.EmailField('email address', blank=True, null=True)
    taxpayer_id = models.CharField(_('Taxpayer\'s identification number'),
                                      max_length=32,
                                      blank=True, null=True)
    gender    = models.CharField(_('Genere'), choices=GENDER,
                                 max_length=12, blank=True, null=True)
    place_of_birth = models.CharField('Luogo di nascita', max_length=30,
                                      blank=True, null=True,
                                      choices=[(i.name, i.name) for i in pycountry.countries])
    birth_date = models.DateField('Data di nascita',
                                  null=True, blank=True)
    persistent_id = models.CharField(_('SAML Persistent Stored ID'),
                                     max_length=30,
                                     blank=True, null=True)

    # short_description = models.CharField(_('Descrizione breve'), max_length=33, blank=True, null=True)
    # bio = models.TextField('Biografia, note', max_length=2048, blank=True, null=True)
    # avatar  = models.ImageField('Avatar, foto', upload_to='avatars/', null=True, blank=True)
    # webpage_url = models.CharField(_('Pagina web'), max_length=512, blank=True, null=True)

    class Meta:
        ordering = ['username']
        verbose_name_plural = _("Users")

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)
