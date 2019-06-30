Requirements and enviroment
^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    sudo apt install xmlsec1 mariadb-server libmariadbclient-dev python3-dev python3-pip libssl-dev libmariadb-dev-compat
    pip3 install virtualenv
    virtualenv -ppython3 uniauth.env
    source uniauth.env/bin/activate

Get uniauth and install dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    git clone https://github.com/UniversitaDellaCalabria/uniAuth.git 
    cd uniAuth
    pip3 install -r requirements

Configure the software
^^^^^^^^^^^^^^^^^^^^^^

::

    cd django_idp

    # copy and modify as your needs
    cp settingslocal.py.example settingslocal.py

    # copy and modify SAML2 IDP paramenters
    cp idp_pysaml2.py.example idp_pysaml2.py

    You can use metadata and SP definitions in ``idp_pysaml2.py`` for
    pysaml2 compatibility otherwise you can create and manage them via
    Django Admin backend.

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

LDAP or not?
^^^^^^^^^^^^

Link to a LDAP if needed, multiple database support is also available as
Django feature. If you do not need a LDAP data source please remove
``ldap_peoples`` from ``uniauth.settings.INSTALLED_APPS``. If you need a
fully compliant LDAP configuration with ``ldap_peoples`` please try the
`dedicated playbook <https://github.com/peppelinux/ansible-slapd-eduperson2016>`__ for it.

See readthedocs documentation for have an idea for multiple LDAP data
sources.

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

Production Environment
^^^^^^^^^^^^^^^^^^^^^^

See `uwsgi_setup` examples.
