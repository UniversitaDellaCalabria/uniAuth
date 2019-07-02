General Description
^^^^^^^^^^^^^^^^^^^

uniAuth, as a SAML2 IDP, is based on `pysaml2 <https://github.com/IdentityPython/pysaml2>`__ and it supports:

- HTTP-REDIRECT and POST bindings;
- AuthnRequest with or without ForceAuthn;
- SLO, SAML Single Logout;
- Encrypted assertions, customizable sign/digest algorithms and, in general, it presents a good posture in terms of security regarding SAML standards.

uniAuth do not support AllowCreate NameIDPolicy, this behaviour is completely demanded to uniAuth AttributeProcessors.

Implementation specific Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Full Internazionalization support (i18n);
- Interactive Metadata Store definitions through the Admin Backend UI;
- MetadataStore supports local file (upload), local folder, remote url and MDQ service;
- Interactive ServiceProvider Federation through the Admin Backend UI;
- Customizable Template and style based on `AGID guidelines <https://www.agid.gov.it/it/argomenti/linee-guida-design-pa>`__;
- MetadataStore and SP validations on save, to prevent faulty configurations in production environment;
- Optional and quite granular Agreement Screen;
- Many configurable options, for every SP we can decide:
    - signature and digest algorithms;
    - attributes release policies;
    - attribute rewrite and creation, fully configurable AttributeProcessors per SP, every aspect of attribute release can be customized from schratch;
    - selectable hashing algorithm for Computed NameID;
    - agreement screen message, availability, data consent form.
- Configurable log rotation through uwsgi;
- Importable StoredPersistentID for each user, for migrations from other IDP;
- An LDAP web manager with a configurable app (`ldap_peoples`);
- Multifactor support, as available in djangosaml2idp;
- Detailed but not huge logs.
