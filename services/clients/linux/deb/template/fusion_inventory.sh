#!/bin/sh

# Vars
. ./server_conf
fusion_cfg="/etc/fusioninventory/agent.cfg"

# Fusion installation

echo 'Installing fusion inventory agent ...'
! apt-get -y install fusioninventory-agent && (
    echo "Unable to install fusioninventory-agent, aborting"
    exit 1
)

# Fusion configuration

if [ -f $fusion_cfg ]; then
    sed -i "/^server/c\server=$pulse_url" $fusion_cfg
    grep '^server' /etc/fusioninventory/agent.cfg > /dev/null
    if [ ! $?  -eq 0 ]; then
        echo "server=$pulse_url" >> $fusion_cfg
    fi
else
    echo "Unable to find FusionInventory configuration file, aborting."
    exit 1
fi

# Restarting fusion inventory service
service fusioninventory-agent restart

# Forcing new inventory
/usr/bin/fusioninventory-agent
