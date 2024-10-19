Start cassandra database:

`cd apache-cassandra-4.0.0/ && bin/cassandra`
`bin/cassandra -f`

Status check:

`bin/nodetool status`

Connect to database:

`bin/cqlsh`

Create keyspace:
`cqlsh> CREATE KEYSPACE pixel WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};`

~OPTIONAL add symlink:

`sudo ln -s /home/pc/apache-cassandra-4.0.7/bin/cqlsh /usr/bin/cqlsh`

python manage.py <-> cassandra commands
https://r4fek.github.io/django-cassandra-engine/guide/management_commands/
```
python3 manage.py dbshell
python3 manage.py inspectdb
python3 manage.py sync_cassandra
python3 manage.py syncdb


python3 authentication.py

python3 manage.py shell --settings=websocket_server.settings

>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username="pc")
>>> from sesame.utils import get_token
>>> get_token(user)

python -m websockets ws://localhost:8888/
python -m websockets ws://localhost:8765/
??? somehow port 8888 decided not to work, using 8765

pc@DESKTOP-F0JOMDJ:~/projects/websocket_server$ redis-cli
127.0.0.1:6379> SELECT 1
OK
127.0.0.1:6379[1]> SUBSCRIBE events

