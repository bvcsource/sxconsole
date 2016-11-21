#!/usr/bin/env bash
set -e

if [ -z "$VIRTUAL_ENV" ]; then
    source $(which virtualenvwrapper.sh)
    set +e; mkvirtualenv sxconsole; set -e
    workon sxconsole
fi

echo "Installing python packages"
pip install pip-tools
pip-sync requirements.txt dev_requirements.txt

# Setup carbon
echo "Setting up local carbon & whisper"
pip install carbon \
    --install-option="--install-lib=${VIRTUAL_ENV}/lib/python2.7/site-packages" \
    --install-option="--prefix=${VIRTUAL_ENV}"
cp carbon/config/* "${VIRTUAL_ENV}/conf/"
if ! carbon-cache.py status > /dev/null; then
    carbon-cache.py start
fi

echo "Installing npm packages"
yarn

echo "All done"
