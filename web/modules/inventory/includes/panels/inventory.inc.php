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
require_once("modules/inventory/includes/xmlrpc.php");

$options = array(
    "class" => "InventoryPanel",
    "id" => "inventory",
    "refresh" => 3600,
    "title" => _T("Computers", "inventory"),
);

class InventoryPanel extends Panel {

    function display_content() {

        $result = getMachineNumberByState();
        $count = $result['count'];
        $days = $result['days'];

        $jsonCount = json_encode($count);
        $jsonDays= json_encode($days);
        $lessThanText = json_encode(_T("Less than %s days: %d", "inventory"));
        $moreThanText = json_encode(_T("More than %s days: %d", "inventory"));
        $urlRedirect = json_encode(urlStrRedirect("inventory/inventory/createStaticGroup"));
        $_SESSION['inventoryDashboard'] = array(
            "green" => $result['machine']['green'],
            "orange" => $result['machine']['orange'],
            "red" => $result['machine']['red'],
        );

        print _T("Latest Inventory Date", "inventory");

        echo <<< INVENTORY
    <div id="inventory-graphs"></div>
    <script type="text/javascript">
    var machineCount = $jsonCount,
        days = $jsonDays,
        lessThanText = $lessThanText,
        moreThanText = $moreThanText,
        urlRedirect = $urlRedirect,
        r = Raphael("inventory-graphs", 200, 250),
        radius = 80,
        x = 90,
        y = 90;

    var data = [];
    var legend = [];
    var colors = [];
    var href = [];

    if (machineCount.green) {
        var legendText = lessThanText.replace('%s', days.orange).replace('%d', machineCount.green)
        data.push(machineCount.green);
        legend.push(legendText);
        colors.push("#73d216");
        href.push(urlRedirect + "&group=green&days=" + days.orange);
    }

    if (machineCount.orange) {
        var legendText = moreThanText.replace('%s', days.orange).replace('%d', machineCount.orange)
        data.push(machineCount.orange);
        legend.push(legendText);
        colors.push("#ff9c00");
        href.push(urlRedirect + "&group=orange&days=" + days.orange);
    }

    if (machineCount.red) {
        var legendText = moreThanText.replace('%s', days.red).replace('%d', machineCount.red)
        data.push(machineCount.red);
        legend.push(legendText);
        colors.push("#ef2929");
        href.push(urlRedirect + "&group=red&days=" + days.red);
    }

    var pie = r.piechart(x, y, radius, data, 
                     {legend: legend,
                      legendpos: "south",
                      colors: colors, 
                      href: href});
    pie.hover(function () {
        this.sector.stop();
        this.sector.animate({ transform: 's1.1 1.1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

        if (this.label) {
            this.label[0].stop();
            this.label[0].attr({ r: 7.5 });
            this.label[1].attr({ "font-weight": 800 });
        }
    }, function () {
        this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

        if (this.label) {
            this.label[0].animate({ r: 5 }, 500, "bounce");
            this.label[1].attr({ "font-weight": 400 });
        }
    });

    </script>
INVENTORY;
    }
}


?>
