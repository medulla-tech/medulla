<?php
/*
 * (c) 2020 Siveo, http://www.siveo.net
 *
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/xmppmaster/includes/html.inc.php");
global $conf;

$get = $_GET;
unset($get['module']);
unset($get['submod']);
unset($get['action']);
unset($get['delete']);
unset($get['tab']);

$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$maxperpage = (isset($_GET['maxperpage'])) ? htmlentities($_GET['maxperpage']) : $conf["global"]["maxperpage"];
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;

$rules = xmlrpc_get_relay_rules(htmlentities($_GET['id']), $start, $maxperpage, $filter);

$editAction = new ActionItem(_T("Edit Rule", "admin"),"editRelayRule","edit","", "admin", "admin");
$raiseAction = new ActionItem(_T("Raise Rule", "admin"),"moveRelayRule","up","", "admin", "admin", "", "raise");
$lowerAction = new ActionItem(_T("Lower Rule", "admin"),"moveRelayRule","down","", "admin", "admin", "", "down");
$deleteAction = new ActionItem(_T("Delete Rule", "admin"),"deleteRelayRule","delete","", "admin", "admin");


$params = [];
$total = 0;

if($rules['status'] != "error"){
  $total = $rules['total'];

  foreach($rules['datas']['name'] as $key=>$array){
    //$actionEditClusters[] = $editcluster;
    $params[] = array_merge([
      //'id' => htmlentities($_GET['id']),
      'rule_id' => $rules['datas']['id'][$key],
      'name'=> $rules['datas']['name'][$key],
      'subject' => $rules['datas']['subject'][$key],
      'order' => $rules['datas']['order'][$key],
    ], $get);

    //$rulesList['datas']['id'][$key] = '<span class="clickable">'.$rulesList['datas']['id'][$key].'</span>';
    $rules['datas']['name'][$key] = '<span class="clickable">'.$rules['datas']['name'][$key].'</span>';
    $rules['datas']['subject'][$key] = '<span class="clickable">'.$rules['datas']['subject'][$key].'</span>';
    $rules['datas']['order'][$key] = '<span class="clickable">'.$rules['datas']['order'][$key].'</span>';

    $raiseActions[] = $raiseAction;
    $lowerActions[] = $lowerAction;
    $editActions[] = $editAction;
    $deleteActions[] = $deleteAction;
  }
}

if($total != 0){
  $n = new OptimizedListInfos( $rules['datas']['name'], _T("Rule", "xmppmaster"));
  $n->disableFirstColumnActionLink();
  $n->setParamInfo($params);
  $n->addExtraInfo($rules['datas']['order'], _T("Order", "admin"));
  $n->addExtraInfo($rules['datas']['subject'], _T("Subject", "admin"));
  //$n->addActionItemArray($raiseActions);
  //$n->addActionItemArray($lowerActions);
  $n->addActionItemArray($editActions);
  $n->addActionItemArray($deleteActions);
  $n->start = 0;
  $n->end = $total;
  $navbar = new AjaxNavBar($total, $filter);
  $n->setNavBar($navbar);
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
  jQuery("#param").val(jQuery(this).text());
  pushSearch();
});

jQuery(".up:first").hide();
jQuery(".down:last").hide();
jQuery(".up:last").css("margin-right", "35px");
</script>
