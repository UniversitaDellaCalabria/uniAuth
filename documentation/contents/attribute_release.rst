Attribute releases
^^^^^^^^^^^^^^^^^^

Every SP can use a specific Attribute Processor, you can even customize a brand new one in a application that can be easily installed into ``django_idp.settings.INSTALLED_APPS``.
You can see how these ``processors`` works simply looking at ``uniauth.processors`` and ``idp.processors``.

You'll can see that there also a special class named ``NameIdBuilder``, the nameID policy relies on it, I hope to made it very easy to inherit and customize as needed.

In every ``processors`` I created a special method called ``extra_attr_processing`` where to put additional conditions and values processing. See ``idp.processors.LdapUnicalAcademiaProcessor`` for an example of inheritance with the use of this method.


.. figure:: agreement.png

  The AttributeProcessors apply all the policy and the filters to attributes, the user will see in the agreement screen the preview of the passing attributes.
