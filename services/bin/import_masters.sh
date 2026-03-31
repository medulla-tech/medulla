#!/bin/bash
# (c) 2026 Medulla, http://www.medulla-tech.io
#
# This file is part of MMC, http://www.medulla-tech.io
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; If not, see <http://www.gnu.org/licenses/>.

# file : /usr/sbin/import_masters.sh

DISCLAIMER="""
Avertissement : L'image Windows mise à disposition est fournie uniquement à titre d'exemple pour faciliter vos tests et vos déploiements.
Le client doit se conformer au contrat de licence d'utilisateur final de Microsoft ou à toute autres dispositions le complétant ou s'y substituant.
L'utilisateur reconnaît notamment disposer des clés logicielles valides et conformes aux licences de Microsoft. Natsu ne pourra être tenu responsable en cas d'usage non conforme, notamment en cas d'utilisation sans licence appropriée.
"""

DL_URL=https://updates.medulla-tech.io/updates_protected
DEST=/var/lib/pulse2/imaging/masters

DBHOST=$(crudini --get /etc/mmc/plugins/imaging.ini.local database dbhost 2> /dev/null || echo localhost)
DBPORT=$(crudini --get /etc/mmc/plugins/imaging.ini.local database dbport 2> /dev/null || echo 3306)
DBUSER=$(crudini --get /etc/mmc/plugins/imaging.ini.local database dbuser 2> /dev/null || echo mmc)
DBPASS=$(crudini --get /etc/mmc/plugins/imaging.ini.local database dbpasswd)
KEYAES32=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local defaultconnection keyAES32)

import_w1125h2profrx64() {
    # Insert master record in db for Windows 11 25H2 Professionnel FR x64
    echo "Inserting Windows 11 25H2 Professionnel FR x64 master into database..."
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT INTO Image VALUES (1,'/var/lib/pulse2/imaging/masters/4dddf514-c4f6-11f0-ade0-bc2411916521','Master Windows 11 Pro FR','4dddf514-c4f6-11f0-ade0-bc2411916521','Windows 11 25H2 Professionnel FR x64','',9063433016,1,'2025-11-19 03:17:39',1,0,1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO Target (id, name, uuid, raw_mode, type, is_registered_in_package_server, fk_entity, fk_menu) VALUES (1, 'Dummy', 'UUID0', 0, 1, 0, 1, 1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImagingLog VALUES (1,'2025-11-19 03:17:39','unknown',1,1,6)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImageOnImagingServer VALUES (1,1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO MasteredOn VALUES (1,1)"

    # Download and extract master files
    echo "Downloading and extracting Windows 11 25H2 Professionnel FR x64 master..."
    curl -fsSL ${DL_URL}/Win11/4dddf514-c4f6-11f0-ade0-bc2411916521.tar?token=${KEYAES32} | tar -xf - -C ${DEST}
}

# First show disclaimer and wait for user confirmation to proceed. Ilf user presses y we continue, else we exit.
echo "${DISCLAIMER}"
read -p "Acceptez-vous ces termes? (y/n) "
if [[ $REPLY != "y" && $REPLY != "Y" && $REPLY != "o" && $REPLY != "O" ]]; then
    echo "Aborting."
    exit 1
fi

import_w1125h2profrx64
