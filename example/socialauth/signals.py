import logging

from django.dispatch import receiver


logger = logging.getLogger(__name__)


def update_principal_email_if_none(sender, instance, created, **kwargs):
    if not instance.user.email and instance.primary and instance.verified:
        instance.user.email = instance.email
        instance.user.save()
        logger.info(
            f"{instance.user} principal email updated in the user profile"
        )
        
        
