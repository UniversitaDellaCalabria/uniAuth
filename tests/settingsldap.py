import ldap3
from multildap.client import LdapClient

LDAPTEST = dict(server =
                   dict(host = 'ldap://localhost:3899',
                        connect_timeout = 5,
                        # TLS...
                        ),
               connection =
                   dict(user = 'uid=mario,ou=people,dc=testunical,dc=it',
                        password = 'cimpa12',
                        read_only = True,
                        version = 3,
                        # see ldap3 client_strategies
                        client_strategy = ldap3.RESTARTABLE,
                        auto_bind = True,
                        pool_size = 1,
                        pool_keepalive = 1),
                search =
                    dict(search_base = 'ou=people,dc=testunical,dc=it',
                         search_filter = '(objectclass=person)',
                         search_scope = ldap3.SUBTREE,

                         # general purpose for huge resultsets
                         # TODO: implement paged resultset, see: examples/paged_resultset.py
                         # size_limit = 500,
                         # paged_size = 1000, # up to 500000 results
                         # paged_criticality = True, # check if the server supports paged results
                         # paged_cookie = True, # must be sent back while requesting subsequent entries

                         # to get all = # '*'
                         attributes = ['eduPersonPrincipalName',
                                       'schacHomeOrganization',
                                       'mail',
                                       'uid',
                                       'givenName',
                                       'sn',
                                       'eduPersonScopedAffiliation',
                                       'schacPersonalUniqueId',
                                       'schacPersonalUniqueCode'
                                       ]

                        ),
                  encoding = 'utf-8',
                  #rewrite_rules =
                        #[{'package': 'attr_rewrite',
                         #'name': 'replace',
                         #'kwargs': {'from_str': 'testunical', 'to_str': 'unical',}},

                         #{'package': 'attr_rewrite',
                          #'name': 'regexp_replace',
                          #'kwargs': {'regexp': '', 'sub': '',}},

                        #],
                  #rewrite_dn_to = _REWRITE_DN_TO,
                  allow_authentication = True
            )

LDAP_CONNECTIONS = {'DEFAULT' : LDAPTEST}
LDAP_CONNECTIONS = [LdapClient(conf) for conf in LDAP_CONNECTIONS.values()]
