#!/bin/bash
# Copyright (C) 2015 Mandriva S.A
# http://www.mandriva.com
#
# This file is part of Mandriva Pulse2 project.
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

VPN_ARCHIVE="SoftEtherVPNClient.zip"
VPN_URL="http://pulse2.mandriva.org/pub/pulse2/misc/${VPN_ARCHIVE}"

if [ ! -e ${VPN_ARCHIVE} ]; then
    echo "Downloading ${VPN_ARCHIVE}..."
    curl --progress-bar -o ${VPN_ARCHIVE} ${VPN_URL}
    if [ ! -e ${VPN_ARCHIVE} ]; then
        echo
        echo "${VPN_ARCHIVE} download failed. Please restart."
        echo
        exit 1
    fi	
fi

7z x ${VPN_ARCHIVE}
makensis -V1 softether-installer.nsi
