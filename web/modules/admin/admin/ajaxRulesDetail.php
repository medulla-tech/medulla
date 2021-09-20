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

$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$maxperpage = (isset($_GET['maxperpage'])) ? htmlentities($_GET['maxperpage']) : 0;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$rules = xmlrpc_get_relays_for_rule($_GET['id'], $start, $maxperpage, $filter);
$total = $rules['total'];
$params = [];
$cssArray = [];


$editAction = new ActionItem(_("Edit rule"), "editRelayRule", "edit", "", "admin", "admin");
$raiseAction = new ActionItem(_T("Raise Rule", "admin"),"moveRelayRule","up","", "admin", "admin", "", "raise");
$lowerAction = new ActionItem(_T("Lower Rule", "admin"),"moveRelayRule","down","", "admin", "admin", "", "down");
$deleteAction = new ActionItem(_T("Delete Rule", "admin"),"deleteRelayRule","delete","", "admin", "admin");

foreach($rules['datas']['hostname'] as $id=>$key){
  $params[] = [
    'id' => $rules['datas']['relay_id'][$id],
    'hostname' => $rules['datas']['hostname'][$id],
    'enabled' => $rules['datas']['enabled'][$id],
    'rule_id' => $rules['datas']['id'][$id],
    'rule' => $rules['datas']['rule_id'][$id],
    'subject' => $rules['datas']['subject'][$id],
    'prev_action' => 'rulesDetail',
    'name' => htmlentities($_GET['name'])
  ];
  $cssArray[] = ($rules['datas']['enabled'][$id] == 1) ? "machineNamepresente" : "machineName";

  $editActions[] = $editAction;
  $deleteActions[] = $deleteAction;
  $lowerActions[] = $lowerAction;
  $raiseActions[] = $raiseAction;
}

$n = new OptimizedListInfos( $rules['datas']['hostname'], _T("Relay Server", "admin"));
$n->disableFirstColumnActionLink();
$n->setMainActionClasses($cssArray);
$n->addExtraInfo($rules['datas']['order'], _T("Order", "admin"));
$n->addExtraInfo($rules['datas']['subject'], _T("Subject", "admin"));
$n->setParamInfo($params);

$n->addActionItemArray($raiseActions);
$n->addActionItemArray($lowerActions);
$n->addActionItemArray($editActions);
$n->addActionItemArray($deleteActions);
$n->start = 0;
$n->end = $total;
$navbar = new AjaxNavBar($total, $filter);
$n->setItemCount($total);
$n->setNavBar($navbar);
$n->display();
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
