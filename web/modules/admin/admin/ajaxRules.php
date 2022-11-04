<?php
/*
 * (c) 2020-2021 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 *
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

global $maxperpage;

if(isset($_GET['mod'], $_GET['id']))
{
  if($_GET['mod'] == "raise" || $_GET['mod'] == "down"){
    $_GET['id'] = htmlentities($_GET['id']);
    $mod = htmlentities($_GET['mod']);
    $name = htmlentities($_GET['name']);

    $result = xmlrpc_order_relay_rule($mod, $_GET['id']);
    if($result['status'] == "success"){
      new NotifyWidgetSuccess(_T('The rule '.$name.' has been '.$mod.'ed', "admin"));
    }
    else{
      new NotifyWidgetFailure(_T($result['message'], "admin"));
    }
  }
  else{
    new NotifyWidgetFailure(_T("Unknown action", "admin"));
  }
}

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$end = (isset($_GET['maxperpage'])) ? $_GET['maxperpage'] : $maxperpage;
$filter = (isset($_GET['filter'])) ? $_GET['filter'] : "";

$rulesList = xmlrpc_get_rules_list($start, $end, $filter);

$raiseAction = new ActionItem(_T("Raise Rule", "admin"),"moveRule","up","", "admin", "admin", "", "raise");
$lowerAction = new ActionItem(_T("Lower Rule", "admin"),"moveRule","down","", "admin", "admin", "", "down");
$listAction = new ActionItem(_T("Rule Detail", "admin"),"rulesDetail","inventory","", "admin", "admin");
$newAction = new ActionItem(_T("New Rule", "admin"),"rules_tabs","addbootmenu","tab", "admin", "admin", "newRelayRule");
$raiseActions = [];
$lowerActions = [];
$listActions = [];
$newActions = [];
$params = [];

$is_default = false;
foreach($rulesList['datas']['name'] as $key=>$array){
  $params[] = [
    'id' => $rulesList['datas']['id'][$key],
    'name'=> $rulesList['datas']['name'][$key],
    'description' => $rulesList['datas']['description'][$key],
    'prev_action' => 'rules'
  ];

  $color = ($is_default) ? "red" : "green";

  $rulesList['datas']['id'][$key] = '<span style="color:'.$color.';" class="clickable">'.$rulesList['datas']['id'][$key].'</span>';
  $rulesList['datas']['name'][$key] = '<span style="color:'.$color.';" class="clickable">'.$rulesList['datas']['name'][$key].'</span>';
  $rulesList['datas']['description'][$key] = '<span style="color:'.$color.';" class="clickable">'.$rulesList['datas']['description'][$key].'</span>';
  $rulesList['datas']['level'][$key] = '<span style="color:'.$color.';" class="clickable">'.$rulesList['datas']['level'][$key].'</span>';


  $raiseActions[] = $raiseAction;
  $lowerActions[] = $lowerAction;
  $listActions[] = $listAction;
  $newActions[] = $newAction;

  if($params[$key]['name'] == 'default')
    $is_default = true;
}

if($rulesList['total'] > 0){
  $n = new OptimizedListInfos( $rulesList['datas']['name'], _T("Rule", "admin"));
  $n->disableFirstColumnActionLink();
  $n->addExtraInfo( $rulesList['datas']['description'], _T("Description", "admin"));
  $n->addExtraInfo( $rulesList['datas']['level'], _T("Level", "admin"));
  $n->addExtraInfo( $rulesList['datas']['count'], _T("Associated rules", "admin"));
  $n->addActionItemArray($raiseActions);
  $n->addActionItemArray($lowerActions);
  $n->addActionItemArray($listActions);
  $n->addActionItemArray($newActions);
  $n->setTableHeaderPadding(0);
  $n->setItemCount($rulesList['total']);
  $n->setNavBar(new AjaxNavBar($rulesList['total'], $filter, "updateSearchParamformRunning"));

  $n->setParamInfo($params);
  $n->start = 0;
  $n->end = $rulesList['total'];
  $n->display();
}
else{
  echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
  echo '<thead>';
  echo '<tr>';
  echo '<td>'._T("Rule", "admin").'</td>';
  echo '<td>'._T("Description", "admin").'</td>';
  echo '<td>'._T("Level", "admin").'</td>';
  echo '</tr>';
  echo '</thead>';
  echo '</table>';
}
?>

<style>
  .clickable{
    cursor: pointer;
  }
</style>

<script>
jQuery(".clickable").on("click", function(){
  jQuery("#paramformRunning").val(jQuery(this).text());
  pushSearchformRunning();
});

jQuery(".up:first").hide();
jQuery(".down:last").hide();
jQuery(".up:last").css("margin-right", "35px");
</script>
