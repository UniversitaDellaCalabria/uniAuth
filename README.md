# Django uniAuth

![CI build](https://travis-ci.org/UniversitaDellaCalabria/uniAuth.svg?branch=master)
![pypi](https://img.shields.io/pypi/v/uniauth-saml2-idp.svg)
![Python version](https://img.shields.io/badge/license-Apache%202-blue.svg)
![Documentation Status](https://readthedocs.org/projects/uniauth/badge/?version=latest)
![License](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)

**uniauth-saml2-idp** is an SAML2 *IDentity Provider* built on top of [Pysaml2](https://idpy.org) and Django.
It was born as a fork of [djangosaml2idp](https://github.com/OTA-Insight/djangosaml2idp/) project of which very little has by now remained.

Consult the [Official Documentation at readthedocs](https://uniauth.readthedocs.io/) for usage specifications and advanced topics.

![Alt text](docs/contents/login.png)

## SAML2 Features

- HTTP-REDIRECT and POST bindings (signed authn request must be in HTTP-POST binding);
- ForceAuthn;
- SLO, SAML Single Logout;
- Signed and Encrypted assertions;
- AllowCreate, nameid is stored with a persistent nameid format.

## Implementation specific Features

- no restart is needed on new matadata store or SP registration;
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
- Configurable log rotation through uwsgi and python logging;
- Importable StoredPersistentID for each user, from migrations from another IDP;
- An optional LDAP web manager with a configurable app (`ldap_peoples`) through `django-ldap-academia-ou-manager <https://github.com/peppelinux/django-ldap-academia-ou-manager>`__;
- _Multiple LDAP_ sources through [pyMultiLDAP](https://github.com/peppelinux/pyMultiLDAP);
- _Multifactor Authentication_ support, as originally available in djangosaml2idp;
- _aacli_ and _mdquery_ management command (yes, inspired by Shibboleth IdP);
- Detailed logs.


## Examples

uniAuth permit to add new metadata and register new Service Providers directly from the Admin backend interface, via Web.
See [Official Documentation at readthedocs](https://uniauth.readthedocs.io/) for usage specifications and advanced topics.

---

![Alt text](docs/contents/md_search.png)
![Alt text](docs/contents/mdstore.png)
*Every Metadata store, during creation or update, will be validated to avoid faulty configurations in production environment.*

---

![Alt text](docs/contents/sp_search.png)
![Alt text](docs/contents/sp.png)
*Create a new SP. If `SAML_DISALLOW_UNDEFINED_SP` is True this configuration is mandatory, otherwise only the sp metadata is needed, the SP configuration will be created automatically using a default configuration.*

## Tests

````
pip install -r requirements-dev.txt
pytest tests/ -x --pdb
````

code coverage
````
coverage erase
coverage run -m pytest tests/
coverage report -m
````

A test LDAP server is available in `tests/ldapd.py`.
You can run it manually and test a query with `ldapsearch`.
Unit test will run `ldapd.py` automatically.

```
python3 tests/ldapd.py

ldapsearch -H ldap://localhost:3899 -b "dc=testunical,dc=it" -x uid=mario

# auth bind
ldapsearch -H ldap://localhost:3899 -b "dc=testunical,dc=it" uid=mario -D "uid=mario,ou=people,dc=testunical,dc=it" -w cimpa12
```

## Contribute

Feel free to contribute creating separate PR from dedicated branches for each feature.
Please open an Issue if you want to talk before develop, to reduce the risk to be not merged for some reason.
