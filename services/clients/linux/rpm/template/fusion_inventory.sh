#!/bin/sh

# Vars
. ./server_conf
fusion_cfg="/etc/fusioninventory/agent.cfg"

# Fusion installation

echo 'Installing fusion inventory agent ...'

# CentOS 6
# http://www.fusioninventory.org/documentation/agent/installation/linux/rpm/
# warning : minor version could change
rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
yum --enablerepo=remi --enablerepo=optional-rhn install fusioninventory-agent


# ==========================================
# Fusion configuration
# ==========================================

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
