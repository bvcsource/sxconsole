# SX Console

SX Console is a fully functional web administration console for Skylable
SX.


## Development

See DEVELOPMENT.md


## Deployment

### Starting the container

To run your sxconsole instance, install docker, modify `conf_example.yaml`
file in this directory (configure the `server.hosts` and `sx` sections) and run
`./deploy.sh`. The script builds required docker images and starts
the containers.

By default, SX Console will be running at `https://0.0.0.0:8443/`


### Creating your account

Once the container is up and running, run `./add-admin.sh user@example.com
password` to create your account.
