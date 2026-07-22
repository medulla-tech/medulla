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

IMPORT_ALL=false
if [[ $# -gt 0 ]]; then
    case "$1" in
        --all)
            IMPORT_ALL=true
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--all]"
            exit 1
            ;;
    esac
fi

import_w1125h2profrx64() {
    existing_id=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='4dddf514-c4f6-11f0-ade0-bc2411916521' LIMIT 1")
    if [[ -n "${existing_id}" ]]; then
        echo -e "\nWindows 11 25H2 Professionnel FR x64 master already exists (id=${existing_id}). Skipping import."
        return 0
    fi

    # Insert master record in db for Windows 11 25H2 Professionnel FR x64
    echo -e "\nInserting Windows 11 25H2 Professionnel FR x64 master into database..."
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT INTO Image (\`path\`, \`name\`, \`uuid\`, \`desc\`, \`size\`, \`is_master\`, \`creation_date\`, \`fk_creator\`, \`fk_state\`) VALUES ('/var/lib/pulse2/imaging/masters/4dddf514-c4f6-11f0-ade0-bc2411916521','Master Windows 11 Pro FR','4dddf514-c4f6-11f0-ade0-bc2411916521','Windows 11 25H2 Professionnel FR x64',9063433016,1,'2025-11-19 03:17:39',1,1)"
    id_image=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='4dddf514-c4f6-11f0-ade0-bc2411916521'")
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO Target (id, name, uuid, raw_mode, type, is_registered_in_package_server, fk_entity, fk_menu) VALUES (1, 'Dummy', 'UUID0', 0, 1, 0, 1, 1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImagingLog VALUES (1,'2025-11-19 03:17:39','unknown',1,1,6)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImageOnImagingServer VALUES (${id_image},1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO MasteredOn VALUES (${id_image},1)"

    # Download and extract master files
    echo "Downloading and extracting Windows 11 25H2 Professionnel FR x64 master..."
    curl -fsSL ${DL_URL}/Win11/4dddf514-c4f6-11f0-ade0-bc2411916521.tar?token=${KEYAES32} | tar -xf - -C ${DEST}
}

import_ubu2404biosamd64() {
    existing_id=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='38fe12a0-59eb-11f1-8795-bc2411e4867f' LIMIT 1")
    if [[ -n "${existing_id}" ]]; then
        echo -e "\nUbuntu 24.04 BIOS AMD64 master already exists (id=${existing_id}). Skipping import."
        return 0
    fi

    # Insert master record in db for Ubuntu 24.04 BIOS AMD64
    echo -e "\nInserting Ubuntu 24.04 BIOS AMD64 master into database..."
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT INTO Image (\`path\`, \`name\`, \`uuid\`, \`desc\`, \`size\`, \`is_master\`, \`creation_date\`, \`fk_creator\`, \`fk_state\`) VALUES ('/var/lib/pulse2/imaging/masters/38fe12a0-59eb-11f1-8795-bc2411e4867f','Master Ubuntu 24.04 BIOS AMD64','38fe12a0-59eb-11f1-8795-bc2411e4867f','Ubuntu 24.04 BIOS AMD64',3271778295,1,'2026-05-27 17:43:43',1,1)"
    id_image=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='38fe12a0-59eb-11f1-8795-bc2411e4867f'")
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO Target (id, name, uuid, raw_mode, type, is_registered_in_package_server, fk_entity, fk_menu) VALUES (1, 'Dummy', 'UUID0', 0, 1, 0, 1, 1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImagingLog VALUES (1,'2025-11-19 03:17:39','unknown',1,1,6)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImageOnImagingServer VALUES (${id_image},1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO MasteredOn VALUES (${id_image},1)"

    # Download and extract master files
    echo "Downloading and extracting Ubuntu 24.04 AMD64 master..."
    curl -fsSL ${DL_URL}/Ubu2404/38fe12a0-59eb-11f1-8795-bc2411e4867f.tar?token=${KEYAES32} | tar -xf - -C ${DEST}
}

import_ubu2604biosamd64() {
    existing_id=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='17734af0-5a76-11f1-ad8c-bc2411e4867f' LIMIT 1")
    if [[ -n "${existing_id}" ]]; then
        echo -e "\nUbuntu 26.04 BIOS AMD64 master already exists (id=${existing_id}). Skipping import."
        return 0
    fi

    # Insert master record in db for Ubuntu 26.04 BIOS AMD64
    echo -e "\nInserting Ubuntu 26.04 BIOS AMD64 master into database..."
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT INTO Image (\`path\`, \`name\`, \`uuid\`, \`desc\`, \`size\`, \`is_master\`, \`creation_date\`, \`fk_creator\`, \`fk_state\`) VALUES ('/var/lib/pulse2/imaging/masters/17734af0-5a76-11f1-ad8c-bc2411e4867f','Master Ubuntu 26.04 BIOS AMD64','17734af0-5a76-11f1-ad8c-bc2411e4867f','Ubuntu 26.04 BIOS AMD64',4162480930,1,'2026-05-28 10:17:47',1,1)"
    id_image=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='17734af0-5a76-11f1-ad8c-bc2411e4867f'")
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO Target (id, name, uuid, raw_mode, type, is_registered_in_package_server, fk_entity, fk_menu) VALUES (1, 'Dummy', 'UUID0', 0, 1, 0, 1, 1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImagingLog VALUES (1,'2025-11-19 03:17:39','unknown',1,1,6)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImageOnImagingServer VALUES (${id_image},1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO MasteredOn VALUES (${id_image},1)"

    # Download and extract master files
    echo "Downloading and extracting Ubuntu 26.04 AMD64 master..."
    curl -fsSL ${DL_URL}/Ubu2604/17734af0-5a76-11f1-ad8c-bc2411e4867f.tar?token=${KEYAES32} | tar -xf - -C ${DEST}
}

import_min223biosamd64() {
    existing_id=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='369f382d-60ec-11f1-8288-bc241111a7ae' LIMIT 1")
    if [[ -n "${existing_id}" ]]; then
        echo -e "\nMint 22.3 BIOS AMD64 master already exists (id=${existing_id}). Skipping import."
        return 0
    fi

    # Insert master record in db for Mint 22.3 BIOS AMD64
    echo -e "\nInserting Mint 22.3 BIOS AMD64 master into database..."
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT INTO Image (\`path\`, \`name\`, \`uuid\`, \`desc\`, \`size\`, \`is_master\`, \`creation_date\`, \`fk_creator\`, \`fk_state\`) VALUES ('/var/lib/pulse2/imaging/masters/369f382d-60ec-11f1-8288-bc241111a7ae','Master Mint 22.3 BIOS AMD64','369f382d-60ec-11f1-8288-bc241111a7ae','Mint 22.3 BIOS AMD64',3454215679,1,'2026-06-05 15:38:27',1,1)"
    id_image=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='369f382d-60ec-11f1-8288-bc241111a7ae'")
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO Target (id, name, uuid, raw_mode, type, is_registered_in_package_server, fk_entity, fk_menu) VALUES (1, 'Dummy', 'UUID0', 0, 1, 0, 1, 1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImagingLog VALUES (1,'2025-11-19 03:17:39','unknown',1,1,6)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImageOnImagingServer VALUES (${id_image},1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO MasteredOn VALUES (${id_image},1)"

    # Download and extract master files
    echo "Downloading and extracting Mint 22.3 AMD64 master..."
    curl -fsSL ${DL_URL}/Min223/369f382d-60ec-11f1-8288-bc241111a7ae.tar?token=${KEYAES32} | tar -xf - -C ${DEST}
}

import_zorin181corebiosamd64() {
    existing_id=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='a23aa027-697d-11f1-8c3e-bc24112b8ad5' LIMIT 1")
    if [[ -n "${existing_id}" ]]; then
        echo -e "\nZorin OS 18.1 Core BIOS AMD64 master already exists (id=${existing_id}). Skipping import."
        return 0
    fi

    # Insert master record in db for Zorin OS 18.1 Core BIOS AMD64
    echo -e "\nInserting Zorin OS 18.1 Core BIOS AMD64 master into database..."
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT INTO Image (\`path\`, \`name\`, \`uuid\`, \`desc\`, \`size\`, \`is_master\`, \`creation_date\`, \`fk_creator\`, \`fk_state\`) VALUES ('/var/lib/pulse2/imaging/masters/a23aa027-697d-11f1-8c3e-bc24112b8ad5','Master Zorin OS 18.1 Core BIOS AMD64','a23aa027-697d-11f1-8c3e-bc24112b8ad5','Zorin OS 18.1 Core BIOS AMD64',5102177913,1,'2026-06-16 13:19:33',1,1)"
    id_image=$(mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "SELECT id FROM Image WHERE uuid='a23aa027-697d-11f1-8c3e-bc24112b8ad5'")
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO Target (id, name, uuid, raw_mode, type, is_registered_in_package_server, fk_entity, fk_menu) VALUES (1, 'Dummy', 'UUID0', 0, 1, 0, 1, 1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImagingLog VALUES (1,'2025-11-19 03:17:39','unknown',1,1,6)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO ImageOnImagingServer VALUES (${id_image},1)"
    mysql -N -s -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} imaging -e "INSERT IGNORE INTO MasteredOn VALUES (${id_image},1)"

    # Download and extract master files
    echo "Downloading and extracting Zorin OS 18.1 Core AMD64 master..."
    curl -fsSL ${DL_URL}/Zor181/a23aa027-697d-11f1-8c3e-bc24112b8ad5.tar?token=${KEYAES32} | tar -xf - -C ${DEST}
}

# First show disclaimer and wait for user confirmation to proceed. If user presses y we continue, else we exit.
echo "${DISCLAIMER}"
read -p "Acceptez-vous ces termes? (y/n) "
if [[ $REPLY != "y" && $REPLY != "Y" && $REPLY != "o" && $REPLY != "O" ]]; then
    echo "Aborting."
    exit 1
fi

if [[ "$IMPORT_ALL" == "true" ]]; then
    import_w1125h2profrx64
    import_ubu2404biosamd64
    import_ubu2604biosamd64
    import_min223biosamd64
    exit 0
fi

echo -e "\nChoose the master to import:"
echo "1) Windows 11 25H2 Professionnel FR x64"
echo "2) Ubuntu 24.04 BIOS AMD64"
echo "3) Ubuntu 26.04 BIOS AMD64"
echo "4) Mint 22.3 BIOS AMD64"
echo "5) Zorin OS 18.1 Core BIOS AMD64"
read -p "Your choice (1/2/3/4/5): " MASTER_CHOICE

case "$MASTER_CHOICE" in
    1)
        import_w1125h2profrx64
        ;;
    2)
        import_ubu2404biosamd64
        ;;
    3)
        import_ubu2604biosamd64
        ;;
    4)
        import_min223biosamd64
        ;;
    5)
        import_zorin181corebiosamd64
        ;;
    *)
        echo "Invalid choice. Aborting."
        exit 1
        ;;
esac
