MDQuery
^^^^^^^

This command permit us to check the availability of a saml entity in the IdP metadata store.
The option `-f` can specify the output format, if saml2 (default) or json.
It will print the entity metadata in the console.

::

    ./manage.py mdquery -e "http://sp1.testunical.it:8000/saml2/metadata/"
    ./manage.py mdquery -e "http://sp1.testunical.it:8000/saml2/metadata/" -f json


AACli
^^^^^


This feature will let us check wich attributes will be released to a specified Service Provider regarding a specified user.

::

    ./manage.py aacli -u joe -e https://sptest.auth.unical.it/saml2


example output::

    SP Configuration:
    {
      "processor": "uniauth_saml2_idp.processors.ldap.LdapUnicalMultiAcademiaProcessor",
      "attribute_mapping": {
        "cn": "cn",
        "codice_fiscale": "codice_fiscale",
        "displayName": "displayName",
        "eduPersonAffiliation": "eduPersonAffiliation",
        "eduPersonEntitlement": "eduPersonEntitlement",
        "eduPersonHomeOrganization": "eduPersonHomeOrganization",
        "eduPersonPrincipalName": "eduPersonPrincipalName",
        "eduPersonScopedAffiliation": "eduPersonScopedAffiliation",
        "eduPersonTargetedID": "eduPersonTargetedID",
        "email": [
          "mail",
          "email"
        ],
        "givenName": [
          "givenName",
          "another_possible_occourrence"
        ],
        "mail": [
          "mail",
          "email"
        ],
        "matricola_dipendente": "matricola_dipendente",
        "matricola_studente": "matricola_studente",
        "schacHomeOrganization": "schacHomeOrganization",
        "schacPersonalUniqueCode": "schacPersonalUniqueCode",
        "schacPersonalUniqueID": "schacPersonalUniqueID",
        "sn": "sn"
      },
      "force_attribute_release": false,
      "display_name": "http://sp1.testunical.it:8000/saml2/metadata/",
      "display_description": "",
      "display_agreement_message": "",
      "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
      "digest_algorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
      "disable_encrypted_assertions": true,
      "show_user_agreement_screen": true,
      "display_agreement_consent_form": false
    }

    TargetedID: 4b7dc8cc66796e63702f7baa73588f772191254801ab9369b7dfa883dbccad58
    {
      "cn": [
        "mario rossi"
      ],
      "eduPersonEntitlement": [
        "urn:mace:terena.org:tcs:personal-user",
        "urn:mace:terena.org:tcs:escience-user",
        "urn:mace:dir:entitlement:common-lib-terms"
      ],
      "eduPersonPrincipalName": [
        "mario@testunical.it"
      ],
      "eduPersonScopedAffiliation": [
        "staff@testunical.it",
        "member@testunical.it",
        "member@altrodominio.it"
      ],
      "email": [
        "mario.rossi@testunical.it"
      ],
      "givenName": [
        "mario"
      ],
      "mail": [
        "mario.rossi@testunical.it"
      ],
      "schacHomeOrganization": [
        "testunical.it"
      ],
      "schacPersonalUniqueCode": [
        "urn:schac:personalUniqueCode:it:testunical.it:dipendente:1237403",
        "urn:schac:personalUniqueCode:it:testunical.it:studente:1234er"
      ],
      "schacPersonalUniqueID": [
        "urn:schac:personalUniqueID:it:CF:CODICEFISCALEmario"
      ],
      "sn": [
        "rossi"
      ],
      "codice_fiscale": "CODICEFISCALEmario"
    }
