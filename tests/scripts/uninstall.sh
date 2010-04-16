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

PREFIX=/usr

echo "MMC CORE auto-uninstallation script"

if [ -z $FORCE ];
    then
    echo
    echo "WARNING: this script will erase some parts of your configuration !"
    echo "         type Ctrl-C now to exit if you are not sure"
    echo "         type Enter to continue"
    read
fi

if [ -f '/etc/mandriva-release' ]; then
    service mmc-agent force-stop || true
elif [ -f '/etc/debian_version' ]; then
    invoke-rc.d mmc-agent force-stop || true
fi

rm -f /var/run/mmc-agent.pid

if which mmc-helper; then
    mmc-helper audit droptables || true
    mmc-helper audit drop | mysql
fi

rm -fr /etc/mmc*
rm -f /etc/init.d/mmc-agent $PREFIX/sbin/mmc-agent

rm -fr $PREFIX/lib/python2.*/site-packages/mmc
rm -fr $PREFIX/share/mmc $PREFIX/lib/mmc
rm -f $PREFIX/bin/mmc-*
rm -fr /var/lib/ldap.*

if [ -f '/etc/mandriva-release' ]; then
    rm -f /usr/lib*/openldap/mmc-check-password.so
    rm -fr /etc/openldap/slapd.conf.*
    rm -fr /etc/openldap/schema/local.schema
fi
if [ -f '/etc/debian_version' ]; then
    rm -f /usr/lib/ldap/mmc-check-password.so
    rm -fr /etc/ldap/slapd.conf.*
    rm -fr /etc/ldap/schema/local.schema
fi

echo "Uninstallation done"
exit 0
