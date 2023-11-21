# Docker Compose

## Table of Contents

1. [What do you need?](#what-do-you-need?)
2. [Run the composition](#run-the-composition)
3. [Stop the composition](#stop-the-composition)
4. [Remove/Delete volumes](#remove/delete-volumes)
5. [Demo data](#demo-data)
6. [Env file](#env-file)
7. [docker compose.yml](#docker compose.yml)

## What do you need?

In order to execute the run script you need:

* jq

Installation example in Ubuntu:

```
sudo apt install jq
```

## Run the composition

### Required at least on first run!

Copy your project folder, customize appa and `django_idp/settingslocal.py`

````
cp -R example example-docker
````

Execute the run script for the first time:

```
cd compose
sudo ./run-docker-compose.sh
```

The following docker volumes are created, if they do not exist:

* uniauth_proj
* uniauth_nginx_certs
* uniauth_nginx_static

The first four are populated with sample data, respectively:

* uniauth_proj with data from ../example-docker
* uniauth_nginx_static with data from ../example-docker/static/
* uniauth_nginx_certs with data from ./nginx/certs/

After these steps, the images of the containers are downloaded and then the containers of the composition are started.

Finally you are warned you can run the following command to check composition start and status:

```
sudo docker compose -f docker-compose.yml logs -f
```

### Where is your data?

Command:

```
sudo docker volume ls
```

In RedHat and Ubuntu based OS the Docker volumes directory is at:

```
sudo ls -1 /var/lib/docker/volumes/
```

### NOT at first run or after volumes deletion!

After first run you can start the composition with the run script or by this commands:

```
sudo docker compose pull; docker compose down -v; docker compose up -d;docker compose logs -f
```

## Stop the composition

```
sudo ./stop-docker compose.sh
```

This script stops all containers of the composition and detaches the volumes, but keeps the data on the persistent volumes.

## Remove/Delete volumes

If you want to start from scratch, or just clear all persistent data, just run the following script:

```
sudo ./rm-persistent-volumes.sh
```

First, the containers of the composition are stopped and the volumes are detached.

Then you are asked if you want to delete the volumes and if you answer yes, you have to confirm volume by volume whether it should be deleted or not.

## Env file

```
# cat .env
HOSTNAME=localhost
```

## docker-compose.yml
In the [project readme](../README.md#configuration-by-environments) is present a detailed list of each environment and function
```
    environment:
      - DJANGO_SUPERUSER_USERNAME=admin
      - DJANGO_SUPERUSER_PASSWORD=that-pass
      - DJANGO_SUPERUSER_EMAIL=that@email.local
      - HOSTNAME=idp.local
```
