#!/bin/sh

# urpmi screen
#

VERSION='trunk'
if [ "x$1" != "x" ]; then VERSION=$1; fi

############ install code
urpmi lsb-release
urpmi --force svn
wget http://mds.mandriva.org/svn/mmc-projects/pulse2/server/trunk/tests/scripts/bootstrap.sh
sh bootstrap.sh

############ install files and configuration
FILEDIR='cs4demo'

svn export http://pulse2.mandriva.org/svn/pulse2-build-tools/branches/build_mandriva/build_vmware_image/cs4demo/ $FILEDIR

# get the documentation files that correspond to the wanted version
if [ "x$VERSION" != "xtrunk" ]; then
    TAG=`echo $VERSION | sed -e 's/\./_/g'`
    svn export https://pulse2.mandriva.org/svn/pulse2-doc/tags/PULSE_$TAG/user pulse2-doc
    cp -f pulse2-doc/Pulse2-Manual-$VERSION* $FILEDIR/home/guest/Desktop/
    cp -f pulse2-doc/Pulse2-Manual-$VERSION* /var/www/html/
    NAMEFR=`ls pulse2-doc/Pulse2-Manual-$VERSION*-FR.pdf | tail -n 1 | xargs basename`
    NAMEEN=`ls pulse2-doc/Pulse2-Manual-$VERSION*-EN.pdf | tail -n 1 | xargs basename`
else
    svn export http://mds.mandriva.org/svn/mmc-projects/pulse2/server/trunk/doc/user pulse2-doc
    cp -f pulse2-doc/Pulse2-Manual-* $FILEDIR/home/guest/Desktop/
    cp -f pulse2-doc/Pulse2-Manual-* /var/www/html/
    NAMEFR=`ls pulse2-doc/Pulse2-Manual-*-FR.pdf | tail -n 1 | xargs basename`
    NAMEEN=`ls pulse2-doc/Pulse2-Manual-*-EN.pdf | tail -n 1 | xargs basename`
fi

cp $FILEDIR/var/www/html/index.html /var/www/html/index.html.bkp -f
perl -e "
while (<>) {
    if (/Pulse 2 manuel en Fr/) {
        s/Pulse2-Manual-.*?.pdf/$NAMEFR/g;
        print;
    } elsif (/Pulse 2 manual in En/) {
        s/Pulse2-Manual-.*?.pdf/$NAMEEN/g;
        print;
    } else {
        print;
    }
}" /var/www/html/index.html.bkp > /var/www/html/index.html
rm -f /var/www/html/index.html.bkp

# do mysql stuff
perl -pi -e 's/skip-networking/#skip-networking/' /etc/my.cnf
service mysqld restart
sleep 10 # let some time for mysql to start

#
mkdir -p /var/lib/pulse2/packages /var/lib/pulse2/downloads /tmp/package_tmp/put

# prepare files
cat /etc/mmc/pulse2/launchers/launchers.ini | \
    sed -e 's/# username =.*/username =/' | \
    sed -e 's/# password =.*/password =/' | \
    sed -e 's/# tcp_sproxy_host =/tcp_sproxy_host = ##IPADDR##/' > cs4demo/etc/mmc/template/etc/mmc/pulse2/launchers/launchers.ini

cat /etc/mmc/pulse2/package-server/package-server.ini | \
    sed -e 's/^host =.*/host = ##IPADDR##/' | \
    sed -e 's/mount_point = \/mirror1/mount_point = \/mirror/' | \
    sed -e 's/mount_point = \/package_api_get1/mount_point = \/package_api_put/' | \
    sed -e 's/tmp_input_dir = \/tmp\/package_tmp\/put1/tmp_input_dir = \/tmp\/package_tmp\/put/' > cs4demo/etc/mmc/template/etc/mmc/pulse2/package-server/package-server.ini

