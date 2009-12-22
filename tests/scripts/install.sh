#!/bin/bash -e

#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

echo "Pulse2 auto-installation script"
echo

if [ ! -f "/etc/init.d/mmc-agent" ];
then
    echo "Please install MMC CORE first."
    exit 1
fi	

if [ ! -f "/bin/lsb_release" ];
then
    echo "Please install lsb_release."
    echo "urpmi lsb-release"
    exit 1
fi	

DISTRIBUTION=`lsb_release -i -s`
RELEASE=`lsb_release -r -s`

PKGS=

if [ `arch` == "x86_64" ];
then
    ARCH=64
else
    ARCH=
fi

function packages_to_install () {
    # MySQL
    PKGS="$PKGS mysql mysql-client python-mysql"
}

if [ ! -f "$DISTRIBUTION-$RELEASE" ];
then
    echo "This version of Operating System ($DISTRIBUTION-$RELEASE) is not supported"
    exit 1
fi

if [ -z $FORCE ];
    then
    echo
    echo "WARNING: this script will erase some parts of your configuration !"
    echo "         type Ctrl-C now to exit if you are not sure"
    echo "         type Enter to continue"
    read
fi

packages_to_install
urpmi --auto --no-suggests $PKGS
rpm -q $PKGS

if [ -z $TMPCO ];
    then
    TMPCO=`mktemp -d`
    pushd $TMPCO
    # Check out Pulse 2 source
    svn co https://mds.mandriva.org/svn/mmc-projects/pulse2/server/trunk pulse2-server
else
    pushd $TMPCO
fi

pushd pulse2-server
make install PREFIX=/usr
popd

popd

/etc/init.d/mysqld stop
sed -i "s/^skip-networking/#skip-networking/" /etc/my.cnf
/etc/init.d/mysqld start

IPADDRESS=`ifconfig eth0 | grep 'inet ' | awk '{print $2}' | sed 's/adr://'`

# Create database msc and configure msc.init

pushd $TMPCO/pulse2-server/services/contrib/msc/sql/
mysqladmin create msc
mysql msc < schema.sql
mysql msc < schema.sql.v.2
mysql msc < schema.sql.v.3
mysql msc < schema.sql.v.4
mysql msc < schema.sql.v.5
mysql msc < schema.sql.v.6
mysql msc < schema.sql.v.7
mysql msc < schema.sql.v.8
mysql msc < schema.sql.v.9
mysql msc < schema.sql.v.10
mysql msc < schema.sql.v.11
mysql msc < schema.sql.v.12
mysql msc < schema.sql.v.13
mysql msc < schema.sql.v.14
mysql msc < schema.sql.v.15
popd

sed -i "s/#\[main\]/\[main\]/" /etc/mmc/plugins/msc.ini
sed -i "s/# disable = 0/disable = 0/" /etc/mmc/plugins/msc.ini
sed -i "s/# mserver = 127.0.0.1/mserver = $IPADDRESS/" /etc/mmc/plugins/msc.ini
sed -i "/\[scheduler_api\]/{n; s/host = 127.0.0.1/host = $IPADDRESS/}" /etc/mmc/plugins/msc.ini

# Create database dyngroup and configure dyngroup.init
pushd $TMPCO/pulse2-server/services/contrib/dyngroup/sql/
mysqladmin create dyngroup
mysql dyngroup < schema.sql
mysql dyngroup < schema.sql.v.1
mysql dyngroup < schema.sql.v.2
mysql dyngroup < schema.sql.v.3
mysql dyngroup << EOF
EOF
sed -i "s/# default_module = /default_module = inventory/" /etc/mmc/plugins/dyngroup.ini
sed -i "s/activate = 0/activate = 1/" /etc/mmc/plugins/dyngroup.ini
popd

# Create database inventory and configure inventory.init
pushd $TMPCO/pulse2-server/services/contrib/inventory/sql/
mysqladmin create inventory
mysql inventory < schema.sql
mysql inventory < schema.sql.v.2
mysql inventory < schema.sql.v.3
mysql inventory < schema.sql.v.4
mysql inventory < schema.sql.v.5
mysql inventory < schema.sql.v.6
mysql inventory < schema.sql.v.7
mysql inventory < schema.sql.v.8
mysql inventory < schema.sql.v.9
mysql inventory < schema.sql.v.10
sed -i "s/disable = 1/disable = 0/" /etc/mmc/plugins/inventory.ini
sed -i "s/# \[querymanager\]/\[querymanager\]/" /etc/mmc/plugins/inventory.ini
sed -i "s/# list =/list =/" /etc/mmc/plugins/inventory.ini
sed -i "s/# double =/double =/" /etc/mmc/plugins/inventory.ini
sed -i "s/# halfstatic =/halfstatic =/" /etc/mmc/plugins/inventory.ini
popd

mysql << EOF
GRANT ALL PRIVILEGES ON msc.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON dyngroup.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON inventory.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
FLUSH PRIVILEGES
EOF

# configure base.ini

sed -i "s/# \[computers\]/\[computers\]/" /etc/mmc/plugins/base.ini
sed -i "s/# method = inventory/method = inventory/" /etc/mmc/plugins/base.ini

#insert in inventory database computers for test
#mysql -h localhost -u mmc -pmmc  inventory</root/selenium/inventory.sql

# create the temp folder for packages

mkdir -p /tmp/package_tmp/put1/test1
mkdir -p /tmp/package_tmp/put1/test2

sed -i "s/host = /host = $IPADDRESS/" /etc/mmc/pulse2/package-server/package-server.ini

# Config pkgs.ini
sed -i "s/server = localhost/server = $IPADDRESS/" /etc/mmc/plugins/pkgs.ini

#launch all service of pulse2
echo "Launch pulse2's services"
/etc/init.d/pulse2-package-server restart
/etc/init.d/pulse2-launchers restart
/etc/init.d/pulse2-scheduler restart

# Launch mmc-agent
/etc/init.d/mmc-agent force-stop
rm -f /var/run/mmc-agent.pid
/etc/init.d/mmc-agent start

echo "Installation done successfully"
exit 0
