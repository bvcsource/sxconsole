#!/usr/bin/env bash

docker exec -t sxconsole /srv/sxconsole/manage.py delete_root_admin $1 $2
