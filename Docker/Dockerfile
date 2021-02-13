FROM python:alpine
LABEL maintaner="angelo.furfaro@unical.it"
ENV REFRESHED_AT 2021-02-11

COPY ./uniAuth/ /home/uniAuth/
RUN apk update
RUN apk add git make rust cargo  mysql mysql-dev libffi-dev gcc g++ musl-dev openldap-dev
WORKDIR /home/uniAuth/
RUN pip3 install -r requirements.txt --ignore-installed
