<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 *
 * This file is part of Mandriva Management Console (MMC).
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
require_once("modules/glpi/includes/xmlrpc.php");

$options = array(
    "class" => "GlpiPanel",
    "id" => "inventory",
    "refresh" => 3600,
    "title" => _T("Inventories", "glpi"),
);

class GlpiPanel extends Panel {

    function display_content() {

        $result = getMachineNumberByState();
        $count = $result['count'];
        $days = $result['days'];

        $jsonCount = json_encode($count);
        $jsonDays= json_encode($days);
        $createGroupText = json_encode(_T("Create a group", "glpi"));
        $lessThanText = json_encode(_T("< %s days: %percent% (%d)", "glpi"));
        $moreThanText = json_encode(_T("> %s days: %percent% (%d)", "glpi"));
        $urlRedirect = json_encode(urlStrRedirect("base/computers/createStaticGroup"));

        echo <<< INVENTORY
    <div id="inventory-graphs"></div>
    <script type="text/javascript">
    var machineCount = $jsonCount,
        days = $jsonDays,
        lessThanText = $lessThanText,
        moreThanText = $moreThanText,
        createGroupText = $createGroupText,
        urlRedirect = $urlRedirect;

    var datas = [
      {
        'label': lessThanText.replace("%s", days['orange']).split(": %percent%")[0],
        'value':("green" in machineCount)?machineCount["green"]:0,
        'href':urlRedirect+"&group=green&days="+days['orange'],
      },
      {
        'label': moreThanText.replace("%s", days['red']).split(": %percent%")[0],
        'value':("red" in machineCount)?machineCount["red"]:0,
        'href':urlRedirect+"&group=red&days="+days['red'],
      },
      {
        'label': moreThanText.replace("%s", days['orange']).split(": %percent%")[0],
        'value':("orange" in machineCount)?machineCount["orange"]:0,
        'href':urlRedirect+"&group=orange&days="+days['orange'],
      }
    ];
    donut("inventory-graphs", datas, "Total", machineCount["green"]+machineCount["red"]+machineCount["orange"])

    </script>
INVENTORY;
    }
}

?>
