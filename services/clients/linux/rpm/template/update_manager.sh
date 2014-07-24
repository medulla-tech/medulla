#!/bin/sh

# Update manager installation
apt-get -y install python-support
echo 'Installing Pulse update manager'
dpkg -i pulse-update-manager*.deb 

if [ ! $? -eq 0 ]; then
    apt-get -f install
    dpkg -i pulse-update-manager*.deb
fi
