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
    "class" => "SpacePanel",
    "id" => "space",
    "refresh" => 960,
    "title" => _T("Disk usage", "dashboard"),
);

class SpacePanel extends Panel {

    function display_content() {

        $json = json_encode($this->data['partitions']);
        $used = _T("used");
        $free = _T("free");

        echo <<< SPACE
        <div id="space-graphs"></div>
        <script type="text/javascript">
        var partitions = $json,
            r = Raphael("space-graphs"),
            radius = 40,
            margin = 30,
            x = 50,
            y = 60;
        for (var i=0; i < partitions.length; i++) {
            var partition = partitions[i],
                data = [],
                legend = [],
                colors = [],
                title = partition.mountpoint;
            if (partition.usage.percent < 1)
                partition.usage.percent = 1;
            var free = 100 - Math.round(partition.usage.percent),
                used = Math.round(partition.usage.percent);
            data.push(used);
            legend.push(partition.usage.used + " $used");
            colors.push("000-#ef2929-#A31A1A");
            if (free > 0) {
                data.push(free);
                legend.push(partition.usage.free + " $free");
                colors.push("000-#73d216-#42780D");
            }
            if (partition.device.length < 30)
                title += " (" + partition.device + ") ";
            r.text(5, y - radius - 10, title)
             .attr({ font: "12px sans-serif" })
             .attr({ "text-anchor": "start" });
            data = getPercentageData(data);
            r.piechart(x, y + 5, radius, data,
                       {legend: legend,
                        legendpos: "east",
                        colors: colors})
             .hover(function () {
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
            y += (radius * 2) + margin + 5;
        }
        r.setSize(200, partitions.length * (radius * 2 + margin) + 10);
        </script>
SPACE;
    }

}

?>
