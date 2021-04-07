
ARG USER=that-user
ARG PASS=that-password
ARG HOST=%
ARG DB=uniauth

ARG COUNTRY=na
ARG STATE=na
ARG LOCATION=na
ARG ORGANIZATION=na
ARG ORGANIZATIONAL_UNIT=na
ARG COMMON_NAME=na

ARG VIRTUAL_ENV=/opt/venv
ARG PATH="$VIRTUAL_ENV/bin:$PATH"


FROM python:3.8-slim-buster as builder

RUN apt update
RUN apt install -y \
	git \
	xmlsec1 \
	mariadb-server \
	libmariadb-dev \
	libssl-dev \
	libmariadb-dev-compat \
	libsasl2-dev \
	libldap2-dev \
	gcc


FROM builder as virtenv

RUN mkdir /app
WORKDIR /app

RUN pip install \
	virtualenv \
	django-sass-processor \
	multildap \
	ldap3 \
	python-ldap \
	design-django-theme \
	django-unical-bootstrap-italia \
	django-admin-rangefilter \
	pycountry
	

ARG VIRTUAL_ENV
ENV VIRTUAL_ENV=$VIRTUAL_ENV
RUN python3 -m venv $VIRTUAL_ENV
ARG PATH
ENV PATH=$PATH
COPY ./requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

ARG USER
ENV USER=$USER
ARG PASS
ENV PASS=$PASS
ARG HOST
ENV HOST=$HOST
ARG DB
ENV DB=$DB
RUN service mysql restart \
	&& mysql -u root -e "\
CREATE USER IF NOT EXISTS '${USER}'@'${HOST}' IDENTIFIED BY '${PASS}';\
CREATE DATABASE IF NOT EXISTS ${DB} CHARACTER SET = 'utf8' COLLATE = 'utf8_general_ci';\
GRANT ALL PRIVILEGES ON ${DB}.* TO '${USER}'@'${HOST}';"


ARG COUNTRY
ARG STATE
ARG LOCATION
ARG ORGANIZATION
ARG ORGANIZATIONAL_UNIT
ARG COMMON_NAME
RUN openssl \
	req -nodes -new -x509 \
	-newkey rsa:2048 \
	-days 3650 \
	-keyout certificates/private.key \
	-out certificates/public.cert \
	-subj "/C=$COUNTRY/ST=$STATE/L=$LOCATION/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$COMMON_NAME"



