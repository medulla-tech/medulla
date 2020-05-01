#!/bin/bash -e

#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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

export LANG=C
export LC_ALL=C

echo "Pulse2 auto-installation script"
echo

if [ ! -f "/etc/init.d/mmc-agent" ];
then
    echo "Please install MMC CORE first."
    exit 1
fi

if [ ! -f `which lsb_release` ];
then
    echo "Please install lsb_release."
    echo "urpmi lsb-release"
    echo "apt-get install lsb-release"
    exit 1
fi

DISTRIBUTION=`lsb_release -i -s`
RELEASE=`lsb_release -r -s`

PKGS=

ARCH=
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    if [ `arch` == "x86_64" ]; then
        ARCH=64
    fi
fi

function packages_to_install () {
    # LDAP stuff
    if [ $DISTRIBUTION == "MandrivaLinux" ]; then
        PKGS="$PKGS openldap-servers openldap-mandriva-dit"
    fi
    if [ $DISTRIBUTION == "Debian" ]; then
        echo slapd slapd/domain string mandriva.com | debconf-set-selections
        echo slapd shared/organization string mandriva | debconf-set-selections
        echo slapd slapd/password1 string secret | debconf-set-selections
        echo slapd slapd/password2 string secret | debconf-set-selections
    	PKGS="$PKGS slapd"
    fi

    # Python
    PKGS="$PKGS python-twisted-web python-ldap"

    # Apache/PHP
    if [ $DISTRIBUTION == "MandrivaLinux" ]; then
        PKGS="$PKGS apache-mpm-prefork apache-mod_php php-gd php-iconv php-xmlrpc gettext"
    fi
    if [ $DISTRIBUTION == "Debian" ]; then
	PKGS="$PKGS apache2 libapache2-mod-php5 php5-gd php5-xmlrpc gettext"
    fi

    # Development & install
    PKGS="$PKGS subversion make gcc wget"

    if [ $DISTRIBUTION == "MandrivaLinux" ]; then
        if [ $RELEASE == "2006.0" ];
            then
            PKGS="$PKGS lib${ARCH}python2.4-devel libldap2.3_0-devel"
        fi
        if [ $RELEASE == "2009.0" ];
        then
        PKGS="$PKGS lib${ARCH}python2.5-devel libldap2.4_2-devel python-setuptools python-sqlalchemy"
        fi
        if [ $RELEASE == "2010.0" ];
            then
            # The python-sqlalchemy lib must be installed manually because we are
            # compatible only with version 0.4, and 2010.0 provides version 0.5.
            PKGS="$PKGS lib${ARCH}python2.6-devel lib${ARCH}crack2-python libldap2.4_2-devel python-setuptools"
        fi
    fi
    if [ $DISTRIBUTION == "Debian" ]; then
        if [ $RELEASE == "5.0.6" ]; then
            PKGS="$PKGS python2.5-dev libldap2-dev python-setuptools python-pylibacl python-sqlalchemy"
        fi
    fi

    # MySQL
    if [ $DISTRIBUTION == "MandrivaLinux" ]; then
        PKGS="$PKGS mysql mysql-client"
        if [ $RELEASE == "2010.0" -o $RELEASE == "2009.0" ];
            then
            PKGS="$PKGS python-mysql"
        fi
    fi
    if [ $DISTRIBUTION == "Debian" ]; then
        PKGS="$PKGS mysql-server mysql-client python-mysqldb"
    fi

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
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    urpmi.update -a
    urpmi --auto --no-suggests $PKGS
    rpm -q $PKGS
fi
if [ $DISTRIBUTION == "Debian" ]; then
    # don't ask mysql password
    export DEBIAN_FRONTEND=noninteractive
    apt-get install --yes $PKGS
    dpkg -l $PKGS
    export DEBIAN_FRONTEND=newt
fi

if [ -z $TMPCO ];
    then
    TMPCO=`mktemp -d`
    TMPREMOVE=1
    pushd $TMPCO
    # Check out Pulse 2 source
    svn co https://mds.mandriva.org/svn/mmc-projects/pulse2/server/trunk pulse2
else
    pushd $TMPCO
fi

pushd pulse2
make install PREFIX=/usr
popd

popd

IPADDRESS=`ifconfig eth0 | grep 'inet ' | awk '{print $2}' | sed 's/addr://'`
echo "My IP address is $IPADDRESS"

export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PWD=

# Create database pulse2
pushd $TMPCO/pulse2/services/contrib/pulse2/sql/
export MYSQL_BASE=pulse2
./install.sh
popd

# Create database msc and configure msc.ini
pushd $TMPCO/pulse2/services/contrib/msc/sql/
export MYSQL_BASE=msc
./install.sh
sed -i "s/#\[main\]/\[main\]/" /etc/mmc/plugins/msc.ini
sed -i "s/# disable = 0/disable = 0/" /etc/mmc/plugins/msc.ini
sed -i "s/# mserver = 127.0.0.1/mserver = $IPADDRESS/" /etc/mmc/plugins/msc.ini
sed -i "/\[scheduler_api\]/{n; s/host = 127.0.0.1/host = $IPADDRESS/}" /etc/mmc/plugins/msc.ini
popd

# Create database dyngroup and configure dyngroup.ini
pushd $TMPCO/pulse2/services/contrib/dyngroup/sql/
export MYSQL_BASE=dyngroup
./install.sh
sed -i "s/# default_module = /default_module = inventory/" /etc/mmc/plugins/dyngroup.ini
sed -i "s/activate = 0/activate = 1/" /etc/mmc/plugins/dyngroup.ini
popd

# Create database inventory and configure inventory.ini
pushd $TMPCO/pulse2/services/contrib/inventory/sql/
export MYSQL_BASE=inventory
./install.sh
sed -i "s/disable = 1/disable = 0/" /etc/mmc/plugins/inventory.ini
sed -i "s/# \[querymanager\]/\[querymanager\]/" /etc/mmc/plugins/inventory.ini
sed -i "s/# list =/list =/" /etc/mmc/plugins/inventory.ini
sed -i "s/# double =/double =/" /etc/mmc/plugins/inventory.ini
sed -i "s/# halfstatic =/halfstatic =/" /etc/mmc/plugins/inventory.ini
popd

# Create database imaging and configure imaging.ini
pushd $TMPCO/pulse2/services/contrib/imaging/sql/
export MYSQL_BASE=imaging
./install.sh
popd

mysql << EOF
GRANT ALL PRIVILEGES ON msc.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON dyngroup.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON inventory.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON imaging.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON pulse2.* TO 'mmc'@'localhost'
IDENTIFIED BY 'mmc' WITH GRANT OPTION;
FLUSH PRIVILEGES
EOF

# Basic installation of GLPI
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    pushd /var/www/html
    wget -N https://forge.indepnet.net/attachments/download/597/glpi-0.72.4.tar.gz
    tar xzf glpi-0.72.4.tar.gz
    chown -R apache.apache glpi
    rm glpi-0.72.4.tar.gz
    popd
fi

# configure base.ini
sed -i "s/# \[computers\]/\[computers\]/" /etc/mmc/plugins/base.ini
sed -i "s/# method = inventory/method = inventory/" /etc/mmc/plugins/base.ini

# Configure imaging.ini
sed -i "s/# disable = 1/disable = 0/" /etc/mmc/plugins/imaging.ini

# Enable profile in dyngroup
sed -i "s/# profiles_enable = 0/profiles_enable = 1/" /etc/mmc/plugins/dyngroup.ini

# create the temp folder for packages
mkdir -p /tmp/package_tmp/put1/test1
mkdir -p /tmp/package_tmp/put1/test2

# Package server configuration
sed -i "6s/^# host =/host = $IPADDRESS/" /etc/mmc/pulse2/package-server/package-server.ini
sed -i "s/# \[imaging_api\]/\[imaging_api\]/" /etc/mmc/pulse2/package-server/package-server.ini
UUID=`uuidgen`
sed -i "s/# uuid = PLEASE_PUT_A_UUID_FOR_THAT_SERVER/uuid = $UUID/" /etc/mmc/pulse2/package-server/package-server.ini
# Copy quick actions
mkdir -p /var/lib/pulse2/qactions
cp $TMPCO/pulse2/services/contrib/msc/quick_actions/* /var/lib/pulse2/qactions/

# Config pkgs.ini
sed -i "s/server = localhost/server = $IPADDRESS/" /etc/mmc/plugins/pkgs.ini

# Imaging server configuration
# Hooks directory
sed -i "s|# hooks_dir = /usr/local|hooks_dir = /usr|" /etc/mmc/pulse2/imaging-server/imaging-server.ini
# Package Server IP address
sed -i "s/# host = 127.0.0.1/host = $IPADDRESS/" /etc/mmc/pulse2/imaging-server/imaging-server.ini

# Generate SSH key if not available
if [ ! -f /root/.ssh/id_dsa ];
then
    ssh-keygen -t dsa -f /root/.ssh/id_dsa -N ""
    # Allow SSH connection without password on localhost
    cat /root/.ssh/id_dsa.pub > /root/.ssh/authorized_keys
fi

# Set NFS exports, and restart NFS services
cp $TMPCO/pulse2/services/contrib/imaging-server/exports /etc/exports
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    if [ $RELEASE != "2006.0" ];
    then
	/etc/init.d/nfs-common restart
	/etc/init.d/nfs-server restart
    else
	/etc/init.d/portmap restart
	/etc/init.d/nfs restart
    fi

    if [ $RELEASE != "2006.0" ];
    then
    # Set ATFTPD root directory
	sed -i "s|ATFTPD_DIRECTORY=\"/var/lib/tftpboot\"|ATFTPD_DIRECTORY=\"/var/lib/pulse2/imaging\"|" /etc/sysconfig/atftpd
	/etc/init.d/atftpd restart
    fi
fi

# Launch mmc-agent
/etc/init.d/mmc-agent force-stop
rm -f /var/run/mmc-agent.pid
/etc/init.d/mmc-agent start

# Launch all service of Pulse 2
echo "Launch Pulse 2's services"
/etc/init.d/pulse2-package-server restart
/etc/init.d/pulse2-launchers restart
/etc/init.d/pulse2-scheduler restart
/etc/init.d/pulse2-imaging-server restart
/etc/init.d/pulse2-inventory-server restart

=======
if [ $DISTRIBUTION == "Debian" ]; then
    export NOCHECKPASSWORD=1
fi

if [ $RELEASE == "2006.0" ];
    then
    export NOCHECKPASSWORD=1
    # Download and setup Python setuptools
    wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e
    tar xzf setuptools-0.6c11.tar.gz
    pushd setuptools-0.6c11
    python setup.py install
    popd
fi
pushd mmc-core/agent
make install PREFIX=/usr
popd

pushd mmc-core/web
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    make install PREFIX=/usr HTTPDUSER=apache
    cp confs/apache/mmc.conf /etc/httpd/conf/webapps.d/
fi
if [ $DISTRIBUTION == "Debian" ]; then
    make install PREFIX=/usr HTTPDUSER=www-data
    cp confs/apache/mmc.conf /etc/apache2/conf.d/
fi
popd

if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    if [ $RELEASE == "2010.0" ];
    then
        # Download and setup SQLAlchemy 0.4.8
	wget "http://switch.dl.sourceforge.net/project/sqlalchemy/sqlalchemy/0.4.8/SQLAlchemy-0.4.8.tar.gz"
	tar xzf SQLAlchemy-0.4.8.tar.gz
	pushd SQLAlchemy-0.4.8
	python setup.py install
	popd
    fi
fi

popd

# MySQL setup
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    service mysqld stop
    sed -i "s/^skip-networking/#skip-networking/" /etc/my.cnf
    service mysqld start
fi
if [ $DISTRIBUTION == "Debian" ]; then
    invoke-rc.d mysql stop
    sed -i "s/^skip-networking/#skip-networking/" /etc/mysql/my.cnf
    invoke-rc.d mysql start
fi
# Wait for MySQL to start
sleep 5

# Setup LDAP
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    rm -f /etc/openldap/schema/*
    touch /etc/openldap/schema/local.schema
    cp $TMPCO/mmc-core/agent/contrib/ldap/mmc.schema $TMPCO/mmc-core/agent/contrib/ldap/mail.schema $TMPCO/mmc-core/agent/contrib/ldap/openssh-lpk.schema $TMPCO/mmc-core/agent/contrib/ldap/quota.schema $TMPCO/mmc-core/agent/contrib/ldap/dhcp.schema /etc/openldap/schema/
    /usr/share/openldap/scripts/mandriva-dit-setup.sh -d mandriva.com -p secret -y
    sed -i 's/cn=admin/uid=LDAP Admin,ou=System Accounts/' /etc/mmc/plugins/base.ini

    sed -i 's!#include.*/etc/openldap/schema/local.schema!include /etc/openldap/schema/local.schema!g' /etc/openldap/slapd.conf
    sed -i '/.*kolab.schema/d' /etc/openldap/slapd.conf
    sed -i '/.*misc.schema/d' /etc/openldap/slapd.conf
    # Shipped dhcp.schema is too old
    sed -i '/.*dhcp.schema/d' /etc/openldap/slapd.conf
    sed -i 's/@inetLocalMailRecipient,//' /etc/openldap/mandriva-dit-access.conf

    echo "include /etc/openldap/schema/mmc.schema" > /etc/openldap/schema/local.schema
    echo "include /etc/openldap/schema/dhcp.schema" >> /etc/openldap/schema/local.schema

fi

if [ $DISTRIBUTION == "Debian" ]; then
    touch /etc/ldap/schema/local.schema
    cp $TMPCO/mmc-core/agent/contrib/ldap/mmc.schema $TMPCO/mmc-core/agent/contrib/ldap/mail.schema $TMPCO/mmc-core/agent/contrib/ldap/openssh-lpk.schema $TMPCO/mmc-core/agent/contrib/ldap/quota.schema $TMPCO/mmc-core/agent/contrib/ldap/samba.schema $TMPCO/mmc-core/agent/contrib/ldap/dhcp.schema $TMPCO/mmc-core/agent/contrib/ldap/dnszone.schema /etc/ldap/schema/
    grep -q '/etc/ldap/schema/local.schema' /etc/ldap/slapd.conf || sed -i -e '/inetorgperson.schema$/a include /etc/ldap/schema/local.schema' /etc/ldap/slapd.conf
    echo "include /etc/ldap/schema/mmc.schema" > /etc/ldap/schema/local.schema
fi

# Setup ppolicy
if [ $RELEASE == "2010.0" -o $RELEASE == "5.0.4" ];
    then
    sed -i "s/disable = 1/disable = 0/" /etc/mmc/plugins/ppolicy.ini
fi

# Restart LDAP & APACHE
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    service ldap restart
    service httpd restart
fi
if [ $DISTRIBUTION == "Debian" ]; then
    invoke-rc.d slapd restart
    invoke-rc.d apache2 restart
fi

# Recreate log directory
rm -fr /var/log/mmc; mkdir /var/log/mmc

# Recreate archives directory
rm -fr /home/archives; mkdir -p /home/archives

# Remove default LDAP password policies because the MMC agent will add one
if [ $DISTRIBUTION == "MandrivaLinux" ]; then
    ldapdelete -x -h 127.0.0.1 -D "uid=LDAP Admin,ou=System Accounts,dc=mandriva,dc=com" -w secret "cn=default,ou=Password Policies,dc=mandriva,dc=com"
fi

# Disable passmod on CS4, because it doesn't work
if [ $RELEASE == "2006.0" ];
    then
    sed -i "s/passwordscheme = passmod/passwordscheme = ssha/" /etc/mmc/plugins/base.ini
fi


# Setup MMC audit framework
cat >> /etc/mmc/plugins/base.ini << EOF

[audit]
method = database
dbhost = localhost
dbdriver = mysql
dbport = 3306
dbuser = audit
dbpassword = audit
dbname = audit
EOF

mmc-helper audit create | mysql
mmc-helper audit init | mysql
mmc-helper audit check

# Start MMC agent
/etc/init.d/mmc-agent start

>>>>>>> old-project/merge_into_pulse
if [ ! -z $TMPREMOVE ];
    then
    rm -fr $TMPCO
fi

echo "Installation done successfully"
exit 0
