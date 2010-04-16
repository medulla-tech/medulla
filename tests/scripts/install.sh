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

export LANG=C
export LC_ALL=C

echo "MMC CORE basic auto-installation script"
echo

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
        PKGS="$PKGS lib${ARCH}python2.5-devel libldap2.4_2-devel python-setuptools"
        fi
        if [ $RELEASE == "2010.0" ]; 
            then
            # The python-sqlalchemy lib must be installed manually because we are
            # compatible only with version 0.4, and 2010.0 provides version 0.5.
            PKGS="$PKGS lib${ARCH}python2.6-devel lib${ARCH}crack2-python libldap2.4_2-devel python-setuptools"
        fi
    fi
    if [ $DISTRIBUTION == "Debian" ]; then
        if [ $RELEASE == "5.0.4" ]; then
            PKGS="$PKGS python2.5-dev libldap2-dev python-setuptools"
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
    urpmi --auto --no-suggests $PKGS
    rpm -q $PKGS
fi
if [ $DISTRIBUTION == "Debian" ]; then
    apt-get install --yes $PKGS
    dpkg -l $PKGS
fi

if [ -z $TMPCO ];
    then
    TMPCO=`mktemp -d`
    TMPREMOVE=1
    pushd $TMPCO
    # Check out MMC CORE
    svn co http://mds.mandriva.org/svn/mmc-projects/mmc-core/trunk mmc-core
else
    pushd $TMPCO
fi

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

# Download and setup SQLAlchemy 0.4.8
wget "http://downloads.sourceforge.net/project/sqlalchemy/sqlalchemy/0.4.8/SQLAlchemy-0.4.8.tar.gz?use_mirror=switch"
tar xzf SQLAlchemy-0.4.8.tar.gz
pushd SQLAlchemy-0.4.8
python setup.py install
popd

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
    cp $TMPCO/mmc-core/agent/contrib/ldap/mmc.schema $TMPCO/mmc-core/agent/contrib/ldap/mail.schema $TMPCO/mmc-core/agent/contrib/ldap/openssh-lpk.schema $TMPCO/mmc-core/agent/contrib/ldap/quota.schema /etc/openldap/schema/
    /usr/share/openldap/scripts/mandriva-dit-setup.sh -d mandriva.com -p secret -y
    sed -i 's/cn=admin/uid=LDAP Admin,ou=System Accounts/' /etc/mmc/plugins/base.ini

    sed -i 's!#include.*/etc/openldap/schema/local.schema!include /etc/openldap/schema/local.schema!g' /etc/openldap/slapd.conf
    sed -i '/.*kolab.schema/d' /etc/openldap/slapd.conf
    sed -i '/.*misc.schema/d' /etc/openldap/slapd.conf
    sed -i 's/@inetLocalMailRecipient,//' /etc/openldap/mandriva-dit-access.conf

    echo "include /etc/openldap/schema/mmc.schema" >> /etc/openldap/schema/local.schema
fi
if [ $DISTRIBUTION == "Debian" ]; then
    touch /etc/ldap/schema/local.schema
    cp $TMPCO/mmc-core/agent/contrib/ldap/mmc.schema $TMPCO/mmc-core/agent/contrib/ldap/mail.schema $TMPCO/mmc-core/agent/contrib/ldap/openssh-lpk.schema $TMPCO/mmc-core/agent/contrib/ldap/quota.schema /etc/ldap/schema/
    grep -q '/etc/ldap/schema/local.schema' /etc/ldap/slapd.conf
    if [ $? -ne 0 ]; then
        sed -i -e '/inetorgperson.schema$/a include /etc/ldap/schema/local.schema' /etc/ldap/slapd.conf
        echo "include /etc/ldap/schema/mmc.schema" > /etc/ldap/schema/local.schema
    fi
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
host = localhost
driver = mysql
port = 3306
user = audit
password = audit
base = audit
EOF

mmc-helper audit create | mysql
mmc-helper audit init | mysql
mmc-helper audit check

# Start MMC agent
/etc/init.d/mmc-agent start

if [ ! -z $TMPREMOVE ];
    then
    rm -fr $TMPCO
fi

echo "Installation done successfully"
exit 0
