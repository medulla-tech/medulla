#!/bin/sh -x
#
# (c) 2003-2007 Linbox FAS, http://linbox.com
# (c) 2008-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

if mount |grep nb0; then
    echo "Only one mount allowed at a time !"
    exit 1
fi

killall gznbd
sleep 1

[ -d /mnt/tmp ] || mkdir -p /mnt/tmp

modprobe nbd
(/tftpboot/revoboot/bin/lrsgznbd /dev/nb0 $1) &
# auto umount after 2 hours
(sleep 7200;umount /mnt/tmp >/dev/null 2>&1) &

sleep 2
mount -r -t vfat /dev/nb0 /mnt/tmp
# autodetect
mount -r /dev/nb0 /mnt/tmp

