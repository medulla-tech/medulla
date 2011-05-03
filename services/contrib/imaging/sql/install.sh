#!/bin/bash

MODULE_NAME=imaging
BASEDIR=`dirname $0`
SCHEMA_NAME=schema
SCHEMA_MAXVERSION=1

if [ ! -n "${MYSQL_HOST+x}" ]; then
    echo 'Enter MYSQL host (default : "localhost", or $MYSQL_DATABASE if defined)' && read
    [ ! -z $REPLY ] && MYSQL_HOST=$REPLY
    [ -z $MYSQL_HOST ] && MYSQL_HOST='localhost'
fi

if [ ! -n "${MYSQL_BASE+x}" ]; then
    echo 'Enter MYSQL database (default : "'${MODULE_NAME}'", or $MYSQL_BASE if defined)' && read
    [ ! -z $REPLY ] && MYSQL_BASE=$REPLY
    [ -z $MYSQL_BASE ] && MYSQL_BASE="${MODULE_NAME}"
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

MYSQL_CMD="mysql --defaults-extra-file=$MYSQL_CNF --batch --skip-column-names --silent --user $MYSQL_USER --host $MYSQL_HOST"

$MYSQL_CMD $MYSQL_BASE -e "select 1;" 2>/dev/null >/dev/null

if [ "$?" -ne 0 ]; then # try to create database
    $MYSQL_CMD -e "create database $MYSQL_BASE;";
    if [ "$?" -ne 0 ]; then
        echo "error creating database; please check access rights"
        exit 1
    fi
    DB_VERSION=0
else # try to recover db version
    DB_VERSION=`$MYSQL_CMD $MYSQL_BASE -e "select Number from version;" 2> /dev/null`
    if test -z "$DB_VERSION"; then
	echo "Error: unable to get database version"
	exit 1
    fi
fi

[ "$(($DB_VERSION))" -ge "$SCHEMA_MAXVERSION" ] && echo "Already up to date (v.$DB_VERSION)" && exit

for i in `seq --format=%03.f $(($DB_VERSION + 1)) $SCHEMA_MAXVERSION`; do
    $MYSQL_CMD $MYSQL_BASE < $BASEDIR/$SCHEMA_NAME-$i.sql
    if [ "$?" -ne 0 ]; then
        echo "error creating/updating database; please check schema $SCHEMA_NAME-$i.sql"
        exit 1
    fi
done

echo "Update to v.$SCHEMA_MAXVERSION succeeded"
