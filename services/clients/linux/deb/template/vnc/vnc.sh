#!/bin/sh

# Checking if Xserver is installed

cd $(dirname $0)

if dpkg -l|grep xinit > /dev/null; then
    ./x11vnc.sh && exit 0
else
    ./linuxvnc.sh && exit 0
fi

