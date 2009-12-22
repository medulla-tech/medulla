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
    PKGS="$PKGS lib${ARCH}python2.6-devel python-twisted-web python-ldap \
          python-sqlalchemy lib${ARCH}crack2-python"

    # Apache/PHP
    PKGS="$PKGS apache-mpm-prefork apache-mod_php php-gd php-iconv php-xmlrpc gettext"

    # Development & install
    PKGS="$PKGS subversion make gcc libldap2.4_2-devel"
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

pushd mmc-core/agent
make install PREFIX=/usr
popd

pushd mmc-core/web
make install PREFIX=/usr HTTPDUSER=apache
cp confs/apache/mmc.conf /etc/httpd/conf/webapps.d/
popd


popd

# Setup LDAP
rm -f /etc/openldap/schema/*
cp $TMPCO/mmc-core/agent/contrib/ldap/mmc.schema $TMPCO/mmc-core/agent/contrib/ldap/mail.schema $TMPCO/mmc-core/agent/contrib/ldap/openssh-lpk.schema /etc/openldap/schema/
/usr/share/openldap/scripts/mandriva-dit-setup.sh -d mandriva.com -p secret -y
sed -i 's/cn=admin/uid=LDAP Admin,ou=System Accounts/' /etc/mmc/plugins/base.ini

sed -i 's!#include.*/etc/openldap/schema/local.schema!include /etc/openldap/schema/local.schema!g' /etc/openldap/slapd.conf
sed -i '/.*kolab.schema/d' /etc/openldap/slapd.conf
sed -i '/.*misc.schema/d' /etc/openldap/slapd.conf
sed -i 's/@inetLocalMailRecipient,//' /etc/openldap/mandriva-dit-access.conf

rm -f /etc/openldap/schema/local.schema
echo "include /etc/openldap/schema/mmc.schema" >> /etc/openldap/schema/local.schema

# Setup ppolicy
sed -i "s/disable = 1/disable = 0/" /etc/mmc/plugins/ppolicy.ini

# Restart LDAP & APACHE
service ldap restart
service httpd restart

# Recreate log directory
rm -fr /var/log/mmc; mkdir /var/log/mmc

# Recreate archives directory
rm -fr /home/archives; mkdir -p /home/archives

# Start MMC agent
# Remove default LDAP password policies because the MMC agent will add one
ldapdelete -h 127.0.0.1 -D "uid=LDAP Admin,ou=System Accounts,dc=mandriva,dc=com" -w secret "cn=default,ou=Password Policies,dc=mandriva,dc=com"
service mmc-agent restart

if [ ! -z $TMPREMOVE ];
    then
    rm -fr $TMPCO
fi

echo "Installation done successfully"
exit 0
