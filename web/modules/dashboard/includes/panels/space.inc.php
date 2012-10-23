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
    "class" => "SpacePanel",
    "id" => "space",
    "title" => _T("Space", "dashboard"),
);

class SpacePanel extends Panel {

    function display_content() {

        $json = json_encode($this->data['partitions']);

echo <<< SPACE
    <div id="space-graphs"></div>
    <script type="text/javascript">
    Plotr.Base.generateColorscheme = function() {
        return {
            used: "#a40000",
            free: "#4e9a06"
        }
    };

    drawPie = function(id, name, used) {
        var free = (1 - used);

        var options = {
            // Define a padding for the canvas node.
            padding: {
                left: 20,
                right: 20,
                top: 0,
                bottom: 30
            },
            // Background color to render.
            background: {
                hide: true
            },
            legend: {
                hide: true
            },
            // Use the predefined blue colorscheme.
            colorScheme: "space",
            axis: {
                // The fontcolor of the labels is black.
                labelColor: '#444',
                // Add the ticks. Keep in mind, x and y axis are swapped
                // when the BarOrientation is horizontal.
                x: {
                    ticks: [
                        {v:0, label:'Used'},
                        {v:1, label:'Free'},
                    ]
                }
            }
        };

        var graphs =  $("space-graphs");
        var container = new Element("div");
        var title = new Element("h4");
        title.update(name);
        var canvas = new Element("canvas", {id: "canvas-" + id, height: 200, width: 200});

        container.appendChild(title);
        container.appendChild(canvas);
        graphs.appendChild(container);

        var pie = new Plotr.PieChart("canvas-" + id, options);
        pie.addDataset({
            used: [[0, used]],
            free: [[0, free]]
        });
        pie.render();
    };
    var partitions = $json;
    for (var i=0; i < partitions.length; i++) {
        var partition = partitions[i];
        drawPie(i, partition.mountpoint, partition.usage.percent / 100);
    }
    </script>
SPACE;

    }
}


?>
