<?php
/*
 * (c) 2016-2019 siveo, http://www.siveo.net/
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/backuppc/includes/xmlrpc.php");?>

<script src="modules/dashboard/graph/js/donut.js"></script>
<?php $options = array(
    "class" => "BackupPanel",
    "id" => "backup",
    "refresh" => 3600,
    "title" => _T("Machines backup", "dashboard"),
    "enable" => true,
);

class BackupPanel extends Panel {

    function display_content() {
        $urlRedirect = urlStrRedirect("base/computers/createBackupStaticGroup");
        $total_machines = getComputerCount();
        $machines_backup = get_count_of_backuped_hosts();
        $machines_not_backup = $total_machines - $machines_backup;
        $configured_text = _T("Backup configured", "dashboard")." : ";
        $not_configured_text = _T("Backup not configured", "dashboard")." : ";
        $total_machines_text =  _T("Total machines", "dashboard")." :" ;
        $uninventorized_text = _T("Uninventoried Machines","dashboard")." : ";
        $uninventorized = get_computer_count_for_dashboard()["unregistered"];
        echo <<< BACKUP
          <script>
            var backupDatas = [
              {"label": "$configured_text", "value":$machines_backup, "href":"$urlRedirect&backup=yes"},
              {'label': '', 'value': 0, "href": ""},
              {'label': '$not_configured_text', 'value': $machines_not_backup, "href": "$urlRedirect&backup=no"},
              {'label': '$uninventorized_text', 'value': $uninventorized, "href": ""}
            ];

            donut("backup",backupDatas, "Total", $total_machines+$uninventorized);
          </script>
BACKUP;
      }
}
?>
