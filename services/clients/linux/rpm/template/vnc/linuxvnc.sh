#!/bin/sh

echo 'Installing x11vnc ...'
apt-get -y install linuxvnc

# Installing init script
cp linuxvnc_init /etc/init.d/linuxvnc
update-rc.d linuxvnc defaults

# Starting service
/etc/init.d/linuxvnc start
