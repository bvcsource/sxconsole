# DOCKER-VERSION 0.4.0

FROM ubuntu:12.04
RUN echo 'deb http://us.archive.ubuntu.com/ubuntu/ precise universe' >> /etc/apt/sources.list
RUN apt-get -y update

RUN apt-get -y install python-pip python-twisted supervisor
RUN pip install --upgrade pip
RUN pip install whisper
RUN pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/lib" carbon

# Add system service config
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Add graphite config
COPY ./carbon.conf /var/lib/graphite/conf/carbon.conf
COPY ./storage-schemas.conf /var/lib/graphite/conf/storage-schemas.conf

COPY ./run.sh /

# Carbon pickle receiver port
EXPOSE 2004

CMD /run.sh
