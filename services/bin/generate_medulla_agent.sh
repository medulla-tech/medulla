#!/bin/bash
#
# (c) 2022 Siveo, http://siveo.net
#
# This file is part of Medulla
#
# Medulla is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Medulla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Medulla; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# PARAMETERS TO BE SET

DEST=/var/lib/pulse2/medulla_agent
TAGNAME=$1
FORCED=$2 # If set to "force", will force regeneration even if agent exists

DBHOST=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbhost 2> /dev/null || echo localhost)
DBPORT=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbport 2> /dev/null || echo 3306)
DBUSER=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbuser 2> /dev/null || echo mmc)
DBPASS=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbpasswd)
DBNAME='admin'

# Get list of agents to be generated
# If TAGNAME is provided, only generate for this tag
if [[ "$TAGNAME" == "all" ]]; then
    agents=$(mysql -u${DBUSER} -p${DBPASS} -h${DBHOST} -P${DBPORT} -D${DBNAME} -Bse "SELECT tag_name FROM saas_organisations WHERE is_active=1;")
elif [[ "${TAGNAME}" != "" ]]; then
    # Make sure the tag exists and is active
    tag_exists=$(mysql -u${DBUSER} -p${DBPASS} -h${DBHOST} -P${DBPORT} -D${DBNAME} -Bse "SELECT COUNT(*) FROM saas_organisations WHERE tag_name='${TAGNAME}' AND is_active=1;")
    if [[ "${tag_exists}" -eq 0 ]]; then
        echo "ERROR: Tag ${TAGNAME} does not exist or is not active"
        exit 1
    fi
    agents=${TAGNAME}
else
    echo "Usage: $0 <tagname|all> [force]"
    echo "  <tagname> : Tag name for which to generate the agent"
    echo "  all       : If 'all' is provided, will generate agents for all active tags"
    echo "  [force]   : If set to 'force', will force regeneration even if agent exists"
    exit 1
fi

for tag_name in ${agents}; do
    # Remove old files if still present
    rm -f /var/lib/pulse2/clients/win/Medulla-Agent-windows-*.exe
    rm -f /var/lib/pulse2/clients/lin/Medulla-Agent-linux-*.sh
    rm -f /var/lib/pulse2/clients/mac/Medulla-Agent-mac-*.pkg.tar.gz
    # Get download tag
    dl_tag=$(mysql -u${DBUSER} -p${DBPASS} -h${DBHOST} -P${DBPORT} -D${DBNAME} -Bse "SELECT dl_tag FROM saas_organisations WHERE tag_name=\"${tag_name}\";")
    # Create directory if it does not exist
    if [[ ! -d ${DEST}/${dl_tag} ]]; then
        mkdir -p "${DEST}/${dl_tag}"
        chmod 755 "${DEST}/${dl_tag}"
    fi
    # Generate Full agent if it does not exist or is forced to be regenerated
    generated=0
    if [[ "${FORCED}" == "force" ]] || [[ ! -f "${DEST}/${dl_tag}/Medulla-Agent-windows-FULL-latest.exe" ]] || [[ ! -f "${DEST}/${dl_tag}/Medulla-Agent-linux-MINIMAL-latest.sh" ]]; then
        /var/lib/pulse2/clients/generate-pulse-agent.sh --inventory-tag="${tag_name}"
        generated=1
        gen_status=$?
    fi
    # Check if generation was successful and move file to destination
    if [[ $generated -eq 1 && $gen_status -ne 0 ]]; then
        echo "ERROR: Unable to generate agent for tag ${tag_name}"
    else
        echo "Agent for tag ${tag_name} generated"
        mv /var/lib/pulse2/clients/win/Medulla-Agent-windows-FULL-*-${tag_name}.exe ${DEST}/${dl_tag}/Medulla-Agent-windows-FULL-latest.exe
        chown syncthing:nogroup ${DEST}/${dl_tag}/Medulla-Agent-windows-FULL-latest.exe
        chmod 666 ${DEST}/${dl_tag}/Medulla-Agent-windows-FULL-latest.exe
        mv /var/lib/pulse2/clients/lin/Medulla-Agent-linux-MINIMAL-*-${tag_name}.sh ${DEST}/${dl_tag}/Medulla-Agent-linux-MINIMAL-latest.sh
        chown syncthing:nogroup ${DEST}/${dl_tag}/Medulla-Agent-linux-MINIMAL-latest.sh
        chmod 666 ${DEST}/${dl_tag}/Medulla-Agent-linux-MINIMAL-latest.sh
    fi
    # Remove generated files from temp directory
    rm -f /var/lib/pulse2/clients/win/Medulla-Agent-windows-*.exe
    rm -f /var/lib/pulse2/clients/lin/Medulla-Agent-linux-*.sh
    rm -f /var/lib/pulse2/clients/mac/Medulla-Agent-mac-*.pkg.tar.gz
done
