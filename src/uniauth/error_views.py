import logging

from django.views.generic import TemplateView


logger = logging.getLogger(__name__)


class SamlIDPErrorView(TemplateView):
    """ Default error view when a 'known' error
        occurs in the saml2 authentication views.
    """
    template_name = 'error.html'
    status = 403
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exception = kwargs.get("exception")

        context.update({
            "exception_type": exception.__class__.__name__ if exception else None,
            "exception_msg": str(exception) if exception else None,
            "extra_message": kwargs.get("extra_message"),
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status
        return super(TemplateView, self).render_to_response(context, **response_kwargs)
