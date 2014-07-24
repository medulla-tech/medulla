#!/bin/sh

# Fusion installation

echo 'Installing OpenSSH Server ...'
apt-get -y install openssh-server

echo 'Installing OpenSSH Server ...'
apt-get -y install rsync

# Copying server key to /root/.ssh
mkdir -p /root/.ssh/
cat server_key >> /root/.ssh/authorized_keys 
