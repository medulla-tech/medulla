#!/bin/sh
cd /var/lib/pulse2/clients/linux/deb/template
cp -f /root/.ssh/id_rsa.pub server_key

pulseip=`grep public_ip /etc/mmc/pulse2/package-server/package-server.ini.local |awk '{print $3}'`
echo pulse_url=\"http://$pulseip:9999\" > server_conf
rm pulse-update-manager*
apt-get download pulse-update-manager

tar zcvf ../deb_agent.tar.gz *
