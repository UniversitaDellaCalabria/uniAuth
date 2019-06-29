# Django uniAuth

Django Unified Authentication System is an IDentity Provider built on top of [IdentityPython](https://idpy.org) stack.

At this moment it only supports SAML2, soon as possibile also OIDC will be implemented.

#### Features

- All already availables in [pysaml2](https://github.com/IdentityPython/pysaml2);
- Full Internazionalization support (i18n);
- Customizable Template based on [AGID guidelines](https://www.agid.gov.it/it/argomenti/linee-guida-design-pa);
- Interactive Metadata Store definitions through the Admin Backend UI;
- Interactive ServiceProvider Federation through the Admin Backend UI;
- Metadata and SP validations on save, to prevent faulty configurations in production environment;
- Optional and quite granular Agreement Screen;
- Different options, signature and digest algorithms, attributes release and other behaviour per SP;
- Configurable log rotation through uwsgi;
- Importable legacy stored StoredPersistentID per user;
- Fully configurable AttributeProcessors per SP, every aspect of attribute release can be customized from schratch;
- Detailed but not huge logs.

#### Documentation 

readthedocs is coming...


Requirements and enviroment
````

````

Create Database
````

````

Link to a LDAP if needed, multiple database support is also available as Django feature.
````

````

Create schemas and superuser
````
./manage.py migrate
./manage.py createsuperuser
````

Run
````
./manage.py runserver
````

...need a SP for preliminar tests?
see djangosaml2_sp here: https://github.com/peppelinux/Django-Identity


#### Author
Giuseppe De Marco




