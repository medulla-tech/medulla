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
?>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/5.7.0/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3pie@0.2.1/d3pie/d3pie.min.js"></script>

<?php
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
      $osLabels[] = $os['os'].' '.$os['version'];
      $osCount[] = (int)$os['count'];

      $links[] = $urlRedirect.'&os='.$os['os'].'&version='.$os['version'];
    }

    $osLabels = json_encode(array_values($osLabels));
    $osCount = json_encode(array_values($osCount));
    $links = json_encode(array_values($links));

    $createGroupText = json_encode(_T("Create a group", "glpi"));
        echo <<< SPACE


        <div id="pieChart"></div>
        <ul id="os-list"></ul>
        <script>

jQuery(function(){

  var labels = $osLabels;
  var count = $osCount;
  var links = $links;

  var datapoints = [];

  for(var i =0; i< labels.size(); i++)
  {
    datapoints.push({value: count[i], label:labels[i], href:links[i]})
  }

  pie = new d3pie("pieChart", {
    "size": {
		"canvasHeight": 205,
		"canvasWidth": 205,
		"pieOuterRadius": "100%"
	},
	data: {
		content: datapoints
	},
  "labels": {
    "outer": {
  		"format": "none",
  		"pieDistance": 10
		},
    "inner": {
	    "format": "none",
		},
  },
  "tooltips": {
		"enabled": true,
		"type": "placeholder",
		"string": "{label}: {value}, {percentage}%"
	},
	callbacks: {
		onClickSegment: function(a) {
			window.location.href =a.data.href;
		}
	}
});

for(var i =0; i< labels.size(); i++)
{
  jQuery("#os-list").append("<li>"+labels[i]+" <a href='"+links[i]+"'> <img title='Créer un groupe' style='height: 10px; padding-left: 3px;' src='img/machines/icn_machinesList.gif'></a></li>")
}


        })
        </script>
SPACE;
    }

}

?>
<style>
  #pieChart svg{
    /*The width of the piechart is ajusted after its generation because the toolstips are truncated*/
    width:350px;
  }
</style>
