Attribute releases
^^^^^^^^^^^^^^^^^^

Every SP can use a specific Attribute Processor, you can even customize a brand new one in an application that can be easily installed into ``django_idp.settings.INSTALLED_APPS``.
You can see how these ``processors`` works simply looking at ``uniauth.processors`` and ``idp.processors``.

There also a special class named ``NameIdBuilder``, the nameID policy relies on it, it should be very easy to inherit and customize as needed.

In every ``processors`` there's a special method called ``extra_attr_processing`` where to put additional conditions and values processing. See ``idp.processors.LdapUnicalAcademiaProcessor`` for an example of inheritance with the use of this method.


.. thumbnail:: agreement.png

  The AttributeProcessors apply all the policies and the filters to attributes, the user will see in the agreement screen the preview of the passing attributes. This screen can be highly customized directly via ServiceProvider configuration screen.
