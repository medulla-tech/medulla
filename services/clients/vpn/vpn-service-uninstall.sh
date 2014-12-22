#!/bin/bash
#
# (c) 2014 Mandriva, http://www.mandriva.com
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


PWD=$( pwd )
PREFIX_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# VPN global variables
. $PREFIX_DIR/vpn-variables

echo "INFO: Stopping the daemon $VPN_START_UP ..."
service $VPN_SERVICE_NAME stop


echo "INFO: Uninstall the daemon service $VPN_START_UP ..."
update-rc.d -f $VPN_SERVICE_NAME remove
rm -f $VPN_START_UP

if [ -d "$VPN_PROG_DIR/$VPN_INST_DIR" ]; then
    echo "INFO: Erasing old folder $VPN_PROG_DIR/$VPN_INST_DIR ..."
    rm -rf $VPN_PROG_DIR/$VPN_INST_DIR
fi
echo "INFO: Remove $VPN_VPNCMD_PATH ..."
rm -f $VPN_VPNCMD_PATH


echo "Done."
