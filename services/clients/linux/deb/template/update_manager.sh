#!/bin/sh

# Update manager installation
apt-get -y install python-support

echo 'Installing Pulse update manager'
! dpkg -i pulse-update-manager*.deb && (
    echo "Unable to install Pulse update manager, aborting"
    exit 1
)
