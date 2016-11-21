FROM centos:centos7
MAINTAINER Skylable Dev-Team <dev-team@skylable.com>

# Install system deps
COPY production/skylable.repo /etc/yum.repos.d/skylable.repo
RUN yum clean all && \
    yum -y update && \
    yum -y install epel-release && \
    yum clean all

RUN yum -y install \
    nginx supervisor python-pip npm redis pwgen python-devel py-bcrypt git \
    gettext skylable-sx


# Update pip, nodejs, npm & yarn
RUN pip install --upgrade pip

RUN npm install -g n yarn
RUN n stable


# install production-specific deps
RUN pip install flup gunicorn


# prepare volumes and workdirs
RUN mkdir -p /srv/static /srv/sxconsole
VOLUME /srv/static/
WORKDIR /srv/sxconsole


# copy server config files
COPY production/nginx-sxconsole.conf /etc/nginx/conf.d/
COPY production/nginx.conf /etc/nginx/
COPY production/custom_50x.html /var/www/error_pages/
COPY production/supervisord.conf /etc/supervisor/


# install sxconsole deps
COPY ./requirements.txt /srv/sxconsole/
RUN pip install -r requirements.txt

COPY ./package.json yarn.lock /srv/sxconsole/
RUN yarn


# copy sxconsole internationalization
COPY ./sx-translations/ /srv/sxconsole/sx-translations
COPY ./assets/i18n /srv/sxconsole/assets/i18n

COPY ./i18n-manager.js /srv/sxconsole/
RUN ./i18n-manager.js process


# copy the rest of the app
COPY ./ /srv/sxconsole


# Initialize the container
COPY production/run.sh /
EXPOSE 443 8000


# Configure the environment
ENV DJANGO_SETTINGS_MODULE=sxconsole.settings.production


CMD /run.sh
