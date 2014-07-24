#!/bin/sh

# Checking if Xserver is installed

cd $(dirname $0)

if dpkg -l|grep xserver-xorg > /dev/null; then
    ./x11vnc.sh
else
    ./linuxvnc.sh
fi

