#!/bin/sh
cd /var/lib/pulse2/clients/linux/deb/template

if ! cp -f /root/.ssh/id_rsa.pub server_key; then
    echo "Unable to Copy server public_key"
    exit 1
fi

pulseip=`grep public_ip /etc/mmc/pulse2/package-server/package-server.ini.local |awk '{print $3}'`
if [ ! $? -eq 0 ]; then
    echo 'Cannot get Pulse Server Public IP, aborting.'
    exit 1
fi

# Updating install.sh with server IP
cat ../install.sh.template|sed "s/__SERVER__/$pulseip/" > ../install.sh

echo "Using http://$pulseip:9999 as inventory server" 

echo pulse_url=\"http://$pulseip:9999\" > server_conf

echo "Downloading latest Pulse update manager package ..."
apt-get download pulse-update-manager 

echo "Compressing new agents ..."
if tar zcvf ../deb_agent.tar.gz * > /dev/null; then
    echo "Pulse agents for Debian generated successfully"
    exit 0
fi


