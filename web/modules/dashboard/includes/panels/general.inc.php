<?php
/**
 * (c) 2012 Mandriva, http://www.mandriva.com
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
    "refresh" => 30,
    "title" => _T("General", "dashboard"),
);

class GeneralPanel extends Panel {

    function display_content() {
        $load = json_encode($this->data['load']);
        $memory = json_encode($this->data['memory']);

        echo '
        <p><strong>' . $this->data['hostname'] . '</strong> ' . _T('on') . ' <strong>' . $this->data['dist'][0] . ' ' . $this->data['dist'][1] . '</strong></p>
        <p><strong>' . _('Uptime') . '</strong> : ' . $this->data['uptime'] . '</p>
        <div><strong>' . _T('Load') . '</strong>
            <div id="load-graph"></div>
        </div>
        <div><strong>' . _T('RAM') . '</strong>
            <div id="ram-graph"></div>
            </div>
        <script type="text/javacript">
            var load = ' . $load . ',
                height = 65,
                width = 200,
                r = Raphael("load-graph", width, height + 5);
            r.path("M20 55L191 55");
            r.linechart(15, 5, width - 15, height - 5,
                        [[10, 5, 0], [10, 5, 0]],
                        [load, [0, 1, 0]],
                        {axis: "0 0 0 1", colors: ["#ef2929", ""], shade: true}
            );
            var memory = ' . $memory . ',
                height = 15,
                width = 200,
                r = Raphael("ram-graph", width, height + 5);
            r.rect(0, 5, width, height)
             .attr({fill: "#73d216", stroke: "#fff", "stroke-width": "2px"});
            r.rect(1, 6, width * (memory.percent / 100), height - 2)
             .attr({fill: "#ef2929", "stroke-width": "0"});
            r.text(width - 3, 13, memory.available + " ' . _T("free") . '")
             .attr({ font: "12px sans-serif", "text-anchor": "end", "fill": "white" });
        </script>';
    }
}

?>
