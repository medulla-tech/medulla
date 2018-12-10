<?php

/**
 * (c) 2012 Mandriva, http://www.mandriva.com
 * (c) 2018 Siveo, http://www.siveo.net
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
require_once("modules/pulse2/includes/xmlrpc.inc.php");
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");
include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");

$options = array(
  "class" => "os_repartitionPanel",
  "id" => "osrepartition",
  "refresh" => 960,
  "title" => _T("Operating systems", "glpi"),
);

class os_repartitionPanel extends Panel {
  function display_content() {
    $urlRedirect = urlStrRedirect("base/computers/createOSStaticGroup");
    $pcs = xmlrpc_get_os_for_dashboard();

    $osLabels = [];
    $osCount = [];
    $links = [];
    $cumul = 0;
    $n = count($pcs);
    for($i =0; $i < $n; $i++)
    {
      $cumul += (int)$pcs[$i]['count'];
    }
    foreach ($pcs as $os){
      //$cumul = $cumul + (int)$os['count'];
      if((int)$os['count'] == 0)
      {
        unset($os);
      }
      $osLabels[] = $os['os'].' '.$os['version'].' ('.$os['count'].')';
      $osCount[] = (int)$os['count'];

      $links[] = $urlRedirect.'&os='.$os['os'].'&version='.$os['version'];
    }

    echo 'total : '.$cumul.'<br />';
    $osLabels = json_encode(array_values($osLabels));
    $osCount = json_encode(array_values($osCount));
    $links = json_encode(array_values($links));


    $createGroupText = json_encode(_T("Create a group", "glpi"));
        echo <<< SPACE
        <div id="os-graphs"></div>
        <script type="text/javascript">
            var r = Raphael("os-graphs"),
                radius = 70,
                margin = 100,
                x = 100,
                y = 75;

            var data = $osCount,
                createGroupText = $createGroupText,
                legend = $osLabels,
                //Add "#000-color-color" into the colors variable if all the os are not displayed
                //colors = ["000-#000000-#666665","000-#73d216-#42780D","000-#ef2929-#A31A1A","000-#003399-#0251ED","000-#7e1282-#c98fcb","000-#b36919-#e8c6a2","000-#2eb9f3-#4297ba","000-#168eff-#28c96c","000-#a9751a-#cdbda1","000-#72ed62-#72ed62","000-#000000-#666665","000-#000000-#666665","000-#000000-#666665"],
                href = $links,
                title = 'OS Repartition';

            /*r.text(5, y - radius - 10, title)
             .attr({ font: "12px sans-serif" })
             .attr({ "text-anchor": "start" });*/
            data = getPercentageData(data);

            pie = r.piechart(x, y + 5, radius, data,
                       {//colors: colors,
                       legend:$osLabels,
                       href:$links,
                       legendpos: "south"})
             .hover(function () {
                this.sector.stop();
                this.sector.animate({ transform: 's1.1 1.1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

                if (this.label) {
                    this.label[0].stop();
                    this.label[0].attr({ r: 7.5 });
                    this.label[1].attr({ "font-weight": 800 });
                }
                //jQuery('#os-graphs ul:first').find('li')
             }, function () {
                this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

                if (this.label) {
                    this.label[0].animate({ r: 5 }, 500, "bounce");
                    this.label[1].attr({ "font-weight": 400 });
                }
             });

            y += (radius * 2) + margin + 5;

            r.setSize(200, (radius * 1 + margin) + legend.size()*20);
            // Legend
            /*jQuery('#os-graphs').append('<ul></ul>');

            for (var i = 0; i < legend.length; i++) {
                jQuery('#os-graphs ul').append(
                    '<li style="color: ' + colors[i].split('-')[1]  + ';"><span style="color: #000">' + legend[i]
                    '<li><span>' + legend[i]
                    + '<a href="' + href[i] + '"><img title="' + createGroupText +
                    '" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a></span></li>'
                );
            }*/
        </script>
        <style type="text/css">
            #os-graphs ul {
                margin: 0px;
                padding-left: 28px;
            }
            #os-graphs li {
                list-style: none;
                font-size: 13px;
            }
            #os-graphs li:before {
                content: "•";
                font-size: 20px;
                vertical-align: bottom;
                line-height: 16px;
                margin-right: 3px;
            }
        </style>
SPACE;
    }

}

?>
