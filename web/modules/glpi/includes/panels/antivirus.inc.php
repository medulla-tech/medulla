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
    "class" => "AntivirusPanel",
    "id" => "antivirus",
    "refresh" => 3600,
    "title" => _T("Antivirus", "glpi"),
);

class AntivirusPanel extends Panel {

    function display_content() {

        $count = getAntivirusStatus();

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
        createGroupText = $createGroupText,
        urlRedirect = $urlRedirect;

    var data = [];
    var legend = [];
    var colors = [];
    var href = [];

    if (machineCount.green) {
        var legendText = greenMessage.replace('%d', machineCount.green)
        data.push(machineCount.green);
        legend.push(legendText);
        colors.push("000-#6AB520-#73d216");
        href.push(urlRedirect + "&group=green");
    }

    if (machineCount.orange) {
        var legendText = orangeMessage.replace('%d', machineCount.orange)
        data.push(machineCount.orange);
        legend.push(legendText);
        colors.push("#ff9c00");
        href.push(urlRedirect + "&group=orange");
    }

    if (machineCount.red) {
        var legendText = redMessage.replace('%d', machineCount.red)
        data.push(machineCount.red);
        legend.push(legendText);
        colors.push("000-#CD1515-#ef2929");
        href.push(urlRedirect + "&group=red");
    }

    // get data percentage values for bar chart generation
    data = getPercentageData(data, 'bar');

    // put percentage values in legend
    for (var i = 0; i < data.length; i++) {
        legend[i] = legend[i].replace('%percent', data[i]);
    }

    var r = Raphael("antivirus-graphs", 200, 20);
        fin = function () {
        },
        fout = function () {
        },
        txtattr = { font: "12px sans-serif" };

    r.hbarchart(0, 0, 200, 20, data, {
        type: 'round',
        stacked: true,
        colors: colors
    }).hover(fin, fout);
    jQuery('#antivirus-graphs').append('<ul></ul>');
    for (var i = 0; i < legend.length; i++) {
        jQuery('#antivirus-graphs ul').append(
            '<li style="color: ' + colors[i].split('-')[2]  + '"><span style="color: #000">' + legend[i]
            + '<a href="' + href[i] + '"><img title="' + createGroupText +
            '" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a></span></li>'
        );
    }
    </script>
    <style type="text/css">
        #antivirus-graphs ul {
            padding-left: 0px;
            margin: 0px;
            margin-top: 3px;
        }
        #antivirus-graphs li {
            list-style: none;
            font-size: 13px;
        }
        #antivirus-graphs li:before {
            content: "•";
            font-size: 20px;
            vertical-align: bottom;
            line-height: 16px;
            margin-right: 3px;
        }
    </style>
ANTIVIRUS;
    }
}

?>
