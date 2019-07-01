Customize uniAuth
^^^^^^^^^^^^^^^^^

In the projects tree there's an application called `idp`, in it we configured the customization of some AttributeProcessors, and AuthenticationBackend based on LDAP and the template to use.
Use it as an example to to your customization, you can even put there another Authentication backend and your customized Attribute Processors.

Remember also to put it in django_idp.settings.INSTALLED_APPS and in case of a custom Autherntication Backend, to configure it also in django_idp.settings.AUTHENTICATION_BACKENDS.

.. figure:: custom_app.png

  This is the structure of `idp`
