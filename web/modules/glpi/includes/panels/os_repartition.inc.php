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

$options = array(
    "class" => "os_repartitionPanel",
    "id" => "osrepartition",
    "refresh" => 960,
    "title" => _T("Operating systems", "dashboard"),
);


  
class os_repartitionPanel extends Panel {

    function display_content() {
        
        // Get All OS Repartition for the user locations
        $locations = getUserLocations();

        // Declare classes from higher priority to lower (note that Microsoft Windows is latest)
        $osClasses = array(
            'Other',
            'Microsoft Windows 7',
            'Microsoft Windows XP',
            'Microsoft Windows'
        );
        
        $osLabels = array(
            _T('Other','glpi'),
            'Windows 7',
            'Windows XP',
            _T('Other Windows','glpi')
        );

        $osCount = array(0,0,0,0);

        foreach ($locations as $location){
            
            $result = getRestrictedComputersList(0,-1,array('location'=>$location['uuid']), False);
            foreach ($result as $info){
                $gotOS = False;
                for ($i = 1; $i< count($osClasses) ; $i++){
                    $os = str_replace('&nbsp;',' ',htmlentities($info[1]['os']));
                    if (stripos($os,$osClasses[$i]) !== False){
                        $osCount[$i]++;
                        $gotOS = True;
                        break;
                    }
                }
                // If no os got, add it to others
                if (!$gotOS)
                    $osCount[0]++;
            }
        }
         
        for ($i = 0; $i<count($osLabels); $i++)
            $osLabels[$i] .= ' ('.$osCount[$i].')';
        
        
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

        echo <<< SPACE
        <div id="os-graphs" style="height:250px;"></div>
        <script type="text/javascript">
        var    r = Raphael("os-graphs"),
                radius = 70,
                margin = 60,
                x = 100,
                y = 80;
        

        var data = $osCount,
            legend = $osLabels,
            colors = ["#000","#73d216","#ef2929","#003399"],
            title = 'OS Repartition';
        
        /*r.text(5, y - radius - 10, title)
         .attr({ font: "12px sans-serif" })
         .attr({ "text-anchor": "start" });*/
        data = getPercentageData(data);
        r.piechart(x, y + 5, radius, data,
                   {legend: legend,
                    legendpos: "south",
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
        
        
        r.setSize(200, 3 * (radius * 2 + margin) + 10);
        </script>
SPACE;
    }
}

?>
