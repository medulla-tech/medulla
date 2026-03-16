#!/bin/bash
#
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

# file : /usr/sbin/medulla-stats.sh

AESKEY=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local defaultconnection keyAES32 2>/dev/null)
NB_MACH=$(mysql --defaults-group-suffix=medulla xmppmaster -Bse 'SELECT COUNT(*) FROM machines')
NB_USERS=$(slapcat | grep "dn: uid=" | wc -l)

curl -fsSL -X POST \
  -H "Content-Type: application/json" \
  --data "{\"aeskey\":\"$AESKEY\",\"nb_mach\":\"$NB_MACH\",\"nb_users\":\"$NB_USERS\"}" \
  https://updates.medulla-tech.io/post_stats.php
