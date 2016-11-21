# SX Console Devleopment guide

## Preparing the environment

### Bootstrap script

Install `virutalenv` and `virtualenvwrapper`, as well as `node` and `yarn`.
Then run `./bootstrap.sh`. This script is idempotent, so you can run it again
to refresh your environment when there are new dependencies.

When bootstrap finishes creating your environment, you'll have to activate it
via `workon sxconsole`.


### Initial setup

Copy `conf_example.yaml` file to `conf.yaml` and then configure all the
required fields.

Create and sync your database: `./manage.py migrate`

Create your user: `./manage.py add_root_admin user@example.com password`


## Starting the server

Development of SX Console requires several processes to be running - django,
redis, webpack, etc. Fortunately all you have to do is run `./dev-server.sh`.
This script runs supervisor, which is used to run and manage the development
tools.

By default, sxconsole will be running on `http://0.0.0.0:8000`


## Running tests

```
py.test
```


## Linting

Python: `flake8`

JS: `npm run lint`


## Whitelabel

Copy the example skin:

```
cp skins/example skins/my-new-skin
```

And then edit the files within. To enable the skin, configure the `skin`
setting in `conf.yaml`


## Managing translations

To collect new messages to be translated:

```
./i18n-manager.js collect
./manage.py makemessages
```

This will update `sx-translations` submodule in this repo.

To refresh the translations used in the app:

```
./i18n-manager.js process
./manage.py compilemessages
```
