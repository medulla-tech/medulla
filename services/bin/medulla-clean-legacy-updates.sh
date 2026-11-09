#!/bin/bash
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Removes what the former updates engine left on a Medulla server and points the
# updates substitute at the new engine. Its database objects are removed by the
# SQL schemas (xmppmaster 117, dyngroup 008), not here.
#
#   medulla-clean-legacy-updates.sh           shows what would be done
#   medulla-clean-legacy-updates.sh --apply   does it
#
# Can be run again: what is already gone is skipped.

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
LOG=/var/log/mmc/medulla-clean-legacy-updates.log
SUBST=/etc/pulse-xmpp-agent-substitute
PACKAGES=/var/lib/pulse2/packages
todo=0

say() { echo "$1"; [ "$APPLY" -eq 1 ] && echo "$(date '+%F %T') $1" >> "$LOG"; }
act() { # description, then the command
    local what=$1; shift
    todo=$((todo + 1))
    if [ "$APPLY" -eq 1 ]; then
        if "$@"; then say "[v] $what"; else say "[x] $what"; fi
    else
        say "[ ] $what"
    fi
}
sql() { mysql -N -B -e "$1" 2>/dev/null; }
size() { du -sh "$1" 2>/dev/null | cut -f1; }
ini_get() { crudini --get "$1" "$2" "$3" 2>/dev/null; }
# Value read from the .ini.local first, then the .ini
effective() { ini_get "$1.local" "$2" "$3" || ini_get "$1" "$2" "$3"; }

if ! command -v crudini >/dev/null || [ -z "$(sql 'SELECT 1')" ]; then
    echo "crudini and root access to MariaDB are required" >&2
    exit 1
fi
[ "$APPLY" -eq 1 ] || echo "Simulation: nothing is changed. Run again with --apply."

echo "== Updates substitute configuration"
INI=$SUBST/agent_master_substitute_upd.ini
if [ -f "$INI" ]; then
    plugins=$(effective "$INI" plugins pluginliststart)
    wanted=$(echo "$plugins" | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep -v -x -e loadactionupdate -e '' \
             | { cat; echo loadupdates; } | awk '!seen[$0]++' | paste -sd, - | sed 's/,/, /g')
    [ "$plugins" != "$wanted" ] && \
        act "pluginliststart = $wanted" crudini --set "$INI.local" plugins pluginliststart "$wanted"
    databases=$(effective "$INI" global activate_plugin)
    if ! echo "$databases" | tr ',' '\n' | sed 's/ //g' | grep -qx updates; then
        act "activate_plugin = $databases, updates" crudini --set "$INI.local" global activate_plugin "$databases, updates"
    fi
    for key in dbuser dbpasswd; do
        if [ -z "$(effective "$INI" updatesdatabase "updates_$key")" ]; then
            value=$(effective "$INI" pkgsdatabase "pkgs_$key")
            [ -n "$value" ] && act "updates_$key taken from pkgs_$key" \
                crudini --set "$INI.local" updatesdatabase "updates_$key" "$value"
        fi
    done
