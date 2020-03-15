MDQuery
^^^^^^

This command permit us to check the availability of a saml entity in the IdP metadata store.
The option `-f` can specify the output format, if saml2 (default) or json.

::

    ./manage.py mdquery -e https://auth.unical.it/idp/metadata/ 


AACli
^^^^^


This feature will let us check wich attributes will be released to a specified user id.

::

    ./manage.py aacli -u joe -e https://sptest.auth.unical.it/saml2
