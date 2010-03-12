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
    # LDAP stuff
    PKGS="$PKGS openldap-servers openldap-mandriva-dit"

    # Python
    PKGS="$PKGS python-twisted-web python-ldap"

    # Apache/PHP
    PKGS="$PKGS apache-mpm-prefork apache-mod_php php-gd php-iconv php-xmlrpc gettext"

    # Development & install
    PKGS="$PKGS subversion make gcc wget"

    if [ $RELEASE == "2006.0" ];
        then
        PKGS="$PKGS lib${ARCH}python2.4-devel libldap2.3_0-devel"
    fi
    if [ $RELEASE == "2010.0" -o $RELEASE == "2009.0" ];
        then
        # The python-sqlalchemy lib must be installed manually because we are
        # compatible only with version 0.4, and 2010.0 provides version 0.5.
        PKGS="$PKGS lib${ARCH}python2.6-devel lib${ARCH}crack2-python libldap2.4_2-devel python-setuptools"
    fi

    # MySQL
    PKGS="$PKGS mysql mysql-client"
    if [ $RELEASE == "2010.0" -o $RELEASE == "2009.0" ];
        then
        PKGS="$PKGS python-mysql"
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
urpmi --auto --no-suggests $PKGS
rpm -q $PKGS

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
make install PREFIX=/usr HTTPDUSER=apache
cp confs/apache/mmc.conf /etc/httpd/conf/webapps.d/
popd

# Download and setup SQLAlchemy 0.8
wget "http://downloads.sourceforge.net/project/sqlalchemy/sqlalchemy/0.4.8/SQLAlchemy-0.4.8.tar.gz?use_mirror=switch"
tar xzf SQLAlchemy-0.4.8.tar.gz
pushd SQLAlchemy-0.4.8
python setup.py install
popd

popd

# MySQL setup
/etc/init.d/mysqld stop
sed -i "s/^skip-networking/#skip-networking/" /etc/my.cnf
/etc/init.d/mysqld start
# Wait for MySQL to start
sleep 5

# Setup LDAP
rm -f /etc/openldap/schema/*
touch /etc/openldap/schema/local.schema
cp $TMPCO/mmc-core/agent/contrib/ldap/mmc.schema $TMPCO/mmc-core/agent/contrib/ldap/mail.schema $TMPCO/mmc-core/agent/contrib/ldap/openssh-lpk.schema /etc/openldap/schema/
/usr/share/openldap/scripts/mandriva-dit-setup.sh -d mandriva.com -p secret -y
sed -i 's/cn=admin/uid=LDAP Admin,ou=System Accounts/' /etc/mmc/plugins/base.ini

sed -i 's!#include.*/etc/openldap/schema/local.schema!include /etc/openldap/schema/local.schema!g' /etc/openldap/slapd.conf
sed -i '/.*kolab.schema/d' /etc/openldap/slapd.conf
sed -i '/.*misc.schema/d' /etc/openldap/slapd.conf
sed -i 's/@inetLocalMailRecipient,//' /etc/openldap/mandriva-dit-access.conf

echo "include /etc/openldap/schema/mmc.schema" >> /etc/openldap/schema/local.schema

# Setup ppolicy
if [ $RELEASE == "2010.0" ];
    then
    sed -i "s/disable = 1/disable = 0/" /etc/mmc/plugins/ppolicy.ini
fi

# Restart LDAP & APACHE
service ldap restart
service httpd restart

# Recreate log directory
rm -fr /var/log/mmc; mkdir /var/log/mmc

# Recreate archives directory
rm -fr /home/archives; mkdir -p /home/archives

# Remove default LDAP password policies because the MMC agent will add one
ldapdelete -x -h 127.0.0.1 -D "uid=LDAP Admin,ou=System Accounts,dc=mandriva,dc=com" -w secret "cn=default,ou=Password Policies,dc=mandriva,dc=com"

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
