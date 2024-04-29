#!/bin/sh
cd /var/lib/medulla/clients/linux/deb/template

if ! cp -f /root/.ssh/id_rsa.pub server_key; then
    echo "Unable to Copy server public_key"
    exit 1
fi

medullaip=`grep public_ip /etc/mmc/medulla/package-server/package-server.ini.local |awk '{print $3}'`
if [ ! $? -eq 0 ]; then
    echo 'Cannot get Medulla Server Public IP, aborting.'
    exit 1
fi

# Updating install.sh with server IP
cat ../install.sh.template|sed "s/__SERVER__/$medullaip/" > ../install.sh

echo "Using http://$medullaip:9999 as inventory server" 

echo medulla_url=\"http://$medullaip:9999\" > server_conf

echo "Downloading latest Medulla update manager package ..."
aptitude download medulla-update-manager

echo "Compressing new agents ..."
if tar zcvf ../deb_agent.tar.gz * > /dev/null; then
    echo "Medulla agents for Debian generated successfully"
    exit 0
fi


