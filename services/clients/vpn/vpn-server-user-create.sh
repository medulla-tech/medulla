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
USR_PASSWORD="linbox"

# VPN global variables
. $PREFIX_DIR/vpn-variables

username=$1
password=$2

usage(){
    echo "Creates a new user in SoftEther VPN server"
    echo
    echo "Usage:" 
    echo "  $0 username password"
    echo
    exit 0
}

if [ -z "$username" ]; then
    usage
fi
if [ -z "$password" ]; then
    usage
fi



expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:443 /SERVER /HUB:$VPN_PULSE_HUB /CMD:UserCreate $username
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect \"Assigned Group Name:\n\"
    send $VPN_PULSE_GROUP\r
    expect \"User Full Name:\n\"
    send $username\r
    expect \"User Description:\n\"
    send $username\r
    expect eof"
echo "----- user $username successfully created ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:443 /SERVER /HUB:$VPN_PULSE_HUB /CMD:UserPasswordSet $username
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect \"Password:\n\"
    send $password\r
    expect \"Confirm input:\n\"
    send $password\r
    expect eof"
echo "----- password for $username successfully set ----- "


