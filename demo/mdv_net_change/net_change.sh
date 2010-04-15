#!/bin/sh

NETTYPE=$1

if [ "x$NETTYPE" != "xnat" -a "x$NETTYPE" != "xbridge" ]; then
	echo "you have to choose betwen 'nat' and 'bridge'"
	exit;
fi
echo "network kind : $NETTYPE"
for i in `find $NETTYPE -type f`; do
	j=`echo $i | sed -e "s/$NETTYPE//"`
	cp -f "$i" "$j"
done

if [ "x$NETTYPE" == "xnat" ]; then
	echo <<EOL
you have to add the following in your vmware dhcpd.conf file
------------------------------------------------------------
    next-server <the pulse2 server IP>;
    filename "/bootloader/pxe_boot";
------------------------------------------------------------
EOL
	service dhcpd stop
	service network restart
elif [ "x$NETTYPE" == "xbridge" ]; then
	service network restart
	service dhcpd start
fi




