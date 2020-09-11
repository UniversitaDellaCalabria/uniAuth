Requirements and enviroment
^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    sudo apt install xmlsec1 mariadb-server libmariadbclient-dev python3-dev python3-pip libssl-dev libmariadb-dev-compat libsasl2-dev libldap2-dev

    pip3 install virtualenv
    virtualenv -ppython3 uniauth.env
    source uniauth.env/bin/activate

Get uniauth and install dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    git clone https://github.com/UniversitaDellaCalabria/uniAuth.git
    cd uniAuth
    pip3 install -r requirements.txt

Configure the software
^^^^^^^^^^^^^^^^^^^^^^

::

    cd django_idp

    # copy and modify as your needs
    cp settingslocal.py.example settingslocal.py

    # copy and modify SAML2 IDP paramenters
    cp idp_pysaml2.py.example idp_pysaml2.py


djangosaml2 parameters:

SAML_IDP_DJANGO_USERNAME_FIELD = 'uid'
    Attribute used for SAML nameid. It must be a field name, a @property or a callable of the Django User model.

SAML_COMPUTEDID_HASHALG = 'sha1'
    Global behaviour, which algorithm should be used to produce the computedID of a user.
    Used only for OPAQUE, TRANSIENT and PERSISTENT nameid format.

SAML_COMPUTEDID_SALT = b'87sdf+ybDS+FDSFsdf__7yb'
    Salt used to produce the computed id. Use ``b''`` to disable salt.
    Used only for TRANSIENT and PERSISTENT nameid format.

SAML_ALLOWCREATE = True
    If enabled and nameid format is persistent the nameid related to user:recipient_id will be stored in PersistentId model

Platform specific parameters, each of these can be overriden in ServiceProvider configurations:

SAML_IDP_SHOW_USER_AGREEMENT_SCREEN = True
    Global behaviour, show or not the agreement screen.

SAML_IDP_SHOW_CONSENT_FORM = False
    Global behaviour, show or not the form for the consent to transmit the attributes.

SAML_IDP_USER_AGREEMENT_ATTR_EXCLUDE = []
    Global behaviour, if for some reason some attribute should be hidden in the agreement screen (discouraged!).

SAML_IDP_USER_AGREEMENT_VALID_FOR = 24 * 365
    User agreements will be valid for 1 year unless overriden. If this attribute is not used, user agreements will not expire.

SAML_AUTHN_SIGN_ALG or SAML_AUTHN_DIGEST_ALG
    Global behaviour, which algorithms should be used for SAML signature and digest.

SAML_FORCE_ENCRYPTED_ASSERTION = False
    It will only release encryoted assertion, default = False. SP without encryption key will not works with this configuration.

SAML_DISALLOW_UNDEFINED_SP = True
    Only configured SP are allowed to do Authentication requests.
    If ``False`` all the SP available in the MetadataStore can request an authentication.

DEFAULT_SPCONFIG = {
    Default configuration that will be preloaded on every ServiceProvider configurations.
    Put here your favourite Attribute Processor or choose another one, from one of your custom application.
    See examples.

To configure new Metadata stores and federate new Service Providers
you can use metadata and SP definitions in ``idp_pysaml2.py`` for
pysaml2 compatibility, otherwise you can create and manage them via
Django Admin backend. See dedicated sections for examples.


Create Database
^^^^^^^^^^^^^^^

::

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

LDAP connection
^^^^^^^^^^^^^^^

You can use LDAP data source with at least two strategy ``ldap_peoples`` ldap manager or ``pyMultiLDAP``.
If you do not need a LDAP data source remove ``ldap_peoples`` or ``multildap`` from ``uniauth.settingslocal.INSTALLED_APPS``.

``ldap_peoples`` is a fancy app to integrate a R&S LDAP manager.
On top of it you'll find a custom authentication backend and a custom attribute processor,
you can even write your custom auth backend and processor with your preferred LDAP library.
If you need a fully compliant LDAP configuration with ``ldap_peoples`` please try the
`dedicated playbook <https://github.com/peppelinux/ansible-slapd-eduperson2016>`__ for it.

If you need multiple LDAP data sources following ``ldap_peoples`` approach
you'll have to create your own django application and use types and methods found in ``ldap_peoples``.

If you do not want to create other django application or develop other things to manage multiple LDAP sources,
you can use `pyMultiLDAP <https://github.com/peppelinux/pyMultiLDAP>`__ as a  proxy, through slapd-sock, or as a python LDAP Client.
See `settingslocal.py.example` to have some usage examples.

Create your own SAML certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Then copy them to ``certificates`` folder and define them in
idp\_pysaml2.py (``key_file`` and ``cert_file``, even in
``encryption_keypairs``).

::

    openssl req -nodes -new -x509 -days 3650 -keyout private.key -out public.cert -subj '/CN=your.own.fqdn.com'

Create schemas and superuser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    ./manage.py migrate
    ./manage.py createsuperuser

Run
^^^

::

    ./manage.py runserver

...need a SP for a preliminar tests? see djangosaml2\_sp here:
https://github.com/peppelinux/Django-Identity

Admin ui could be configured in `settingslocal.py`, with the variable `ADMIN_PATH`.
If it is not defined, default will be `admin/`

Production Environment
^^^^^^^^^^^^^^^^^^^^^^

See `uwsgi_setup` examples.

Remember to run ``collectstatic`` to copy all the static files in the production static folder:


::

    ./manage.py collectstatic


If you need more debug control with the same production configuration, using uwsgi you could run the following commands (absolute paths as examples):


::


    /etc/init.d/unicalauth stop
    uwsgi --ini /opt/unicalauth/uwsgi_setup/uwsgi.ini.debug
