#!/bin/bash

autopep8 -r --in-place uniauth_saml2_idp
autoflake -r --in-place  --remove-unused-variables --expand-star-imports --remove-all-unused-imports uniauth_saml2_idp

flake8 uniauth_saml2_idp --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 uniauth_saml2_idp --count --statistics  --max-line-length 160 --exclude=*migrations*,*tests*
