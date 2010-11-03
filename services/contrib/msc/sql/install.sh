#!/bin/bash

SCHEMA_NAME=schema
SCHEMA_MAXVERSION=16

if [ ! -n "${MYSQL_HOST+x}" ]; then
    echo 'Enter MYSQL host (default : "localhost", or $MYSQL_DATABASE if defined)' && read
    [ ! -z $REPLY ] && MYSQL_HOST=$REPLY
    [ -z $MYSQL_HOST ] && MYSQL_HOST='localhost'
fi

if [ ! -n "${MYSQL_BASE+x}" ]; then
    echo 'Enter MYSQL database (default : "msc", or $MYSQL_BASE if defined)' && read
    [ ! -z $REPLY ] && MYSQL_BASE=$REPLY
    [ -z $MYSQL_BASE ] && MYSQL_BASE='msc'
fi

if [ ! -n "${MYSQL_USER+x}" ]; then
    echo 'Enter MYSQL user (default : "root", or $MYSQL_USER if defined)' && read
    [ ! -z $REPLY ] && MYSQL_USER=$REPLY
    [ -z $MYSQL_USER ] && MYSQL_USER='root'
fi

if [ ! -n "${MYSQL_PWD+x}" ]; then
    echo 'Enter MYSQL password (default : <empty>, or $MYSQL_PWD if defined)' && read
    [ ! -z $REPLY ] && MYSQL_PWD=$REPLY
fi

MYSQL_CNF=`mktemp`
trap "rm -f MYSQL_CNF" EXIT
echo "[client]" >> $MYSQL_CNF
echo "password=$MYSQL_PWD" >> $MYSQL_CNF

MYSQL_CMD="mysql --defaults-extra-file=$MYSQL_CNF --batch --silent --user $MYSQL_USER --host $MYSQL_HOST"

$MYSQL_CMD $MYSQL_BASE -e "select 1;" 2>/dev/null >/dev/null

if [ "$?" -ne 0 ]; then # try to create database
    $MYSQL_CMD -e "create database $MYSQL_BASE;";
    if [ "$?" -ne 0 ]; then
        echo "error creating database; please check access rights"
        exit 1
    fi
    DB_VERSION=0
else # try to recover db version
     DB_VERSION=`$MYSQL_CMD $MYSQL_BASE -e "select Number from version;" | head -1 | tr -d -c [0-9]`
    if [ "$?" -ne 0 ]; then
        echo "error recovering database version; please check access rights"
        exit 1
    fi
fi

[ "$(($DB_VERSION))" -ge "$SCHEMA_MAXVERSION" ] && echo "Already up to date (v.$DB_VERSION)" && exit

for i in `seq --format=%03.f $(($DB_VERSION + 1)) $SCHEMA_MAXVERSION`; do
    $MYSQL_CMD $MYSQL_BASE < $SCHEMA_NAME-$i.sql
done

echo "Update to v.$SCHEMA_MAXVERSION succeeded"
