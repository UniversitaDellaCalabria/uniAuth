import sys
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from twisted.application import service
from twisted.internet.endpoints import serverFromString
from twisted.internet.protocol import ServerFactory
from twisted.python.components import registerAdapter
from twisted.python import log
from ldaptor.inmemory import fromLDIFFile
from ldaptor.interfaces import IConnectedLDAPEntry
from ldaptor.protocols.ldap.ldapserver import LDAPServer


LDIF = b"""\
dn: dc=it
dc: it
objectClass: dcObject

dn: dc=testunical,dc=it
dc: testunical
objectClass: dcObject
objectClass: organization

dn: ou=people,dc=testunical,dc=it
objectClass: organizationalUnit
ou: people

dn: uid=mario,ou=people,dc=testunical,dc=it
objectclass: inetOrgPerson
objectclass: organizationalPerson
objectclass: person
objectclass: userSecurityInformation
objectclass: eduPerson
objectclass: radiusprofile
objectclass: sambaSamAccount
objectclass: schacContactLocation
objectclass: schacEmployeeInfo
objectclass: schacEntryConfidentiality
objectclass: schacEntryMetadata
objectclass: schacExperimentalOC
objectclass: schacGroupMembership
objectclass: schacLinkageIdentifiers
objectclass: schacPersonalCharacteristics
objectclass: schacUserEntitlements
uid: mario
userpassword: cimpa12
sambantpassword: 24cec09b7ced05ea259a94ae51306e6e
cn: mario
sn: rossi
givenName: mario
mail: mario.rossi@testunical.it
displayname: Mario Rossi
edupersonaffiliation: staff
edupersonaffiliation: member
edupersonentitlement: urn:mace:terena.org:tcs:personal-user
edupersonentitlement: urn:mace:terena.org:tcs:escience-user
edupersonprincipalname: mario@testunical.it
edupersonscopedaffiliation: staff@testunical.it
edupersonscopedaffiliation: member@testunical.it
edupersonscopedaffiliation: member@altrodominio.it
schachomeorganization: testunical.it
schachomeorganizationtype: university
schachomeorganizationtype: educationInstitution
schacPersonalUniqueID: urn:schac:personalUniqueID:IT:CF:CODICEFISCALEmario
schacPersonalUniqueCode: urn:schac:personalUniqueCode:IT:testunical.it:dipendente:1237403
schacPersonalUniqueCode: urn:schac:personalUniqueCode:IT:testunical.it:studente:1234er

"""



class Tree(object):

    def __init__(self):
        global LDIF
        self.f = BytesIO(LDIF)
        d = fromLDIFFile(self.f)
        d.addCallback(self.ldifRead)

    def ldifRead(self, result):
        self.f.close()
        self.db = result


class LDAPServerFactory(ServerFactory):
    protocol = LDAPServer

    def __init__(self, root):
        self.root = root

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.debug = self.debug
        proto.factory = self
        return proto


if __name__ == '__main__':
    from twisted.internet import reactor
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 3899
    # First of all, to show logging info in stdout :
    log.startLogging(sys.stderr)
    # We initialize our tree
    tree = Tree()
    # When the LDAP Server protocol wants to manipulate the DIT, it invokes
    # `root = interfaces.IConnectedLDAPEntry(self.factory)` to get the root
    # of the DIT.  The factory that creates the protocol must therefore
    # be adapted to the IConnectedLDAPEntry interface.
    registerAdapter(
        lambda x: x.root,
        LDAPServerFactory,
        IConnectedLDAPEntry)
    factory = LDAPServerFactory(tree.db)
    factory.debug = True
    application = service.Application("ldaptor-server")
    myService = service.IServiceCollection(application)
    serverEndpointStr = "tcp:{0}".format(port)
    e = serverFromString(reactor, serverEndpointStr)
    d = e.listen(factory)
    reactor.run()
