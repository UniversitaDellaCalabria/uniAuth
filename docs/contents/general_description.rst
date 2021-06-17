General Description
^^^^^^^^^^^^^^^^^^^

uniAuth, as a SAML2 IDP, is based on `pysaml2 <https://github.com/IdentityPython/pysaml2>`__ and it supports:

- HTTP-REDIRECT and POST bindings (signed authn request must be in HTTP-POST binding);
- ForceAuthn;
- SLO, SAML Single Logout;
- Signed and Encrypted assertions in Response;
- AllowCreate, nameid is stored if nameid format is persistent.


Implementation specific Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- no restart is needed when add a new metadata or Service Provider Definition;
- Full Internazionalization support (i18n);
- Interactive Metadata Store definitions through the Admin Backend UI;
- Interactive ServiceProvider definition through the Admin Backend UI;
- Customizable Template and style based on [AGID guidelines](https://www.agid.gov.it/it/argomenti/linee-guida-design-pa);
- MetadataStore and SP validations on save, to prevent faulty configurations in production environment;
- Configurable digest algorithm and salt for Computed NameID;
- Many configurable options, for every SP we can decide:
    - enable/disable explicitally;
    - signature and digest algorithms;
    - attributes release (force a set or release what requested by sp);
    - attribute rewrite and creation, fully configurable AttributeProcessors per SP, every aspect of attribute release can be customized from scratch;
    - agreement screen message, availability, data consent form.
- Configurable log rotation through uwsgi;
- Importable StoredPersistentID for each user, from migrations from another IDP;
- An optional LDAP web manager with a configurable app (`ldap_peoples`) through `django-ldap-academia-ou-manager <https://github.com/peppelinux/django-ldap-academia-ou-manager>`__;
- Multiple LDAP sources through `pyMultiLDAP <https://github.com/peppelinux/pyMultiLDAP>`__;
- Detailed logs.
