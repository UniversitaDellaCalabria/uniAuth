#####################
# pyMutliLDAP related
#####################
import ldap3
from ldap3 import ALL, NTLM
from multildap.client import LdapClient
# GLOBALS

# encoding
ldap3.set_config_parameter('DEFAULT_SERVER_ENCODING',
                           'UTF-8')
# some broken LDAP implementation may have different encoding
# than those expected by RFCs
# ldap3.set_config_paramenter('ADDITIONAL_ENCODINGS', ...)

# timeouts
ldap3.set_config_parameter('RESTARTABLE_TRIES', 3)
ldap3.set_config_parameter('POOLING_LOOP_TIMEOUT', 2)
ldap3.set_config_parameter('RESET_AVAILABILITY_TIMEOUT', 2)
ldap3.set_config_parameter('RESTARTABLE_SLEEPTIME', 2)


XDR_DEMO = dict(server =
                   dict(host = 'ldap://10.5.3.19:389',
                        connect_timeout = 5,
                        get_info=ALL
                        ),
               connection =
                   dict(user="example.local\\xdrplus-user",
                        password="That-password", 
                        read_only = True,
                        version = 3,
                        # see ldap3 client_strategies
                        client_strategy = ldap3.RESTARTABLE,
                        auto_bind = True,
                        pool_size = 10,
                        pool_keepalive = 10,
                        authentication=NTLM
                        ),
                search =
                    dict(search_base = 'CN=Users,DC=example,DC=local',
                         search_filter = '(objectclass=person)',
                         search_scope = ldap3.SUBTREE,

                         # general purpose for huge resultsets
                         # TODO: implement paged resultset, see: examples/paged_resultset.py
                         # size_limit = 500,
                         # paged_size = 1000, # up to 500000 results
                         # paged_criticality = True, # check if the server supports paged results
                         # paged_cookie = True, # must be sent back while requesting subsequent entries

                         # to get all = # '*'
                         attributes = ['cn','sn','givenName','mail']
                        ),
                  encoding = 'utf-8',
                  rewrite_rules =
                        [

                         # {'package': 'multildap.attr_rewrite',
                          # 'name': 'append',
                          # 'kwargs': {'value': '@unical.it',
                                     # 'to_attrs': ['eduPersonPrincipalName',]}},

                         # {'package': 'attr_rewrite',
                          # 'name': 'regexp_replace',
                          # 'kwargs': {'regexp': '', 'sub': '',}},

                        ],
                  # Authentication settings
                  # only needed if behind multildap proxy
                  # rewrite_dn_to = _REWRITE_DN_TO,
                  allow_authentication = True,
                  uid_alias = 'cn'
            )

# put multiple connections here
LDAP_CONNECTIONS = {
    'DEFAULT' : XDR_DEMO,
}
LDAP_CONNECTIONS = [LdapClient(conf) for conf in LDAP_CONNECTIONS.values()]
