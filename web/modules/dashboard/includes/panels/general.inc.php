<?php
/*
 * (c) 2012 Mandriva, http://www.mandriva.com
 * (c) 2019 siveo, http://www.siveo.net/
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

include_once("modules/dashboard/includes/panel.class.php");?>
<script src="modules/dashboard/graph/js/line.js"></script>
<?php $options = array(
    "class" => "GeneralPanel",
    "id" => "general",
    "refresh" => 3600,
    "title" => _T("General", "dashboard"),
);

class GeneralPanel extends Panel {

    function display_content() {
        $load = json_encode($this->data['load']);
        $memory = json_encode($this->data['memory']);
        $free_text = _T("free", "dashboard");
        $used_text = _T("used", "dashboard");
        echo '<p><strong>' . $this->data['hostname'] . '</strong> ' . _T('on') . ' <strong>' . $this->data['dist'][0] . ' ' . $this->data['dist'][1] . '</strong></p>
        <p><strong>' . _('Uptime') . '</strong> : ' . $this->data['uptime'] . '</p>
        <div><strong>' . _T('Load') . '</strong>
        <div id="load-graph"></div>
        </div>
        <div><strong>' . _T('RAM') . '</strong>
        <div id="ram-graph"></div>
        </div>';

        echo <<< GENERAL
<script>

  var load = $load;
  load = load.reverse();
  var n = load.length;
  var datas = [];
  for(i =0; i < n; i++)
  {
    datas.push({"x": i, "y":load[i]})
  }
  lineChart("load-graph",datas)

  var memory = $memory;
  function splitMem(valueToSplit)
  {
    var result = [];

    if(valueToSplit.endsWith("GB"))
      result = valueToSplit.split("GB");
    else if(valueToSplit.endsWith("MB"))
    {
      result = valueToSplit.split("MB");
      result[0] = (result[0] / 1000);
    }
    return result[0];
  }

  ram_free = parseFloat(splitMem(memory.free)) + parseFloat(splitMem(memory.available));
  ram_free = parseFloat(ram_free.toFixed(1))
  ram_used = parseFloat(splitMem(memory.used));
  ram_used = parseFloat(ram_used.toFixed(1));

  var datas = [
    {"label":"$free_text ", "value": ram_free,"unit":"GB"},
    {"label":"$used_text ", "value": ram_used,"unit":"GB"},
    ];
  donut("ram-graph", datas, "Total", memory.total)
</script>
GENERAL;
    }
}

?>
