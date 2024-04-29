#!/bin/bash -e

#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id: uninstall.sh 4915 2009-12-22 15:07:58Z cdelfosse $
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

echo "Medulla 2 auto-uninstallation script"

if [ -z $FORCE ];
    then
    echo
    echo "WARNING: this script will erase some parts of your configuration !"
    echo "         type Ctrl-C now to exit if you are not sure"
    echo "         type Enter to continue"
    read
fi

[ -f /etc/init.d/medulla-scheduler ] && /etc/init.d/medulla-scheduler stop || true
[ -f /etc/init.d/medulla-launchers ] && /etc/init.d/medulla-launchers stop || true
[ -f /etc/init.d/medulla-package-server ] && /etc/init.d/medulla-package-server stop || true
[ -f /etc/init.d/medulla-imaging-server ] && /etc/init.d/medulla-imaging-server stop || true
[ -f /etc/init.d/medulla-inventory-server ] && /etc/init.d/medulla-inventory-server stop || true

# DROP databases
if [ -f /usr/bin/mysql ];
    then
    echo "drop database if exists medulla" | mysql
    echo "drop database if exists msc" | mysql
    echo "drop database if exists dyngroup" | mysql
    echo "drop database if exists inventory" | mysql
    echo "drop database if exists imaging" | mysql
    echo "drop user mmc@localhost" | mysql || true
fi

rm -fr $PREFIX/lib/python2.*/site-packages/medulla
rm -f /etc/init.d/medulla-*
rm -f $PREFIX/sbin/medulla-*
rm -fr /var/lib/medulla/packages/*-*-*-*-* /var/lib/medulla/imaging
rm -fr /var/lib/medulla/qactions
rm -fr /tmp/package_tmp

# GLPI
rm -fr /var/www/html/glpi

exit 0
