<?php
/*
 * (c) 2015-2020 Siveo, http://www.siveo.net
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
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

$relays = xmlrpc_get_xmpprelays_list($start, $maxperpage, $filter, 'all');

$editremoteconfigurationempty = new EmptyActionItem1(_("Edit config files"),"listconffile", "configg","computers","xmppmaster", "xmppmaster");
$editremoteconfiguration = new ActionItem(_("Edit config files"),"listconffile","config","computers", "xmppmaster", "xmppmaster");

$detailactionempty = new EmptyActionItem1(_("Relay Detail"),"relaystatusdetail", "logfileg","","xmppmaster", "xmppmaster");
$detailaction = new ActionItem(_("Relay Detail"),"relaystatusdetail", "logfile","","xmppmaster", "xmppmaster");

$quickaction = new ActionPopupItem(_("Quick action"), "deployquick", "quick", "computer", "xmppmaster", "xmppmaster");
$quickactionempty = new EmptyActionItem1(_("Quick action"), "deployquick", "quick", "computer", "xmppmaster", "xmppmaster");

$consoleaction = new ActionPopupItem(_("Console Relay"), "consolerelay", "console", "", "xmppmaster", "xmppmaster");
$consoleactionempty = new EmptyActionItem1(_("Console Relay"), "consolerelay", "consoleg", "", "xmppmaster", "xmppmaster");
$raw = 0;
$params = [];
if($relays['total'] > 0){
foreach($relays['datas']['hostname'] as $key=>$array){
  $params[] = [
    'id' => $relays['datas']['id'][$raw],
    'hostname' => $relays['datas']['hostname'][$raw],
    'enabled' => $relays['datas']['enabled'][$raw],
    'enabled_css' => $relays['datas']['enabled_css'][$raw],
    'jid'=> $relays['datas']['jid'][$raw],
    'cluster_name' => $relays['datas']['cluster_name'][$raw],
    'cluster_description' => $relays['datas']['cluster_description'][$raw],
    'classutil' => $relays['datas']['classutil'][$raw],
    'macaddress'=> $relays['datas']['macaddress'][$raw],
    'ip_xmpp' => $relays['datas']['ip_xmpp'][$raw],
    'agenttype'=> 'relayserver'
  ];

  $relays['datas']['hostname'][$raw] = '<span class="relay-clickable">'.$relays['datas']['hostname'][$raw].'</span>';
  $relays['datas']['jid'][$raw] = '<span class="relay-clickable">'.$relays['datas']['jid'][$raw].'</span>';
  $relays['datas']['cluster_name'][$raw] = '<span class="relay-clickable">'.$relays['datas']['cluster_name'][$raw].'</span>';
  $relays['datas']['cluster_description'][$raw] = '<span class="relay-clickable">'.$relays['datas']['cluster_description'][$raw].'</span>';
  $relays['datas']['classutil'][$raw] = '<span class="relay-clickable">'.$relays['datas']['classutil'][$raw].'</span>';
  $relays['datas']['macaddress'][$raw] = '<span class="relay-clickable">'.$relays['datas']['macaddress'][$raw].'</span>';
  $relays['datas']['ip_xmpp'][$raw] = '<span class="relay-clickable">'.$relays['datas']['ip_xmpp'][$raw].'</span>';

  if ($relays['datas']['enabled'][$raw]){
    $configActions[] =$editremoteconfiguration;
    $consoleActions[] = $consoleaction;
  }
  else{
    $configActions[] =$editremoteconfigurationempty;
    $consoleActions[] = $consoleactionempty;
  }
  $switchActions[] = new CheckActionItem(_("Switch"), "switch", $relays['datas']['mandatory'][$raw], $relays['datas']['switchonoff'][$raw], "", "switchrelay","xmppmaster", "xmppmaster");
  $raw++;
}
echo '<div id="switchresult"></div>';
$n = new OptimizedListInfos( $relays['datas']['hostname'], _T("Relays Xmpp", "xmppmaster"));
$n->setMainActionClasses($relays['datas']['enabled_css']);
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $relays['datas']['jid'], _T("Jid", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['cluster_name'], _T("Cluster Name", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['cluster_description'], _T("Cluster Description", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['classutil'], _T("Class Util", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['macaddress'], _T("Mac Address", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['ip_xmpp'], _T("Xmpp IP", "xmppmaster"));


$n->setTableHeaderPadding(0);
$n->setItemCount($relays['total']);
$n->setNavBar(new AjaxNavBar($relays['total'], $filter, "updateSearchParamformRunning"));
$n->addActionItemArray($switchActions);
$n->addActionItemArray($configActions);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $relays['total'];

$n->display();

}
else{
  echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
  echo '<thead>';
  echo '<tr>';
  echo '<td>Relays Xmpp</td>';
  echo '<td>Jid</td>';
  echo '<td>Cluster Name</td>';
  echo '<td>Cluster Description</td>';
  echo '<td>Class Util</td>';
  echo '<td>Mac Address</td>';
  echo '<td>Xmpp Ip</td>';
  echo '</tr>';
  echo '</thead>';
  echo '</table>';
}
?>

<style>
  .relay-clickable{
    cursor: pointer;
  }
</style>

<script>
jQuery(".relay-clickable").on("click", function(){
  jQuery("#paramformRunning").val(jQuery(this).text());
  pushSearchformRunning();
});
</script>
