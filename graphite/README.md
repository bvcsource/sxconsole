## Graphite + Carbon

An all-in-one image running graphite and carbon-cache. **Version**: 0.9.12.

Starting this container will, by default, expose the the following ports:

- `80`: the graphite web interface
- `2003`: the carbon-cache line receiver (the standard graphite protocol)
- `2004`: the carbon-cache pickle receiver
- `7002`: the carbon-cache query port (used by the web interface)

Example command:

```
docker run -v /data/graphite:/var/lib/graphite/storage/whisper -t -i -d --restart=always --name sxconsole-graphite sxconsole-graphite
```

You can log into the administrative interface of graphite-web (a Django
application) with the username `admin` and password `admin`. These passwords can
be changed through the web interface.

### Data volumes

Graphite data is stored at `/var/lib/graphite/storage/whisper` within the
container.
On the host graphite's metric data is stored at `/data/graphite`.

### Technical details

Originally forked from https://github.com/nickstenning/docker-graphite
