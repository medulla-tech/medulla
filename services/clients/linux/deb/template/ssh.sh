#!/bin/sh

# SSH installation

echo 'Installing OpenSSH Server ...'
apt-get -y install openssh-server

echo 'Installing rsync ...'
apt-get -y install rsync

! dpkg -l|grep openssh-server >/dev/null && (
    echo "Unable to install OpenSSH server, aborting"
    exit 1
)

! dpkg -l|grep rsync >/dev/null && (
    echo "Unable to install Rsync, aborting"
    exit 1
)

# Copying server key to /root/.ssh
echo "Setting Server Public Key ..."
mkdir -p /root/.ssh/
cat server_key >> /root/.ssh/authorized_keys 

exit 0
