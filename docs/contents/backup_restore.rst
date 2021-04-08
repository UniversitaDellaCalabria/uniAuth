Backup
^^^^^^

We can export all the MetadataStores, the federated ServiceProviders and user's Agreements in JSON format as follow:

::

    ./manage.py dumpdata uniauth_saml2_idp
    # to a file
    ./manage.py dumpdata uniauth_saml2_idp > /path/to/file.json


If we had some users with legacy SAML persistent ID stored in our ``USER_MODEL`` we can also backup these with the following command:

::

    ./manage.py dumpdata accounts


Restore
^^^^^^^

To restore these backups just run this:

::

    ./manage.py loaddata /path/to/file.json