cat /etc/mmc/plugins/base.ini | \
    sed -e 's/#\[provisioning\]/[provisioning]/' | \
    sed -e 's/#method = externalldap/method = inventory/' | \
    sed -e 's/# \[userdefault\]/[userdefault]\nobjectClass = +lmcUserObject\nlmcProfile = default/' | \
    sed -e 's/\[audit\]/#[audit]/' > cs4demo/etc/mmc/template/etc/mmc/plugins/base.ini

perl -pi -e 's/# username = .*/username =/; s/# password =.*/password =/; s/username =.*/username =/; s/password =.*/password =/' /etc/mmc/pulse2/scheduler/scheduler.ini

cp -rf cs4demo/etc/mmc/template /etc/mmc/
cp -rf cs4demo/etc/mmc/live_template.sh /etc/mmc/
head -n 7 cs4demo/etc/sysconfig/network-scripts/ifup.d/mmc-ip > /etc/sysconfig/network-scripts/ifup.d/mmc-ip
perl -pi -e 's/pulse2-launcher /pulse2-launchers /' /etc/sysconfig/network-scripts/ifup.d/mmc-ip
echo "UPDATE ImagingServer SET url = 'https://##IPADDR##:9990/imaging_api' WHERE id = 1;" > /etc/mmc/template/etc/mmc/update_imaging_server.sql
echo "mysql imaging < /etc/mmc/update_imaging_server.sql" >> /etc/sysconfig/network-scripts/ifup.d/mmc-ip
echo '/etc/init.d/pulse2-imaging-server restart' >> /etc/sysconfig/network-scripts/ifup.d/mmc-ip
echo 'fi' >> /etc/sysconfig/network-scripts/ifup.d/mmc-ip
chmod +x /etc/sysconfig/network-scripts/ifup.d/mmc-ip
cp -rf cs4demo/root/* /root/
cp -rf cs4demo/tmp/package_tmp /tmp/
cp -rf cs4demo/usr/share/mmc/license.php /usr/share/mmc/
cp -rf cs4demo/var/lib/pulse2/packages/ff002009/ /var/lib/pulse2/packages/
cp -rf cs4demo/var/www/html/ /var/www/html/
rm -fr /home/guest
cp -rf cs4demo/home/guest /home
chown guest:guest -R /home/guest/

# startup
mkdir -p /home/guest/.icewm
echo """
#!/bin/sh

if [ -f \"\$HOME/.second_start\" ]; then
    firefox&
else
    draklocale&
    touch \"\$HOME/.second_start\"
fi
""" > /home/guest/.icewm/startup
chown guest:guest /home/guest/.icewm -R
chmod +x /home/guest/.icewm/startup

echo """
AUTOLOGIN=yes
USER=guest
EXEC=/usr/bin/startx.autologi
""" > /etc/sysconfig/autologin


# patch some configuration files
perl -pi -e 's/disable = 0/disable = 1/' /etc/mmc/plugins/glpi.ini
perl -pi -e 's/# \[computers\]/[computers]/' /etc/mmc/plugins/base.ini
perl -pi -e 's/# method = inventory/method = inventory/' /etc/mmc/plugins/base.ini
perl -pi -e 's/method = glpi/# method = glpi/' /etc/mmc/plugins/base.ini
perl -pi -e 's/# \[querymanager\]/[querymanager]/' /etc/mmc/plugins/inventory.ini
perl -pi -e 's~# list = Entity/Label\|\|Software/ProductName\|\|Hardware/ProcessorType\|\|Hardware/OperatingSystem\|\|Drive/TotalSpace~list = Entity/Label\|\|Software/ProductName\|\|Hardware/ProcessorType\|\|Hardware/OperatingSystem~' /etc/mmc/plugins/inventory.ini
perl -pi -e 's&# double = Software/Products::Software/ProductName##Software/ProductVersion&double = &' /etc/mmc/plugins/inventory.ini
perl -pi -e 's&# halfstatic = Registry/Value/display name::Path##DisplayName&halfstatic = &' /etc/mmc/plugins/inventory.ini
perl -pi -e 's/PROMPT=.*/PROMPT=NO/' /etc/sysconfig/init
perl -pi -e 's/# default_module =.*/default_module = inventory/' /etc/mmc/plugins/dyngroup.ini
perl -pi -e 's/activate = 0/activate = 1/' /etc/mmc/plugins/dyngroup.ini

