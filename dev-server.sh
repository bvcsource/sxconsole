#!/usr/bin/env bash


if [ -z "$VIRTUAL_ENV" ]; then
    echo 'You are not in a virtualenv. Activate it by running `workon sxconsole`.'
    exit 2
fi

COLUMNS=$(tput cols) supervisord \
    --configuration dev-server.conf \
    --nodaemon \
    --user $USER
