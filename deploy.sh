#!/usr/bin/env bash
set -e

process_args () {
    while [[ $# -gt 0 ]]; do
        key="$1"
        case $key in
            --non-interactive)
                echo '** Performing automatic deploy **'
                NON_INTERACTIVE=true
            ;;
        esac
        shift
    done
}

process_args $@


DEFAULT_BASE_DIR='/var/lib/sxconsole'

echo -n "Specify the path for persistent docker storage [default: $DEFAULT_BASE_DIR]: "
if [ -n "$NON_INTERACTIVE" ]; then
    echo '/data'
    BASE_DIR='/data'
else
    read BASE_DIR
fi

BASE_DIR=${BASE_DIR:-$DEFAULT_BASE_DIR}
SXCONSOLE_DIR="$BASE_DIR/sxconsole"
GRAPHITE_DIR="$BASE_DIR/sxconsole-graphite"
SXCONSOLE_CONFIG="$SXCONSOLE_DIR/conf_defaults.yaml"

mkdir -p "$SXCONSOLE_DIR"
mkdir -p "$GRAPHITE_DIR"

if [ ! -e "$SXCONSOLE_CONFIG" ]; then
    echo "Could not find 'conf_defaults.yaml' in $SXCONSOLE_DIR"
    echo 'Preparing config template...'
    cp ./conf_example.yaml "$SXCONSOLE_CONFIG"
    echo "Config template has been saved to $SXCONSOLE_CONFIG"
    echo 'Please edit that file and re-run this script.'
    exit 2
fi

if [ ! -e "$SXCONSOLE_DIR/sxconsole.key" ]; then
    echo "Could not find 'sxconsole.key' in $SXCONSOLE_DIR"
    echo 'Generating self-signed certs...'
    openssl genrsa -out ca.key 2048
    openssl req -new -key ca.key -out ca.csr
    openssl x509 -req -days 3650 -in ca.csr -signkey ca.key -out ca.crt
    rm ca.csr
    mv ca.crt "$SXCONSOLE_DIR/sxconsole.crt"
    mv ca.key "$SXCONSOLE_DIR/sxconsole.key"
fi

echo -n 'Rebuild sxconsole docker image? (Y/n) '
if [ -n "$NON_INTERACTIVE" ]; then
    echo 'y'
    ANSWER='y'
else
    read ANSWER
fi
if [ "$ANSWER" != 'n' ]; then
    echo 'Building new image'
    docker build -t sxconsole .
fi

echo -n 'Rebuild sxconsole-graphite docker image? (y/N) '
if [ -n "$NON_INTERACTIVE" ]; then
    echo 'n'
    ANSWER='n'
else
    read ANSWER
fi
if [ "$ANSWER" == 'y' ]; then
    echo 'Building new image'
    docker build -t sxconsole-graphite graphite
fi

echo 'Restarting containers...'
set +e
docker stop sxconsole sxconsole-graphite > /dev/null
docker rm sxconsole sxconsole-graphite > /dev/null
set -e

docker run -d \
    -v "$GRAPHITE_DIR:/var/lib/graphite/storage/whisper" \
    --name sxconsole-graphite \
    sxconsole-graphite

docker run -d \
    -v "$SXCONSOLE_DIR:/data" \
    -v "$SXCONSOLE_DIR/logs:/srv/logs" \
    -v "$GRAPHITE_DIR:/var/lib/graphite/storage/whisper" \
    -p :8443:443 \
    --link sxconsole-graphite:sxconsole-graphite \
    --name=sxconsole \
    sxconsole

docker ps

echo
echo 'All done!'
echo '> Press enter to follow logs from sxconsole container.'
echo '> Press Ctrl-C to exit.'
if [ -n "$NON_INTERACTIVE" ]; then
    echo
else
    read
fi

docker logs -f sxconsole
