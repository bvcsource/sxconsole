#!/bin/bash

mkdir -p /var/lib/graphite/storage/whisper
touch /var/lib/graphite/storage/index
chown -R www-data /var/lib/graphite/storage
chmod 0775 /var/lib/graphite/storage /var/lib/graphite/storage/whisper

supervisord
