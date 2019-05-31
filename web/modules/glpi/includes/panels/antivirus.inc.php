<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 * (c) 2012-2019 siveo, http://www.siveo.net/
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
    "class" => "AntivirusPanel",
    "id" => "antivirus",
    "refresh" => 3600,
    "title" => _T("Antivirus", "glpi"),
);

class AntivirusPanel extends Panel {

    function display_content() {

        $count = getAntivirusStatus();
        $uninventorized_text = _T("Uninventoried Machines", "dashboard");
        $uninventorized = get_computer_count_for_dashboard()['unregistered'];

        $jsonCount = json_encode($count);
        $createGroupText = json_encode(_T("Create a group", "glpi"));
        $greenMessage = json_encode(_T("OK: %percent% (%d)", "glpi"));
        $orangeMessage = json_encode(_T("Not running or not up-to-date: %percent% (%d)", "glpi"));
        $redMessage = json_encode(_T("No antivirus found: %percent% (%d)", "glpi"));
        $urlRedirect = json_encode(urlStrRedirect("base/computers/createAntivirusStaticGroup"));

        echo <<< ANTIVIRUS
    <div id="antivirus-graphs"></div>
    <script type="text/javascript">
    var machineCount = $jsonCount,
        greenMessage = $greenMessage,
        orangeMessage = $orangeMessage,
        redMessage = $redMessage,
        uninventorized = $uninventorized,
        createGroupText = $createGroupText,
        urlRedirect = $urlRedirect;

        var datas = [
          {
            'label': greenMessage.split(" %percent% ")[0],
            'value':("green" in machineCount)?machineCount["green"]:0,
            'href':urlRedirect+"&group=green",
          },
          {
            'label': redMessage.split(" %percent% ")[0],
            'value':("red" in machineCount)?machineCount["red"]:0,
            'href':urlRedirect+"&group=red",
          },
          {
            'label': orangeMessage.split(" %percent% ")[0],
            'value':("orange" in machineCount)?machineCount["orange"]:0,
            'href':urlRedirect+"&group=orange",
          },
          {
            'label': '$uninventorized_text',
            'value': uninventorized,
            'href':"#",
          }
        ];
      donut("antivirus-graphs", datas, "Total", machineCount["green"]+machineCount["red"]+machineCount["orange"]+uninventorized);
    </script>
ANTIVIRUS;
    }
}

?>
