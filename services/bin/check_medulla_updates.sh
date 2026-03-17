#!/bin/bash
# (c) 2026 Medulla, http://www.medulla-tech.io
#
# Cron script to check for available Medulla updates.
# Writes results to the admin.medulla_update_availability table.
#
# Cron entry: 0 3 * * * /usr/sbin/check_medulla_updates.sh
# file: /usr/sbin/check_medulla_updates.sh

DBUSER=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbuser 2> /dev/null || echo mmc)
DBPASS=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbpasswd)
DBHOST=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbhost 2> /dev/null || echo localhost)

mysql_cmd() {
    mysql -u"${DBUSER}" -p"${DBPASS}" -h"${DBHOST}" admin -Bse "$1" 2>/dev/null
}

# Get current Medulla version
CURRENT_VERSION=$(cat /var/lib/mmc/version 2>/dev/null)
if [[ -z "${CURRENT_VERSION}" ]]; then
    CURRENT_VERSION=$(dpkg-query -W -f='${Version}' pulse2-common 2>/dev/null | cut -d'g' -f1)
fi

# Update apt cache
apt-get update -qq > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    mysql_cmd "INSERT INTO medulla_update_availability (id, update_available, current_version, last_check, last_check_status)
               VALUES (1, 0, '${CURRENT_VERSION}', NOW(), 'error')
               ON DUPLICATE KEY UPDATE
               update_available=0, current_version='${CURRENT_VERSION}', last_check=NOW(), last_check_status='error';"
    exit 1
fi

# Check if medulla packages have updates available
UPDATES=$(LANG=C apt-get -s dist-upgrade 2>/dev/null | awk '/^Inst/ { print $2 }')
MEDULLA_UPDATES=""
for pkg in $UPDATES; do
    # Check if package comes from medulla repository
    repo_check=$(apt-cache policy "$pkg" 2>/dev/null | awk '/Candidate:/,/\*\*\*/' | grep -i medulla)
    if [[ -n "$repo_check" ]]; then
        MEDULLA_UPDATES="${MEDULLA_UPDATES} ${pkg}"
    fi
done

# Get available version from apt candidate
AVAILABLE_VERSION=$(apt-cache policy pulse2-common 2>/dev/null | awk '/Candidate/ { print $2 }' | cut -d'g' -f1)

# Check for updates: either new packages available via apt, or pending migration
# (packages already updated but /var/lib/mmc/version not yet bumped)
if [[ -n "${MEDULLA_UPDATES}" ]] || [[ -n "${AVAILABLE_VERSION}" && "${AVAILABLE_VERSION}" != "${CURRENT_VERSION}" ]]; then
    if [[ -z "${AVAILABLE_VERSION}" ]]; then
        AVAILABLE_VERSION="unknown"
    fi

    mysql_cmd "INSERT INTO medulla_update_availability (id, update_available, current_version, available_version, last_check, last_check_status)
               VALUES (1, 1, '${CURRENT_VERSION}', '${AVAILABLE_VERSION}', NOW(), 'success')
               ON DUPLICATE KEY UPDATE
               update_available=1, current_version='${CURRENT_VERSION}', available_version='${AVAILABLE_VERSION}', last_check=NOW(), last_check_status='success';"
else
    mysql_cmd "INSERT INTO medulla_update_availability (id, update_available, current_version, available_version, last_check, last_check_status)
               VALUES (1, 0, '${CURRENT_VERSION}', NULL, NOW(), 'success')
               ON DUPLICATE KEY UPDATE
               update_available=0, current_version='${CURRENT_VERSION}', available_version=NULL, last_check=NOW(), last_check_status='success';"
fi