fi
LOADUPDATES=$SUBST/loadupdates.ini
SECURITY=/etc/mmc/plugins/security.ini
for pair in server_id:server_id key:keyAES32; do
    key=${pair%%:*}; source_key=${pair#*:}
    if [ -z "$(effective "$LOADUPDATES" parameters "$key")" ]; then
        value=$(effective "$SECURITY" cve_central "$source_key")
        [ -n "$value" ] && act "loadupdates $key taken from cve_central $source_key" \
            crudini --set "$LOADUPDATES.local" parameters "$key" "$value"
    fi
done
[ -z "$(effective "$LOADUPDATES" parameters url)" ] && \
    echo "    To do by hand: url of the mirror in $LOADUPDATES.local"

echo "== Former configuration files"
for f in loadactionupdate.ini update_windows.ini; do
    for path in "$SUBST/$f" "$SUBST/$f.local"; do
        [ -e "$path" ] && act "remove $path" rm -f "$path"
    done
done

echo "== Former scheduled tasks"
for f in medulla_winupdates_dl medulla_osupgrade_dl; do
    [ -e "/etc/cron.d/$f" ] && act "remove /etc/cron.d/$f" rm -f "/etc/cron.d/$f"
done
if crontab -l 2>/dev/null | grep -qE 'winupdate|medulla-generate-update|osupgrade'; then
    act "remove the former updates lines of the root crontab" \
        sh -c "crontab -l | grep -vE 'winupdate|medulla-generate-update|osupgrade' | crontab -"
fi

echo "== Former program files"
for f in medulla-generate-update-package.py medulla-generate-winupdate-packages \
         medulla-generate-winupdatemajor-packages medulla-mariadb-move-update-package.py \
         medulla_mysql_exec_update.sh medulla_mysql_exec_uninstall_unnecessary_update_package.sh; do
    [ -e "/usr/sbin/$f" ] && act "remove /usr/sbin/$f" rm -f "/usr/sbin/$f"
done
for dir in /usr/lib/python3*/dist-packages/pulse_xmpp_master_substitute /usr/lib/python3*/site-packages/pulse_xmpp_master_substitute; do
    for f in pluginsmastersubstitute/plugin_loadactionupdate.py pluginsmastersubstitute/plugin_update_windows.py \
             pluginsmastersubstitute/plugin_update_linux.py config/loadactionupdate.ini config/update_windows.ini; do
        [ -e "$dir/$f" ] && act "remove $dir/$f" rm -f "$dir/$f"
    done
done
# Served to the machines by this server
for f in xmpp_baseplugin/plugin_updatemedullainfo.py xmpp_baseplugin/plugin_update_linux_command.py \
         xmpp_basepluginscheduler/scheduling_win11compatcheck.py \
         xmpp_baseremoteagent/lib/medulla_windows11_compatibility.py xmpp_baseremoteagent/lib/update_linux.py \
         xmpp_baseremoteagent/lib/linux_major_upgrade.py \
         xmpp_baseremoteagent/script/history_update.ps1 xmpp_baseremoteagent/bin/medulla_info_update.py \
         xmpp_baseremoteagent/bin/uninstall_medulla_info_update_notification.py; do
    [ -e "/var/lib/pulse2/$f" ] && act "remove /var/lib/pulse2/$f" rm -f "/var/lib/pulse2/$f"
done

echo "== Former data"
[ -d /var/lib/pulse2/base_update_package ] && \
    act "remove /var/lib/pulse2/base_update_package ($(size /var/lib/pulse2/base_update_package))" \
        rm -rf /var/lib/pulse2/base_update_package
if [ -n "$(sql "SHOW DATABASES LIKE 'base_wsusscn2'")" ]; then
    mb=$(sql "SELECT ROUND(SUM(data_length + index_length) / 1048576) FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'base_wsusscn2'")
    act "drop the base_wsusscn2 database (${mb:-0} MB)" mysql -e "DROP DATABASE base_wsusscn2"
fi

echo "== Former packages"
remove_package() { # uuid, share directory
    local uuid=$1 dir=$2
    [ -L "$PACKAGES/$uuid" ] && rm -f "$PACKAGES/$uuid"
    rm -rf "${dir:?}/$uuid"
    mysql -e "DELETE FROM pkgs.packages WHERE uuid = '$uuid'"
}
for uuid in dfd3b8dc-linuxupdategenericcommand_p 34181a66-updateslinuxkernel_i8ppnmrs \
            aa365fe6-linuxupdateother_cew74x5bi0 e05e689e-linuxupdatesecutity_ivvfn4b; do
    if [ -e "$PACKAGES/sharing/global/$uuid" ] || [ -n "$(sql "SELECT 1 FROM pkgs.packages WHERE uuid = '$uuid'")" ]; then
        act "remove package $uuid" remove_package "$uuid" "$PACKAGES/sharing/global"
    fi
done
# Shares of the updates: everything the new engine did not build
known=$(sql "SELECT uuid FROM updates.packages")
for share in winupdates winupdatesmajor; do
    dir=$PACKAGES/sharing/$share
    listed=$(sql "SELECT p.uuid FROM pkgs.packages p JOIN pkgs.pkgs_shares s ON s.id = p.pkgs_share_id WHERE s.name = '$share'")
    for uuid in $( { ls "$dir" 2>/dev/null; echo "$listed"; } | sort -u); do
        [[ "$uuid" =~ ^[A-Za-z0-9_.-]+$ ]] || continue
        grep -qxF "$uuid" <<<"$known" && continue
        act "remove package $uuid of $share ($(size "$dir/$uuid"))" remove_package "$uuid" "$dir"
    done
done

echo
if [ "$todo" -eq 0 ]; then
    echo "Nothing left from the former updates engine."
elif [ "$APPLY" -eq 1 ]; then
    echo "$todo actions done, log in $LOG. Restart the updates substitute to load the new engine."
else
    echo "$todo actions to do."
fi
