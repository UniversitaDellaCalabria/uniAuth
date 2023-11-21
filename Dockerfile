FROM python:3.10-slim-bullseye as bullseye

RUN apt update
RUN apt install -y \
git \
xmlsec1 \
libmariadb-dev \
libssl-dev \
libmariadb-dev-compat \
libsasl2-dev \
libldap2-dev \
libpq-dev \
postgresql-contrib \
gcc

RUN rm -rf /var/lib/apt/lists/*

RUN mkdir /uniauth
WORKDIR /uniauth

COPY ./requirements.txt .
COPY ./requirements-dev.txt .
COPY ./requirements-customizations.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-dev.txt
RUN pip3 install -r requirements-customizations.txt

COPY ./uniauth_saml2_idp ./uniauth_saml2_idp
COPY ./setup.py .
COPY ./README.md .

COPY xdrplus-iam/ /opt/uniauth/

RUN echo $PWD
RUN ls

RUN pip3 install -e .
RUN pip3 install uwsgi
RUN pip3 install psycopg2
RUN pip3 list

# DB setup - just as a note
# ARG USER=that-user
# ARG PASS=that-password
# ARG HOST=%
# ARG DB=uniauth
# ENV USER=$USER
# ENV PASS=$PASS
# ENV HOST=$HOST
# ENV DB=$DB
# RUN service mysql restart \
# && mysql -u root -e "\
# CREATE USER IF NOT EXISTS ${USER}@${HOST} IDENTIFIED BY ;\
# CREATE DATABASE IF NOT EXISTS ${DB} CHARACTER SET = utf8 COLLATE = utf8_general_ci;\
# GRANT ALL PRIVILEGES ON ${DB}.* TO ${USER}@${HOST};"
