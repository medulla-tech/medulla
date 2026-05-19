#!/bin/bash
# (c) 2026 Medulla, http://www.medulla-tech.io
#
# Cron script to check for available Medulla updates.
# Writes results to the admin.medulla_update_availability table.
#
# Cron entry: 0 3 * * * /usr/sbin/check_medulla_updates.sh
# file: /usr/sbin/check_medulla_updates.sh
#
# Dependencies: curl, jq (for fetching and parsing the remote disclaimer manifest)

DBUSER=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbuser 2> /dev/null || echo mmc)
DBPASS=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbpasswd)
DBHOST=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbhost 2> /dev/null || echo localhost)

DISCLAIMER_URL="https://dl.medulla-tech.io/up/versions_disclaimer.json"

mysql_cmd() {
    mysql -u"${DBUSER}" -p"${DBPASS}" -h"${DBHOST}" admin -Bse "$1" 2>/dev/null
}

# Double single quotes for safe injection into SQL string literals.
sql_escape() {
    printf '%s' "$1" | sed "s/'/''/g"
}

# Fetch the remote disclaimer manifest and extract the block for the given
# version. Sets DISCLAIMER_LEVEL and DISCLAIMER_JSON globals; leaves them
# empty when the version has no entry or when the fetch fails.
fetch_disclaimer() {
    local target_version="$1"
    DISCLAIMER_LEVEL=""
    DISCLAIMER_JSON=""

    if [[ -z "${target_version}" || "${target_version}" == "unknown" ]]; then
        return
    fi

    local manifest
    manifest=$(curl -fsS --max-time 10 "${DISCLAIMER_URL}" 2>/dev/null)
    if [[ -z "${manifest}" ]]; then
        return
    fi

    local entry
    entry=$(printf '%s' "${manifest}" | jq -c --arg v "${target_version}" '.[$v] // empty' 2>/dev/null)
    if [[ -z "${entry}" ]]; then
        return
    fi

    DISCLAIMER_LEVEL=$(printf '%s' "${entry}" | jq -r '.level // ""' 2>/dev/null)
    DISCLAIMER_JSON=$(printf '%s' "${entry}" | jq -c '.disclaimer // {}' 2>/dev/null)
}

# Get current Medulla version
CURRENT_VERSION=$(cat /var/lib/mmc/version 2>/dev/null)
if [[ -z "${CURRENT_VERSION}" ]]; then
    CURRENT_VERSION=$(dpkg-query -W -f='${Version}' pulse2-common 2>/dev/null | cut -d'g' -f1)
fi

# Update apt cache
apt-get update -qq > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    mysql_cmd "INSERT INTO medulla_update_availability (id, update_available, current_version, last_check, last_check_status, disclaimer_level, disclaimer_json)
               VALUES (1, 0, '${CURRENT_VERSION}', NOW(), 'error', NULL, NULL)
               ON DUPLICATE KEY UPDATE
               update_available=0, current_version='${CURRENT_VERSION}', last_check=NOW(), last_check_status='error', disclaimer_level=NULL, disclaimer_json=NULL;"
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

    fetch_disclaimer "${AVAILABLE_VERSION}"

    if [[ -n "${DISCLAIMER_LEVEL}" && -n "${DISCLAIMER_JSON}" ]]; then
        LEVEL_SQL="'$(sql_escape "${DISCLAIMER_LEVEL}")'"
        JSON_SQL="'$(sql_escape "${DISCLAIMER_JSON}")'"
    else
        LEVEL_SQL="NULL"
        JSON_SQL="NULL"
    fi

    mysql_cmd "INSERT INTO medulla_update_availability (id, update_available, current_version, available_version, last_check, last_check_status, disclaimer_level, disclaimer_json)
               VALUES (1, 1, '${CURRENT_VERSION}', '${AVAILABLE_VERSION}', NOW(), 'success', ${LEVEL_SQL}, ${JSON_SQL})
               ON DUPLICATE KEY UPDATE
               update_available=1, current_version='${CURRENT_VERSION}', available_version='${AVAILABLE_VERSION}', last_check=NOW(), last_check_status='success', disclaimer_level=${LEVEL_SQL}, disclaimer_json=${JSON_SQL};"
else
    mysql_cmd "INSERT INTO medulla_update_availability (id, update_available, current_version, available_version, last_check, last_check_status, disclaimer_level, disclaimer_json)
               VALUES (1, 0, '${CURRENT_VERSION}', NULL, NOW(), 'success', NULL, NULL)
               ON DUPLICATE KEY UPDATE
               update_available=0, current_version='${CURRENT_VERSION}', available_version=NULL, last_check=NOW(), last_check_status='success', disclaimer_level=NULL, disclaimer_json=NULL;"
fi
