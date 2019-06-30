# Django uniAuth

Django Unified Authentication System is an IDentity Provider built on top of [IdentityPython](https://idpy.org) stack.
Used in Research & Scholarship context, in Università della Calabria.

This Release Candidate supports a SAML2 IDP, an OIDC Provider will be available in the next release.

## Why?

Many SAML2 IDP OpenSource softwares come as mature, I used them and also appreciate them.
However I didn't understand why there come always the need to have high sysadmin skills to work with them, data definitions still need to be
stored and handled in multiple files and in a way that, I think, there's too much management costs in time, with repetitive and boring actions handled via console. In addition to this the learning curve related to SAML2 implementations proves itself very slow,  often many users preferred to get out of all this.

> I found a lot of python projects developed from scratch and I thought that a Django implementation of them would be a better solution.

As a long date Python Programmer I was also looking for something more hacky to me.
I put some contributions in [djangosaml2idp](https://github.com/OTA-Insight/djangosaml2idp) and I was not the only one (thank you @askvortsov1).
Soon these contributions became a distinct fork, so uniAuth was born as a djangosaml2idp fork, because that project won't need some of the features that we found today in uniAuth and that I also needed in reasonable time.

> Why these great softwares still doesn't have a human management UI and other helpers tools was another of my questions. 

uniAuth wants to bring the IDentity management to smart users without give up smartness.
Probably you noticed that uniAuth not come as a Django app but as an entire project, this is because we want to offer a ready-to-use software and not a software too much linked to programming skills of users.

This is only our first shot, hopefully we'll do even better in the time, never give up.


## Features

uniAuth, as a SAML2 IDP, supports HTTP-REDIRECT and POST bindings, AuthnRequest with ForceAuthn but not AllowCreate NameIDPolicy, it simply ignore AllowCreate. Features set are:

- All already availables in [pysaml2](https://github.com/IdentityPython/pysaml2);
- Full Internazionalization support (i18n);
- Interactive Metadata Store definitions through the Admin Backend UI;
- Interactive ServiceProvider Federation through the Admin Backend UI;
- Customizable Template and style based on [AGID guidelines](https://www.agid.gov.it/it/argomenti/linee-guida-design-pa);
- MetadataStore and SP validations on save, to prevent faulty configurations in production environment;
- Optional and quite granular Agreement Screen;
- Many options definable for every SP, like:
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


## Documentation 

*readthedocs is coming*...


#### Requirements and enviroment

````
sudo apt install xmlsec1 mariadb-server libmariadbclient-dev python3-dev python3-pip libssl-dev libmariadb-dev-compat
pip3 install virtualenv
virtualenv -ppython3 uniauth.env
source uniauth.env/bin/activate
````

#### Get uniauth and install dependencies
````
git clone https://github.com/UniversitaDellaCalabria/uniAuth.git 
cd uniAuth
pip3 install -r requirements

```` 

#### Configure the software
````
cd django_idp

# copy and modify as your needs
cp settingslocal.py.example settingslocal.py

# copy and modify SAML2 IDP paramenters
cp idp_pysaml2.py.example idp_pysaml2.py
````

> You can use metadata and SP definitions in `idp_pysaml2.py` for pysaml2 compatibility otherwise you can create and manage them via Django Admin backend.

#### Create Database
````
# create your MysqlDB
export USER='that-user'
export PASS='that-password'
export HOST='%'
export DB='uniauth'

# tested on Debian 10
sudo mysql -u root -e "\
CREATE USER IF NOT EXISTS '${USER}'@'${HOST}' IDENTIFIED BY '${PASS}';\
CREATE DATABASE IF NOT EXISTS ${DB} CHARACTER SET = 'utf8' COLLATE = 'utf8_general_ci';\
GRANT ALL PRIVILEGES ON ${DB}.* TO '${USER}'@'${HOST}';"
````

#### LDAP or not?
Link to a LDAP if needed, multiple database support is also available as Django feature.
If you do not need a LDAP data source please remove `ldap_peoples` from `uniauth.settings.INSTALLED_APPS`.
If you need a fully compliant LDAP configuration with `ldap_peoples` configuration please try the [dedicated playbook]() for it.
See readthedocs documentation for have an idea for multiple LDAP data sources.


#### Create your own SAML certificates
Then copy them to `certificates` folder and define them in idp_pysaml2.py (`key_file` and `cert_file`, even in `encryption_keypairs`).
````
openssl req -nodes -new -x509 -days 3650 -keyout private.key -out public.cert -subj '/CN=your.own.fqdn.com'
````


#### Create schemas and superuser
````
./manage.py migrate
./manage.py createsuperuser
````

#### Run
````
./manage.py runserver
````

...need a SP for a preliminar tests?
see djangosaml2_sp here: https://github.com/peppelinux/Django-Identity


## Production Environment
See `uwsgi_setup` examples.


## Contribute

Feel free to contribute creating separate PR from dedicated brancheds for each feature.
Open an Issue if you want to talk before develop to reduce the risk to be unmerged for some latest reason.
All the things will be collected in a new roadmap to the next release candidate.

Still need to handle Continuous Integration with unit test.

## Author

Giuseppe De Marco





