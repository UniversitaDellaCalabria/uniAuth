#!/bin/bash

function delete-volume {
        if [ ! "$(docker volume ls -q -f name=$1)" ]
        then
            echo -e "Il volume $1 non esiste, quindi non faccio nulla! \n"
        else
            read -p "Il volume $1 esiste. Lo cancello?(y/n):" ELIMINA_VOLUME
            ELIMINA_VOLUME=${ELIMINA_VOLUME:-"n"}
            export ELIMINA_VOLUME
            if [ $ELIMINA_VOLUME = "y" ]
            then
                docker volume rm $1
                echo -e "Eliminato $1 !!! \n"
            else
                echo -e "Non ho eliminato $1 !!! \n"
            fi
        fi
}

set x
set e

echo -e "Inizio le procedure per fare il down della composizione e poi CANCELLARE i volumi persistenti! \n"

echo -e "Fermo la composizione! \n"
docker compose -f docker-compose.yml down -v;

echo -e "\n"

read -p "Volete veramente procedere con la cancellazione dei volumi persistenti? Tutti i dati andranno persi! Procedo ? (y/n) :" ELIMINA_DATI_PERSISTENTI
ELIMINA_DATI_PERSISTENTI=${ELIMINA_DATI_PERSISTENTI:-"n"}
export ELIMINA_DATI_PERSISTENTI
if [ $ELIMINA_DATI_PERSISTENTI != "y" ] 
then
    echo -e "\n"
    echo -e "Non elimino nulla ed esco!!! \n"
    exit 0
else

echo -e "Procedo ... \n"                  

echo -e "\n"

delete-volume uniauth_proj
delete-volume uniauth_nginx_certs
delete-volume uniauth_nginx_static

fi

exit 0
