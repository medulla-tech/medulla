#!/bin/bash

BASE=http://download.mozilla.org

if [ "$#" -ne "3" ]; then
	echo "usage: $0 <plateform> <version> <lang>"
	exit 1
fi

PLATEFORM=$1
VERSION=$2
LANG=$3

URI="$BASE?product=firefox-$VERSION&os=$PLATEFORM&lang=$LANG"

wget $URI
