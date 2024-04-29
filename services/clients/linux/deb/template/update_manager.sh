#!/bin/sh

# Update manager installation
apt-get -y install python-support

echo 'Installing Medulla update manager'
! dpkg -i medulla-update-manager*.deb && (
    echo "Unable to install Medulla update manager, aborting"
    exit 1
)
