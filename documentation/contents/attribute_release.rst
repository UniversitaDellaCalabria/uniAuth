Attribute releases
^^^^^^^^^^^^^^^^^^

Every SP can use a specific Attribute Processor, you can even customize a brand new one in an application that can be easily installed into ``django_idp.settingslocal.INSTALLED_APPS``.
You can see how these ``processors`` works simply looking at ``uniauth.processors`` and ``idp.processors``.

There also a special class named ``NameIdBuilder``, the nameID policy relies on it, it should be very easy to inherit and customize as needed.

In every ``processors`` there's a special method called ``extra_attr_processing`` where to put additional conditions and values processing. See ``idp.processors.LdapUnicalAcademiaProcessor`` for an example of inheritance with the use of this method.


.. thumbnail:: agreement.png

  The AttributeProcessors apply all the policies and the filters to attributes, the user will see in the agreement screen the preview of the passing attributes. This screen can be highly customized directly via ServiceProvider configuration screen.


Entity Categories
^^^^^^^^^^^^^^^^^

Entity Categories is handled as it come from pySAML2.
In the `django_idp.idp_pysaml2` we can define ``entity_category_support`` or ``entity_category`` as follow


::


    SAML_IDP_CONFIG = {
        'debug' : True,
        'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
        'entityid': '%s/metadata' % BASE_URL,
        'attribute_map_dir': 'data/attribute-maps',
        'description': 'SAML2 IDP',

        'entity_category': [edugain.COCO, # "http://www.geant.net/uri/dataprotection-code-of-conduct/v1"
                            refeds.RESEARCH_AND_SCHOLARSHIP],

        'service': {


The previous configuration will expose Entity Categories in the IDP metadata.
If we need also to handle these as policy, to manage these as restrictions on attribute release, we
could define them in ``SAML_IDP_CONFIG['service']['idp']['policy']``


::


            "policy": {
                "default": {
                    "lifetime": {"minutes": 15},
                    "name_form": NAME_FORMAT_URI,
                    # if the sp are not conform to entity_categories (in our metadata)
                    # the attributes will not be released
                    # "entity_categories": ["refeds",],
                },

                # attributes will be released only if this SP have
                # edugain entity_category definition in its metadata.
                "https://sp1.testunical.it/saml2/metadata/": {
                    "entity_categories": ["edugain"]
                }

            }

Name ID Format
^^^^^^^^^^^^^^

This uniAuth release only supports these Name ID formats:

- NAMEID_FORMAT_UNSPECIFIED
- NAMEID_FORMAT_TRANSIENT
- NAMEID_FORMAT_PERSISTENT
- NAMEID_FORMAT_EMAILADDRESS

See ``uniauth.processors.NameIdBuilder`` if you need to implement other formats, it's trivial.
