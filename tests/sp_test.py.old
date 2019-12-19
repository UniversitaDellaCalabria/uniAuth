import re
import requests


form_action_regex = '[\s\n.]*action="(?P<action>[a-zA-Z0-9\:\.\_\-\?\&\/]*)"'
form_samlreq_regex = '[\s\n.]*name="SAMLRequest"'
form_samlreq_value_regex = 'value="(?P<value>[a-zA-Z0-9+]*)"[\s\n.]*'

# TODO: add RelayState
#  <input type="hidden" name="RelayState" value="/"/>


class Saml2SPAuthnReq(object):
    """
    TODO:
        - add error handling in conformity of:
          https://wiki.geant.org/display/eduGAIN/eduGAIN+Connectivity+Check
    """
    def __init__(self, wayf=False, verify=False, debug=False, timeout=12):
        # create an user agent here ;)
        self.session = requests.Session()
        self.wayf = wayf
        self.debug = debug
        self.timeout = timeout
        self.verify = verify
        # to be filled
        self.saml_request_dict = {}

    def _check_response(self, request):
        print(request.reason)
        if self.debug:
            print(request.content)
        assert request.status_code == 200

    def _handle_error(self, info):
        raise Exception(('Error: Cannot find any saml request '
                         'value in {}').format(info))

    def saml_request(self, target,
                     form_action_regex=form_action_regex,
                     form_samlreq_regex=form_samlreq_regex):
        # do a GET, do not verify ssl cert validity
        sp_saml_req_form = self.session.get(target, verify=self.verify,
                                            timeout=self.timeout)
        if not sp_saml_req_form.ok:
            raise Exception('SP SAML Request Failed')

        html_content =  sp_saml_req_form._content.decode() \
                        if isinstance(sp_saml_req_form._content, bytes) \
                        else sp_saml_req_form._content

        if self.wayf:
            self._check_response(sp_saml_req_form)
            return

        action = re.search(form_action_regex, html_content)
        if not action: self._handle_error(target)
        self.saml_request_dict.update(action.groupdict())

        saml_request = re.search(form_samlreq_regex, html_content)
        if not saml_request: self._handle_error(target)
        self.saml_request_dict.update(saml_request.groupdict())

        saml_request_value = re.search(form_samlreq_value_regex, html_content)
        self.saml_request_dict.update(saml_request_value.groupdict())

        if self.debug:
            print(self.saml_request_dict)

    def saml_request_post(self):
        d = {'SAMLRequest': self.saml_request_dict['value'],
             'RelayState': '/'}
        idp_auth_form = self.session.post(self.saml_request_dict['action'],
                                          data=d, timeout=self.timeout)
        self._check_response(idp_auth_form)


if __name__ == '__main__':
    import argparse
    _description = ('Check if an SP is able to make an Authn Request to an Idp '
                    'and if this latter accepts it.')
    _epilog = ('python3 test_saml2_authnreq.py -target "https://peo.unical.it" --check-cert'
              '\nor\n'
              'python3 test_saml2_authnreq.py -target "https://sp24-test.garr.it/Shibboleth.sso/Login?SAMLDS=1&target=ss%3Amem%3A4eae3aa14e7d76fa1e78be0bc848b74e84326e83779adf0508f4fcd442a28ba5&entityID=https%3A%2F%2Fauth.unical.it%2Fidp%2Fmetadata%2F" --wayf --check-cert'
              )
    parser = argparse.ArgumentParser(description=_description,
                                     epilog='Usage example: {}'.format(_epilog),
                                     formatter_class=argparse.RawTextHelpFormatter)

    # parameters
    parser.add_argument('-target', required=True,
                        help=("service provider protected resource. "
                              "Used to be redirected to the IdP login page"))
    # parser.add_argument('-u', required=False,
                        # help="username")
    # parser.add_argument('-p', required=False,
                    # help="password")
    parser.add_argument('--wayf', action='store_true',
                        help=("if the url contains the wayf selection."
                              "See usage examples."),
                        required=False,
                        default=False)
    parser.add_argument('--check-cert', action='store_true',
                        help="validate https TLS certificates", required=False,
                        default=False)
    parser.add_argument('-timeout',
                        metavar='N',
                        type=float,
                        default=5,
                        required=False,
                        help="http connection timeout, default: 5 seconds")
    parser.add_argument('-debug', action='store_true',
                        help="print debug informations", required=False)
    args = parser.parse_args()

    # let's go
    ua = Saml2SPAuthnReq(wayf=args.wayf, verify=args.check_cert,
                         debug=args.debug, timeout=args.timeout)
    ua.saml_request(target=args.target)
    if not ua.wayf:
        ua.saml_request_post()
