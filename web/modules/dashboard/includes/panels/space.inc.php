<?php

/*
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

var dataset = $json;
dataset.forEach(function(d,i){
  var tmp = [
    {"label":"$free","value":parseFloat(dataset[i].usage.free.split("GB")[0]),"unit":"GB"},
    {"label":"$used","value":parseFloat(dataset[i].usage.used.split("GB")[0]),"unit":"GB"},
  ];
  jQuery("#spaceChart").append("<div id='spaceChart"+i+"'></div>");
  donut("spaceChart"+i, tmp, dataset[i].mountpoint, dataset[i].usage.total);
})

</script>
SPACE;
    }

}

?>

<style>
  #spaceChart svg{
    margin-left:-11px;
  }
</style>
