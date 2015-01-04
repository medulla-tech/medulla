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



if [ ! -f "`which make`" ]; then
    echo "WARNING: You should install the make and build-essential tools."
    echo "INFO: Please type 'apt-get install build-essential' to install it."
    exit 1;
fi

if [ ! -f "$PREFIX_DIR/$VPN_ARCHIVE_NAME" ]; then
    echo "Install pack $VPN_ARCHIVE_NAME not exists, try to download it from $VPN_URL"
    curl -o $PREFIX_DIR/$VPN_ARCHIVE_NAME $VPN_URL_ROOT/$VPN_ARCHIVE_NAME
fi 


if [ -d "$PREFIX_DIR/$VPN_INST_DIR" ]; then
    echo "INFO: Erasing previous install folder $PREFIX_DIR/$VPN_INST_DIR ..."
    rm -rf $PREFIX_DIR/$VPN_INST_DIR
fi

if [ -d "$VPN_PROG_DIR/$VPN_INST_DIR" ]; then
    echo "INFO: Erasing old folder $VPN_PROG_DIR/$VPN_INST_DIR ..."
    rm -rf $VPN_PROG_DIR/$VPN_INST_DIR
fi

tar xvzf $PREFIX_DIR/$VPN_ARCHIVE_NAME -C $PREFIX_DIR

cd $PREFIX_DIR/$VPN_INST_DIR

echo "INFO: Preparation of $SERVICE_NAME installer ..."
# "make" command requests some license confirmations ...
expect -c "
    log_user $VPN_LOG_EXPECT 
    set timeout 1
    spawn make
    sleep 1
    expect \"Please choose one of above number:\n\"
    send 1\r
    expect \"Please choose one of above number:\n\"
    send 1\r
    expect \"Please choose one of above number:\n\"
    send 1\r
    expect eof"


if [ ${?} -eq 0 ]; then
    echo "INFO: succeffully processed"
else
    echo "WARNING: The preparation of VPN Server installer failed"
    exit 1;
fi     

cd ..
echo "INFO: Moving the prepared folder $VPN_INST_DIR to $VPN_PROG_DIR ..."
mv $VPN_INST_DIR $VPN_PROG_DIR

echo "INFO: Set the rights..."
sleep 2
chmod 600 $VPN_PROG_DIR/$VPN_INST_DIR/* 
chmod 700 $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd 
chmod 700 $VPN_PROG_DIR/$VPN_INST_DIR/$VPN_SERVICE_NAME 

if [[ $VPN_OS == "linux" ]]; then
	echo "INFO: Registering a startup script"

	echo "#!/bin/bash
### BEGIN INIT INFO
# Provides: $VPN_SERVICE_NAME"  > $VPN_START_UP
	echo '# Required-Start: $local_fs $yslog
# Required-Stop: $local_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: VPN Service for Pulse2 server
# Description: VPN Service for Pulse2 server
### END INIT INFO
	' >> $VPN_START_UP
	echo "DAEMON=$VPN_PROG_DIR/$VPN_INST_DIR/$VPN_SERVICE_NAME" >> $VPN_START_UP
	echo "LOCK=/var/run/lock/$VPN_SERVICE_NAME" >> $VPN_START_UP

	# Create the daemon
	echo '
test -x $DAEMON || exit 0
case "$1" in
  start)
    $DAEMON start
    touch $LOCK
    sleep 1' >> $VPN_START_UP
	if [[ $VPN_SERVICE_SIDE == "server" ]]; then 
	    echo "/sbin/ifconfig $VPN_TAP_IFACE $VPN_TAP_ADDRESS" >> $VPN_START_UP
	fi    
	echo '  ;;
  stop)
    $DAEMON stop
    rm $LOCK
    sleep 1' >> $VPN_START_UP
	if [[ $VPN_SERVICE_SIDE == "server" ]]; then 
	    echo "/sbin/ifconfig $VPN_TAP_IFACE $VPN_TAP_ADDRESS" >> $VPN_START_UP
	fi
	echo '  ;;
  restart)
    $DAEMON stop
    sleep 3
    $DAEMON start
  ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
esac
exit 0
	' >> $VPN_START_UP

	chmod 755 $VPN_START_UP

	echo "#!/bin/bash" > $VPN_VPNCMD_PATH 
	echo "cd $VPN_PROG_DIR/$VPN_INST_DIR" >> $VPN_VPNCMD_PATH
	echo "$VPN_PROG_DIR/$VPN_INST_DIR/vpncmd" >> $VPN_VPNCMD_PATH

	chmod 700 $VPN_VPNCMD_PATH 

	#ln -s $VPN_PROG_DIR/$VPN_INST_DIR/vpncmd /usr/bin

	# Start up on boot
	update-rc.d $VPN_SERVICE_NAME defaults

	if [[ $VPN_SERVICE_SIDE == "server" ]]; then 
            
            # Configure DNS & DHCP service 		
	    echo "interface=${VPN_TAP_INTERFACE}" >> /etc/dnsmasq.conf
	    echo "dhcp-range=${VPN_TAP_INTERFACE},${VPN_DHCP_RANGE},${VPN_DHCP_LEASE}h" >> /etc/dnsmasq.conf
	    echo "dhcp-option=${VPN_TAP_INTERFACE},${VPN_TAP_ADDRESS}" >> /etc/dnsmasq.conf

	    # enable IPv4 forwarding
	    echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/ipv4_forwarding.conf

	    # apply sysctl
	    sysctl --system

            iptables -t nat -A POSTROUTING -s $VPN_TAP_LAN -j SNAT --to-source $VPN_SERVER_PUBLIC_IP 
	    apt-get install iptables-persistent
        fi

	# Start the service
	service $VPN_SERVICE_NAME start
	service dnsmasq start
fi

