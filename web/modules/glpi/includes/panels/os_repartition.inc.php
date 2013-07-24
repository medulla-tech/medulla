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

require_once("modules/pulse2/includes/xmlrpc.inc.php");
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");
include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");

$options = array(
    "class" => "os_repartitionPanel",
    "id" => "osrepartition",
    "refresh" => 960,
    "title" => _T("Operating systems", "dashboard"),
);


  
class os_repartitionPanel extends Panel {

    function display_content() {
        
        // Declare OS classes
        $osClasses = array(
            'other',
            'Microsoft%Windows%7',
            'Microsoft%Windows%XP',
            'otherw'
        );
        
        $osLabels = array(
            _T('Other','glpi'),
            'Windows 7',
            'Windows XP',
            _T('Other Windows','glpi')
        );

        $osCount = array();
      
        for ($i = 0; $i< count($osClasses) ; $i++){
            $osCount[] = getMachineByOsLike($osClasses[$i],1);
            $osLabels[$i] .= ' ('.$osCount[$i].')';
        }
        
        $n = count($osCount);

        // Treating osCount for adapting to raphaeljs
        for ($i = 0; $i < $n ; $i++){
            if ($osCount[$i] == 0){
                unset($osCount[$i]);
                unset($osLabels[$i]);
                
            }
            elseif ($osCount[$i]/array_sum($osCount) < 0.015)
                $osCount[$i] = 0.015/(1-0.015)*(array_sum($osCount)-$osCount[$i]);
        }
        $osLabels = json_encode(array_values($osLabels));
        $osCount = json_encode(array_values($osCount));
        
        
        /*$links = json_encode(array("#",
                "main.php?module=base&submod=computers&action=computersgroupcreator&req=glpi&add_param=OS&request=stored_in_session&id=&value=Microsoft Windows 7 *",
                "main.php?module=base&submod=computers&action=computersgroupcreator&req=glpi&add_param=OS&request=stored_in_session&id=&value=Microsoft Windows XP *",
                    "#"));  DYNGROUP LINKS*/ 
        $urlRedirect = json_encode(urlStrRedirect("base/computers/createOSStaticGroup"));
        $createGroupText = json_encode(_T("Create a group", "glpi"));
        $links = json_encode(array(
                "main.php?module=base&submod=computers&action=createOSStaticGroup&os=other", // Static group links
                "main.php?module=base&submod=computers&action=createOSStaticGroup&os=Microsoft Windows 7",
                "main.php?module=base&submod=computers&action=createOSStaticGroup&os=Microsoft Windows XP",
                "main.php?module=base&submod=computers&action=createOSStaticGroup&os=otherw"
            ));

        echo <<< SPACE
        <div id="os-graphs" style="height:250px;"></div>
        <script type="text/javascript">
        var    r = Raphael("os-graphs"),
                radius = 70,
                margin = 60,
                x = 100,
                y = 80;
        

        var data = $osCount,
            createGroupText = $createGroupText,
            legend = $osLabels,
            colors = ["#000","#73d216","#ef2929","#003399"],
            href = $links,
            title = 'OS Repartition';
        
        /*r.text(5, y - radius - 10, title)
         .attr({ font: "12px sans-serif" })
         .attr({ "text-anchor": "start" });*/
        data = getPercentageData(data);
        pie = r.piechart(x, y + 5, radius, data,
                   {colors: colors})
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
        
        r.setSize(200, (radius * 1 + margin) + 50);
        // Legend
        jQuery('#os-graphs').append('<ul></ul>');
        for (var i = 0; i < legend.length; i++) {
            jQuery('#os-graphs ul').append(
                '<li style="color: ' + colors[i]  + '"><span style="color: #000">' + legend[i]
                + '<a href="' + href[i] + '"><img title="' + createGroupText +
                '" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a></span></li>'
            );
        }
        </script>
SPACE;
    }
}

?>
