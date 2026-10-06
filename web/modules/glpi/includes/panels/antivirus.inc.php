<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 * (c) 2012-2019 siveo, http://www.siveo.net/
 * (c) 2025 Medulla, http://www.medulla-tech.io
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
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$options = array(
    "class" => "AntivirusPanel",
    "id" => "antivirus",
    "refresh" => 3600,
    "title" => _T("Antivirus", "glpi"),
);

class AntivirusPanel extends Panel
{
    public function display_content()
    {
        $count = xmlrpc_get_antiviruses_for_dashboard();

        $jsonCount        = json_encode($count);
        $okLabel          = json_encode(_T("OK", "glpi"));
        $notUpToDateLabel = json_encode(_T("Not up to date", "glpi"));
        $disabledLabel    = json_encode(_T("Antivirus disabled", "glpi"));
        $missingLabel     = json_encode(_T("Missing antivirus", "glpi"));
        $staleLabel       = json_encode(_T("Unreliable information", "glpi"));
        $urlRedirect      = json_encode(urlStrRedirect("base/computers/createAntivirusStaticGroup"));

        echo <<< ANTIVIRUS
    <div id="antivirus-graphs" style="display:flex;flex-direction:column;align-items:center;flex:1;"></div>
    <script type="text/javascript">
    var machineCount     = $jsonCount,
        okLabel          = $okLabel,
        notUpToDateLabel = $notUpToDateLabel,
        disabledLabel    = $disabledLabel,
        missingLabel     = $missingLabel,
        staleLabel       = $staleLabel,
        urlRedirect      = $urlRedirect;

    function antivirusCount(key) {
      return (key in machineCount) ? parseInt(machineCount[key], 10) : 0;
    }

    // The donut colors are positional (see dashboard/graph/js/donut.js) :
    // 0 grey, 1 blue, 2 green, 3 orange, 4 red, 5 dark grey, 6 light grey.
    // The two empty slices shift the first real slice on the green color.
    var datas = [
      {'label': '', 'value': 0, 'href': ''},
      {'label': '', 'value': 0, 'href': ''},
      {
        'label': okLabel,
        'value': antivirusCount("green"),
        'href': urlRedirect+"&group=green",
      },
      {
        'label': notUpToDateLabel,
        'value': antivirusCount("orange"),
        'href': urlRedirect+"&group=orange",
      },
      {
        'label': disabledLabel,
        'value': antivirusCount("red"),
        'href': urlRedirect+"&group=red",
      },
      {
        'label': missingLabel,
        'value': antivirusCount("missing"),
        'href': urlRedirect+"&group=missing",
      },
      {
        'label': staleLabel,
        'value': antivirusCount("stale"),
        'href': urlRedirect+"&group=stale",
      }
    ];
    donut("antivirus-graphs", datas, "Total", antivirusCount("total"));
    </script>
ANTIVIRUS;
    }
}
