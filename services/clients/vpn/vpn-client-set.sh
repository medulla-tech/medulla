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
fqdn=$( hostname )
# VPN global variables
. $PREFIX_DIR/vpn-variables
account_name="pulse2connection"

if [ $VPN_OS == "osx" ]; then
        # need to install tun/tap driver 
	if [ ! -f "$PREFIX_DIR/$VPN_TUNTAP_DRIVER_ARCHIVE" ]; then
	    echo "Install pack $VPN_TUNTAP_DRIVER_ARCHIVE not exists, try to download it..."
	    curl -o $PREFIX_DIR/$VPN_TUNTAP_DRIVER_ARCHIVE $VPN_URL_ROOT/$VPN_TUNTAP_DRIVER_ARCHIVE
	fi 

	tar xvzf $PREFIX_DIR/$VPN_TUNTAP_DRIVER_ARCHIVE -C $PREFIX_DIR
        /usr/sbin/installer -pkg $VPN_TUNTAP_DRIVER_NAME -target /
        nic_name="vpn0"
fi

if [ $VPN_OS == "linux" ]; then
        nic_name="0"
fi

$VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost /CLIENT /CMD:NicCreate $nic_name 
#$VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost /CLIENT /CMD:AccountCreate $account_name 

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost /CLIENT /CMD:AccountCreate $account_name 
    sleep 1
    expect \"Destination VPN Server Host Name and Port Number:\n\"
    send $VPN_SERVER_HOST:$VPN_SERVER_PORT\r
    expect \"Destination Virtual Hub Name:\n\"
    send $VPN_PULSE_HUB\r
    expect \"Connecting User Name:\n\"
    send $VPN_SERVER_USER\r
    expect \"Used Virtual Network Adapter Name:\n\"
    send $nic_name\r
    expect eof"

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost /CLIENT /CMD:AccountPasswordSet $account_name 
    sleep 1
    expect \"Password:\n\"
    send $VPN_SERVER_PASSWORD\r
    expect \"Confirm input:\n\"
    send $VPN_SERVER_PASSWORD\r
    expect \"Specify standard or radius:\n\"
    send standard\r
    expect eof"

if [ $VPN_OS == "linux" ]; then
    # enable IPv4 forwarding
    echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/ipv4_forwarding.conf
    # apply sysctl
    sysctl --system
    dhclient vpn_0
fi

$VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost /CLIENT /CMD:AccountConnect $account_name
$VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost /CLIENT /CMD:AccountStatusGet $account_name

 
