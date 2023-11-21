
## Setup

````
pip install multildap

# avoid exception: ValueError: unsupported hash type MD4
pip install "pycryptodome==3.18.0"
````

## Connection and searches

````
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE

server = Server('10.5.3.19', get_info=ALL)

conn = Connection(
    server, 
    user="example.local\\xdrplus-user", 
    password="that-pass", 
    authentication=NTLM, 
    auto_bind=True
)


conn.search('cn=*', '(objectclass=*)')
````

````
conn.search('dc=example,dc=local', '(objectclass=person)')

conn.entries

conn.search('dc=example,dc=local', '(objectclass=*)') # ...

conn.search('cn=example,cn=Users,dc=4securitas,dc=local', '(objectclass=person)', search_scope = SUBTREE, attributes = ['cn','sn','givenName','mail'])

conn.search('uid=xdrplus-user,cn=Users,dc=example,dc=local', '(objectclass=person)', search_scope = SUBTREE, attributes = ['cn','sn','givenName','mail'])

````
