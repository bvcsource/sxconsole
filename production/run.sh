#!/bin/bash -x

set -e

# start SXConsole
RUN_AS=sxconsole
SUGGEST_CMD="docker run -v /path/to/datadir:/data --name=sxconsole --link sxconsole-graphite:sxconsole-graphite --restart=always -d sxconsole"

for i in sxconsole.key sxconsole.crt; do
    if ! [ -r /data/$i ]; then
        echo $i not found. Please use the following syntax and make sure the sxconsole user can read the file:
        echo Use: $SUGGEST_CMD
        exit 1
    fi
done

echo Copying SSL certs...
mkdir -p /etc/nginx/ssl
cp /data/sxconsole.crt /data/sxconsole.key /etc/nginx/ssl/
chmod 600 /etc/nginx/ssl/sxconsole.key

echo Updating SXConsole config file...
mkdir -p /data/sql

if ! [ -r "/data/conf_defaults.yaml" ]; then
    cp /srv/sxconsole/conf_example.yaml /data/conf_defaults.yaml
else
    chmod 600 /data/conf_defaults.yaml
    cp -p /data/conf_defaults.yaml /srv/sxconsole/conf.yaml
fi

if grep -i ^Edit-me-first /srv/sxconsole/conf.yaml; then
    echo Please edit conf_defaults.yaml
    exit 1
fi

if [ -z "$SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR" ]; then
    # is the container linked with a different name? Guess
    export $(env|grep PORT_2004_TCP_ADDR=|head -n 1|sed -e 's/^.*PORT_2004_TCP_ADDR/SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR/')
fi
if [ -z "$SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR" ]; then
    echo You must link this container to sxconsole-graphite
    echo Use: $SUGGEST_CMD
    exit 1
fi
sed -i "s/CARBON_ADDR/$SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR/" /srv/sxconsole/conf.yaml

echo Building static assets
npm run build

# fix permissions
if ! getent passwd $RUN_AS > /dev/null 2>&1; then
    adduser $RUN_AS
fi

python manage.py migrate --noinput # Apply database migrations
chmod -R go-rwx /data/sql
python manage.py compilemessages # Compile translations
python manage.py collectstatic --noinput # Collect static files
chown $RUN_AS /srv/sxconsole/conf.yaml
chown $RUN_AS /data/django_secret_key
chown $RUN_AS /data/sql/db.sqlite3

# Prepare log files and start outputting logs to stdout
mkdir -p /srv/logs/supervisor
touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
chown -R $RUN_AS /srv/logs
tail -n 0 -f /srv/logs/*.log &


echo If you need to add a root admin, run:
echo 'docker exec -t -i  sxconsole su sxconsole -c "/srv/sxconsole/manage.py add_root_admin your-email your-pass"'

/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
