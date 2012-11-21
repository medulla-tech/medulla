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

$options = array(
    "class" => "GeneralPanel",
    "id" => "general",
    "title" => _T("General", "dashboard"),
);

class GeneralPanel extends Panel {

    function display_content() {

        $load = implode(", ", $this->data['load']);
        $memory = json_encode($this->data['memory']);

echo <<< GENERAL
    <p><strong>{$this->data['hostname']}</strong> on <strong>{$this->data['dist'][0]} {$this->data['dist'][1]}</strong></p>
    <br />
    <p>Uptime : {$this->data['uptime']}</p>
    <p>Load : $load</p>
    <div>RAM :
        <div id="ram-graph"></div>
    </div>
    <script type="text/javacript">
        var memory = $memory,
            height = 15,
            width = 200,
            r = Raphael("ram-graph", width, height + 5);
        r.rect(0, 5, width, height)
         .attr({fill: "#73d216", stroke: "#fff", "stroke-width": "2px"});
        r.rect(1, 6, width * (memory.percent / 100), height - 2)
         .attr({fill: "#ef2929", "stroke-width": "0"});
        r.text(width - 3, 13, memory.available + " Free")
         .attr({ font: "12px sans-serif", "text-anchor": "end", "fill": "white" });
    </script>
GENERAL;

    }
}

?>
