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
fqdn=$( hostname )

# VPN global variables
. $PREFIX_DIR/vpn-variables

if [ ! -f "`which dnsmasq`" ]; then
    echo "WARNING: You should install a DNS service."
    echo "INFO: Please type 'apt-get install dnsmasq' to install it."
    exit 1;
fi

if [[ -n $( netstat -anp | grep LISTEN | grep ":$VPN_SERVER_PORT" | grep -v $VPN_SERVICE_NAME ) ]]; then
    echo "WARNING: Port ${VPN_SERVER_PORT} already in use."
    exit 1;    
fi	

$VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:ServerPasswordSet $VPN_ADMIN_PASSWORD
echo "----- set password ok ----- "
expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:HubCreate $VPN_PULSE_HUB
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect \"Confirm input:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect eof"
echo "----- create hub ok ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:BridgeCreate $VPN_PULSE_HUB /DEVICE:$VPN_TAP_IFACE /TAP:yes
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect eof"
echo "----- create bridge ok ----- "

# Configure DNS & DHCP service 		
echo "interface=tap_${VPN_TAP_IFACE}" >> /etc/dnsmasq.conf
echo "dhcp-range=tap_${VPN_TAP_IFACE},${VPN_DHCP_RANGE},${VPN_DHCP_LEASE}h" >> /etc/dnsmasq.conf
#echo "dhcp-option=tap_${VPN_TAP_IFACE},3,${VPN_TAP_ADDRESS}" >> /etc/dnsmasq.conf
echo "dhcp-option=tap_${VPN_TAP_IFACE},3" >> /etc/dnsmasq.conf
echo "dhcp-option=tap_${VPN_TAP_IFACE},121,${VPN_TAP_LAN},${VPN_TAP_ADDRESS}" >> /etc/dnsmasq.conf

# enable IPv4 forwarding
echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/ipv4_forwarding.conf

# apply sysctl
sysctl --system

iptables -t nat -A POSTROUTING -s $VPN_TAP_LAN -j SNAT --to-source $VPN_SERVER_PUBLIC_IP 
#apt-get install iptables-persistent

# uncomment the ifconfig tap_soft clause in /etc/init.d/vpnserver
sed -i 's/#\ ifconfig/ifconfig/g' $VPN_START_UP
service $VPN_SERVICE_NAME restart
service dnsmasq restart


expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /HUB:$VPN_PULSE_HUB /CMD:GroupCreate $VPN_PULSE_GROUP
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect \"Group Full Name:\n\"
    send \r
    expect \"Group Description:\n\"
    send \r
    expect eof"
echo "----- group create ok ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:IPSecEnable
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect \"Enable L2TP over IPsec Server Function (yes / no):\n\"
    send yes\r
    expect \"Enable Raw L2TP Server Function (yes / no):\n\"
    send yes\r
    expect \"Enable EtherIP / L2TPv3 over IPsec Server Function (yes / no):\n\"
    send yes\r
    expect \"Pre Shared Key for IPsec (Recommended: 9 letters at maximum):\n\"
    send $VPN_PRE_SHARED_KEY\r
    expect \"Default Virtual HUB in a case of omitting the HUB on the Username:\n\"
    send $VPN_PULSE_HUB\r
    expect eof"
echo "----- IPSec ok ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:ServerCertRegenerate $fqdn
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect eof"
echo "----- ServerCertRegenerate for $fqdn ok ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:ServerCertGet $VPN_CRT_PATH
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect eof"
echo "----- ServerCertGet to $VPN_CRT_PATH ok ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:SstpEnable yes
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect eof"
echo "----- SstpEnable ok ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:OpenVpnEnable yes /PORTS:1194
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect eof"
echo "----- OpenVpnEnable ok ----- "

expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd localhost:$VPN_SERVER_PORT /SERVER /CMD:OpenVpnMakeConfig $VPN_OPENVPN_CONFIG_ARCHIVE
    sleep 1
    expect \"Password:\n\"
    send $VPN_ADMIN_PASSWORD\r
    expect eof"
echo "----- OpenVpnMakeConfig save ok ----- "


