<?php

/*
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
include_once("modules/dashboard/includes/panel.class.php");
?>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/5.7.0/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3pie@0.2.1/d3pie/d3pie.min.js"></script>

<?php $options = array(
    "class" => "SpacePanel",
    "id" => "space",
    "refresh" => 3600,
    "title" => _T("Disk usage", "dashboard"),
);

class SpacePanel extends Panel {

    function display_content() {

        $json = json_encode($this->data['partitions']);
        $used = _T("used");
        $free = _T("free");

        echo <<< SPACE
        <div id="spaceChart"></div>
        <script>
jQuery(function(){

  function donut(datas, index){
    var pie = new d3pie("spaceChart"+index, {
  	"header": {
  		"title": {
  			"text": datas.mountpoint,
  			"fontSize": 11,
  			"font": "Arial, Verdana, Lucida, Geneva, Helvetica, sans-serif"
  		},
  		"subtitle": {
  			"text": datas.usage.total,
  			"color": "#999999",
  			"fontSize": 11,
  			"font": "Arial, Verdana, Lucida, Geneva, Helvetica, sans-serif"
  		},
  		"location": "pie-center",
  		"titleSubtitlePadding": 1
  	},
  	"size": {
  		"canvasHeight": 200,
  		"canvasWidth": 200,
  		"pieInnerRadius": "65%",
  		"pieOuterRadius": "60%"
  	},
  	"data": {
  		"sortOrder": "label-desc",
  		"content": [
  			{
  				"label": "Used",
  				"value": parseFloat(datas.usage.used.split('GB')[0]),
  				"color": "#c55252"
  			},
  			{
  				"label": "Free",
  				"value":  parseFloat(datas.usage.free.split('GB')[0]),
  				"color": "#509a4e"
  			}
  		]
  	},
  	"labels": {
  		"outer": {
  			"pieDistance": 5
  		},
  		"inner": {
  			"format": "value"
  		},
  		"mainLabel": {
  			"fontSize": 11,
        "font": "Arial, Verdana, Lucida, Geneva, Helvetica, sans-serif"
  		},
  		"percentage": {
  			"color": "#999999",
  			"fontSize": 11,
        "font": "Arial, Verdana, Lucida, Geneva, Helvetica, sans-serif",
  			"decimalPlaces": 1
  		},
  		"value": {
  			"color": "#000000",
  			"fontSize": 11,
        "font":"Arial, Verdana, Lucida, Geneva, Helvetica, sans-serif"
  		},
  		"lines": {
  			"enabled": true,
  			"style": "straight",
  			"color": "#777777"
  		},
  		"truncation": {
  			"enabled": true
  		}
  	},
  	"tooltips": {
  		"enabled": true,
  		"type": "placeholder",
  		"string": "{label}: {value} Gb, {percentage}%",
  		"styles": {
  			"fadeInSpeed": 255,
  			"borderRadius": 9,
  			"padding": 8,
        "font": "Arial, Verdana, Lucida, Geneva, Helvetica, sans-serif",
        "fontSize": 11
  		}
  	},
  	"effects": {
  		"pullOutSegmentOnClick": {
  			"effect": "linear",
  			"speed": 400,
  			"size": 8
  		}
  	},
  	"misc": {
  		"colors": {
  			"segmentStroke": "#ffffff"
  		},
  		"canvasPadding": {
  			"top": 0,
  			"right": 0,
  			"bottom": 0,
  			"left": 0
  		},
      "pieCenterOffset": {
			"y": -25
		}
  	}
  });

    return pie;
  }

  var dataset = $json;

  d3.select("#spaceChart")
    .selectAll("div")
    .data(dataset)
    .enter()
    .append("div")
    .attr('id', function(d, i){
      return "spaceChart"+i;
    })
    .attr('html',function(d, i){
      var tmp = donut(d,i);
      return jQuery(tmp.element).html();
    });

})

</script>
SPACE;
    }

}

?>

<style>
  #spaceChart svg{
    /*The width of the piechart is ajusted after its generation because the toolstips are truncated*/
    width:350px;
    height:150px;
    padding-top:-50px;
  }
</style>
