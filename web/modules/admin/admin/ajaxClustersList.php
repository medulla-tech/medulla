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

$clusters = xmlrpc_get_clusters_list($start, $maxperpage, $filter);

$editremoteconfigurationempty = new EmptyActionItem1(_("Edit config files"),"listconffile", "configg","computers","xmppmaster", "xmppmaster");
$editremoteconfiguration = new ActionItem(_("Edit config files"),"listconffile","config","computers", "xmppmaster", "xmppmaster");

$detailactionempty = new EmptyActionItem1(_("Relay Detail"),"relaystatusdetail", "logfileg","","xmppmaster", "xmppmaster");
$detailaction = new ActionItem(_("Relay Detail"),"relaystatusdetail", "logfile","","xmppmaster", "xmppmaster");

$quickaction = new ActionPopupItem(_("Detail actions"), "detailactions", "quick", "", "xmppmaster", "xmppmaster", "", "620");
$quickactionempty = new EmptyActionItem1(_("Detail actions"), "detailactions", "quickg", "", "xmppmaster", "xmppmaster");

$consoleaction = new ActionPopupItem(_("Console Relay"), "consolerelay", "console", "", "xmppmaster", "xmppmaster");
$consoleactionempty = new EmptyActionItem1(_("Console Relay"), "consolerelay", "consoleg", "", "xmppmaster", "xmppmaster");
$switchoffaction = new ActionPopupItem(_("Switch"), "switchrelay", 'stop', "", "xmppmaster", "xmppmaster");
$switchonaction = new ActionPopupItem(_("Switch"), "switchrelay", 'start', "", "xmppmaster", "xmppmaster");
$switchemptyaction = new EmptyActionItem1(_("Switch"), "switchrelay", 'stopg', "", "xmppmaster", "xmppmaster");

$reconfigureaction = new ActionPopupItem(_("Reconfigure Machines"), "reconfiguremachines", 'restart', "nopropagate", "xmppmaster", "xmppmaster");
$reconfigureemptyaction = new EmptyActionItem1(_("Reconfigure Machines"), "reconfiguremachines", 'restartg', "nopropagate", "xmppmaster", "xmppmaster");

$qalisteaction = new ActionItem(_("QA Launched"), "qalaunched", 'inventory', "", "xmppmaster", "xmppmaster");

$vncaction = new ActionPopupItem(_("Remote control"), "vnc_client", "guaca", "computer", "base", "computers");
$vncemptyaction = $vncClientActiongriser = new EmptyActionItem1(_("Remote control"), "vnc_client", "guacag", "computer", "base", "computers");

$packageaction = new ActionItem(_("Packages List"), "packageslist", 'package', "", "xmppmaster", "xmppmaster");
$packageemptyaction = new EmptyActionItem1(_("Packages List"), "packageslist", 'packageg', "", "xmppmaster", "xmppmaster");

$row = 0;
$params = [];

if($clusters['total'] > 0){
foreach($clusters['datas']['hostname'] as $key=>$array){
  $params[] = [
    'id' => $clusters['datas']['id'][$row],
    'name'=> $clusters['datas']['name'][$row],
    'description' => $clusters['datas']['description'][$row],
  ];

  $clusters['datas']['id'][$row] = '<span class="cluster-clickable">'.$clusters['datas']['id'][$row].'</span>';
  $clusters['datas']['name'][$row] = '<span class="cluster-clickable">'.$clusters['datas']['name'][$row].'</span>';
  $clusters['datas']['description'][$row] = '<span class="cluster-clickable">'.$clusters['datas']['description'][$row].'</span>';

  $row++;
}
echo '<div id="switchresult"></div>';
$n = new OptimizedListInfos( $clusters['datas']['name'], _T("Clusters", "xmppmaster"));
$n->setMainActionClasses($clusters['datas']['enabled_css']);
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $clusters['datas']['description'], _T("Description", "xmppmaster"));
$n->addExtraInfo( $clusters['datas']['nb_ars'], _T("Associated relays", "xmppmaster"));
$n->setTableHeaderPadding(0);
$n->setItemCount($clusters['total']);
$n->setNavBar(new AjaxNavBar($clusters['total'], $filter, "updateSearchParamformRunning"));

$n->setParamInfo($params);
$n->start = 0;
$n->end = $clusters['total'];

$n->display();

}
else{
  echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
  echo '<thead>';
  echo '<tr>';
  echo '<td>Clusters Xmpp</td>';

  echo '<td>Description</td>';
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
jQuery(".cluster-clickable").on("click", function(){
  jQuery("#paramformRunning").val(jQuery(this).text());
  pushSearchformRunning();
});
</script>
