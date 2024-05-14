<?php
/*
 * (c) 2017-2024 Siveo, http://http://www.siveo.net
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once("modules/pulse2/includes/utilities.php");
class AjaxFilterAudit extends AjaxFilter {
  function AjaxFilterAudit($url, $divid = "container", $params = array(), $formid = "") {
      $this->AjaxFilter($url, $divid, $params, $formid);
      $this->setRefresh(0);
  }

  function display($arrParam = array()) {
    global $conf;
    $root = $conf["global"]["root"];
    $maxperpage = $conf["global"]["maxperpage"];?>
    <form name="Form<?php echo $this->formid ?>" id="Form<?php echo $this->formid ?>" action="#" onsubmit="return false;">
      <div id="loader<?php echo $this->formid ?>">
          <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/>
      </div>
      <div id="searchSpan<?php echo $this->formid ?>" class="searchbox" style="float: right;">

      <div id="searchBest">
          <span class="searchfield">
            <!-- Hide Windows Updates checkbox -->
            <select style="position: relative; float: left" class="searchfieldreal" name="filter-type" id="filter-type" onchange="pushSearch<?php echo $this->formid ?>(); return false;" >
              <option value="status"><?php echo _T("Deployment Status", "xmppmaster");?></option>
              <option value="infos"><?php echo _T("Machine Inventory", "xmppmaster");?></option>
              <option value="relays"><?php echo _T("Relays", "xmppmaster");?></option>
            </select>
          </span>
          <span >
            <input type="text" class="searchfieldreal" name="param" id="param<?php echo $this->formid ?>"  />
            <img class="searchfield" src="graph/croix.gif" alt="suppression" style="position:relative; top : 4px;" onclick="document.getElementById('param<?php echo $this->formid ?>').value =''; pushSearch<?php echo $this->formid ?>(); return false;" />
          </span>
          <button style="margin-left:20px;" onclick="pushSearch<?php echo $this->formid ?>(); return false;"><?php echo _T("Search", "glpi");?></button>
        </div>
      </div>
      <br /><br /><br />

  </form>
  <div id="<?php echo $this->divid;?>" style="width:100%"></div>

  <script>
  var arr = {};
  updateSearch<?php echo $this->formid ?> = function(params=null) {
    if(params == null){
      var url = '<?php echo $this->url ?>'+'<?php echo $this->params ?>';

    }
    else
    {
        var url = '<?php echo $this->url ?>'+'<?php echo $this->params ?>'+'&filter='+params['filter']+'&criterion'+'='+params['value'];
    }
    jQuery('#<?php echo  $this->divid; ?>').load(url);
  }

  pushSearch<?php echo $this->formid ?> = function() {
      // Refresh the state of the hide_win_updates checkbox
      arr['filter'] = document.getElementById("filter-type").value;
      arr['value'] = encodeURIComponent(document.getElementById("param").value);
      updateSearch<?php echo $this->formid ?>(arr);
  }

  updateSearchParam<?php echo $this->formid ?> = function(filter, start, end, max) {

    arr['filter'] = document.getElementById("filter-type").value;
    arr['value'] = encodeURIComponent(document.getElementById("param").value);

    if(document.getElementById('maxperpage') != undefined)
        maxperpage = document.getElementById('maxperpage').value;
    else
      maxperpage = <?php echo $conf["global"]["maxperpage"];?>

    if(arr['value'])
      jQuery('#<?php echo  $this->divid; ?>').load('<?php echo  $this->url; ?>filter='+arr['filter']+'&criterion='+arr['value']+'&start='+start+'&end='+end+'&maxperpage='+maxperpage+'<?php echo  $this->params ?>');
    else
      jQuery('#<?php echo  $this->divid; ?>').load('<?php echo  $this->url; ?>start='+start+'&end='+end+'&maxperpage='+maxperpage+'<?php echo  $this->params ?>');
  }


pushSearch<?php echo $this->formid ?>();

  </script>

  <?php
  }
}


$ajax = new AjaxFilterAudit(urlStrRedirect("xmppmaster/xmppmaster/ajaxviewgrpdeploy"), "container", array(
  'login' => $_SESSION['login'],
  'cmd_id' => $_GET['cmd_id'],
  'gid' => $_GET['gid'],
  'hostname' => $_GET['hostname'],
  'uuid' => $_GET['uuid'],
  'title' => urlencode ( $_GET['title']),
  'startdeploy' => urlencode ( $_GET['start']),
  'endcmd' => urlencode ( $_GET['endcmd']),
  'startcmd' => urlencode ( $_GET['startcmd']),
  'previous'=>'viewlogs',
));

$sidemenu->display();
$ajax->display();
?>
