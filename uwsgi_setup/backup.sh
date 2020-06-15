#!/bin/bash

PROJ_NAME=unicalauth
PROJ_PATH=/opt/$PROJ_NAME
ENV_PATH=/opt/django-idp.env
export DJANGO_SETTINGS_MODULE="django_idp.settings"

cd $PROJ_PATH

PASSWORD=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['default']['PASSWORD'])")
USERNAME=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['default']['USER'])")
DB=$($ENV_PATH/bin/python3 -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])")

BACKUP_DIR="/opt/dumps_unicalauth"
BACKUP_DIR_JSON=$BACKUP_DIR"/json"
BACKUP_DIR_SQL=$BACKUP_DIR"/sql"
BACKUP_DIR_MEDIA=$BACKUP_DIR"/media"
FNAME="$PROJ_NAME.$(date +"%Y-%m-%d_%H%M%S")"

# sudo apt install p7zip-full

mkdir -p $BACKUP_DIR
mkdir -p $BACKUP_DIR_JSON
mkdir -p $BACKUP_DIR_SQL
mkdir -p $BACKUP_DIR_MEDIA

set -x
set -e

# clear expired sessions
$ENV_PATH/bin/python3 $PROJ_PATH/manage.py  clearsessions

# JSON dump, encrypt and compress
$ENV_PATH/bin/python3 $PROJ_PATH/manage.py dumpdata --exclude auth.permission --exclude contenttypes --exclude sessions --indent 2  | 7z a $BACKUP_DIR_JSON/$FNAME.json.7z -si -p$PASSWORD

# SQL dump, encrypt and compress
mysqldump -u $USERNAME --password=$PASSWORD $DB | 7z a $BACKUP_DIR_SQL/$FNAME.sql.7z -si -p$PASSWORD

# decrypt
# 7z x $BACKUP_DIR/$FNAME.7z -p$PASSWORD

# media files
# [ -d "$PROJ_PATH/data/media" ] && rsync -avu --delete $PROJ_PATH/data/media $BACKUP_DIR_MEDIA
[ -d "$PROJ_PATH/data/media" ] && rsync -avu $PROJ_PATH/data/media $BACKUP_DIR_MEDIA