mkdir /etc/mmc/template/etc/mmc/pulse2/imaging-server/ -p
cp /etc/mmc/pulse2/imaging-server/imaging-server.ini /etc/mmc/template/etc/mmc/pulse2/imaging-server/ -f
perl -pi -e 's/host =.*/host = ##IPADDR##/' /etc/mmc/template/etc/mmc/pulse2/imaging-server/imaging-server.ini

# patch some files
perl -pi -e 's/canAddComputer/False && canAddComputer/' /usr/share/mmc/modules/base/computers/localSidebar.php

# generate ssh key
#rm -f /root/.ssh/id_dsa*
#ssh-keygen -t dsa -f /root/.ssh/id_dsa -N ""
cp -f /root/.ssh/id_dsa.pub /var/www/html/

# generate agent with the new key
urpmi --force p7zip
sh build_win32-agents.sh

# restart all services
cd /etc/mmc/ && ./live_template.sh

/etc/init.d/httpd restart
/etc/init.d/pulse2-launchers restart
chkconfig --add pulse2-launchers
/etc/init.d/pulse2-scheduler restart
chkconfig --add pulse2-scheduler
/etc/init.d/pulse2-inventory-server restart
chkconfig --add pulse2-inventory-server
/etc/init.d/pulse2-package-server restart
chkconfig --add pulse2-package-server
/etc/init.d/pulse2-imaging-server restart
chkconfig --add pulse2-imaging-server

/etc/init.d/mmc-agent restart
chkconfig --add mmc-agent

## START AGENT and register the package server
pulse2-package-server-register-imaging -m https://mmc:s3cr3t@localhost:7080/mmc -n "Localhost Imaging Server"

## DOC :
# arreter vmware
# modifier le dhcpd de l'interface nat de vmware et ajouter la ligne "next-server <l'ip de la vm pulse>;" dans le tronc principal
#
mv /etc/exports /etc/exports.bkp
svn export http://mds.mandriva.org/svn/mmc-projects/pulse2/server/trunk/services/contrib/imaging-server/exports /etc/exports
#/etc/init.d/nfs-common restart
#/etc/init.d/nfs-server restart

mv /etc/sysconfig/atftpd /etc/sysconfig/atftpd.bkp
echo "
## Path:    Network/FTP/Atftpd
## Description: ATFTP Configuration
## Type:    string
## Default: \"--daemon \"
#
# atftpd options
#
ATFTPD_OPTIONS=\"--daemon \$ATFTPD_OPTIONS\"
ATFTPD_OPTIONS=\"\$ATFTPD_OPTIONS --pidfile /var/run/atftpd/atftpd.pid\"
ATFTPD_OPTIONS=\"\$ATFTPD_OPTIONS --logfile /var/log/mmc/atftpd.log\"
ATFTPD_OPTIONS=\"\$ATFTPD_OPTIONS --user root.root\"

## Type:    yesno
## Default: no
#
# Use inetd instead of daemon
#
ATFTPD_USE_INETD=\"no\"

## Type:    string
## Default: \"/var/lib/tftpboot\"
#
#  TFTP directory must be a world readable/writable directory.
#  By default /tftpboot is assumed.
#
ATFTPD_DIRECTORY=\"/var/lib/pulse2/imaging\"
" > /etc/sysconfig/atftpd
touch /var/log/mmc/atftpd.log
chmod 777 /var/log/mmc/atftpd.log
/etc/init.d/atftpd restart


mv /etc/dhcpd.conf /etc/dhcpd.conf.bkp
echo 'allow booting;
allow bootp;

subnet 172.16.13.0 netmask 255.255.255.0 {
        next-server 172.16.13.136;
        filename "/bootloader/pxe_boot";
}
' > /etc/dhcpd.conf

# clean
rm -fr "$FILEDIR" "pulse2-doc" "bootstrap.sh"

# and halt
urpmi --force screen
screen /root/clean_and_halt.sh


