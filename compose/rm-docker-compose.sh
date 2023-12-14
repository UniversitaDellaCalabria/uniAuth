#!/bin/bash
set x
set e 

echo -e "Eseguo il down e la distruzione della composizione. \n"

docker compose -f docker-compose.yml down -v

sudo docker container rm uniauth-nginx
sudo docker container rm uniauth
sudo docker container rm uniauth-db
sudo docker image rm compose_uniauth

exit 0
