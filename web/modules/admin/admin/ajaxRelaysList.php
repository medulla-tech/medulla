<?php
/*
 * (c) 2015-2021 Siveo, http://www.siveo.net
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
require_once("modules/pkgs/includes/xmlrpc.php");

global $conf;

?>

<style>

.tooltip{   font-size:20px; }
.ui-tooltip {
                padding: 6px 4px 8px 4px;
                max-width: 600px;
                color: #ffffff;
                background-color: #000000;
                -moz-box-shadow: 4px 4px 10px #888;
                -webkit-box-shadow: 4px 4px 10px #888;
                box-shadow:4px 4px 6px #888;
                border-radius: 15px;}

.tooltip-content {
                    padding: 2px;
                    color: #FF00AA;
                    max-width: 800px;}

.ttabletr   {   margin:0;
                padding:0;
                background:none;
                border:none;
                border-collapse:collapse;
                border-spacing:0;
                background-image:none;}


.ttabletd   {   margin:0;
                padding:0;
                background:none;
                border:none;
                border-collapse:collapse;
                border-spacing:0;
                background-image:none;}

.ttable tr td{  margin:0;
                padding:0;
                background:none;
                border:none;
                border-collapse:collapse;
                border-spacing:0;
                background-image:none;
                font-size:.9em;
}
</style>

<script>

jQuery(function()
{
	 jQuery( function() {
      jQuery(".infomach").tooltip({
      position: { my: "left+15 center", at: "right center" },
          items: "[mydata]",
          content: function() {
              var element = jQuery( this );
              if ( element.is( "[mydata]" ) ) {
              console.log(element.attr('mydata'));
                  var text = element.attr('mydata');
                  return text;
              }

          }
      });
  } );

});

</script>

<?php
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

  $sharings = xmlrpc_pkgs_search_share(["login"=> $_SESSION["login"]]);
  if($sharings['config']['centralizedmultiplesharing'] == 1){
      $relays = get_list_ars_from_sharing($sharings['datas'],$start, $maxperpage,$_SESSION["login"],  $filter);
  }else{
    $relays = xmlrpc_get_xmpprelays_list($start, $maxperpage, $filter, 'all');
  }

$chaine = [];
$cn = [];
$datas = $relays['datas'];
foreach ($datas as $columns_name => $tabvalue){
    $chaine[$columns_name] = $columns_name;
}
for ($index = 0; $index < count($datas['publicclass'] ); $index++) {
    $chainestr ="<table class='ttable'>";
    foreach($datas as $mach => $value ){
        $chainestr .= "<tr class='ttabletr'><td class='ttabletd'>".$mach ."</td><td class='ttabletd'>: ".$value[$index]."</td></tr>";
    }

    $chainestr .= "</table>";
$cn[] = sprintf('<span class="infomach" mydata="%s">%s</pan>', $chainestr, $datas['hostname'][$index]);

}

//$editremoteconfigurationempty = new EmptyActionItem1(_("Edit config files"),"listconffile", "configg","computers","xmppmaster", "xmppmaster");
$editremoteconfigurationempty = new EmptyActionItem1(_("Edit config files"),"conffile", "configg","","admin", "admin");
//$editremoteconfiguration = new ActionItem(_("Edit config files"),"listconffile","config","computers", "xmppmaster", "xmppmaster");
$editremoteconfiguration = new ActionItem(_("Edit config files"),"conffile","config","", "admin", "admin");

$detailactionempty = new EmptyActionItem1(_("Relay Detail"),"relaystatusdetail", "logfileg","","admin", "admin");
$detailaction = new ActionItem(_("Relay Detail"),"relaystatusdetail", "logfile","","admin", "admin");

$quickaction = new ActionPopupItem(_("Detail actions"), "detailactions", "quick", "", "admin", "admin", "", "620");
$quickactionempty = new EmptyActionItem1(_("Detail actions"), "detailactions", "quickg", "", "admin", "admin");

$consoleaction = new ActionPopupItem(_("Console Relay"), "consolerelay", "console", "", "admin", "admin");
$consoleactionempty = new EmptyActionItem1(_("Console Relay"), "consolerelay", "consoleg", "", "admin", "admin");
$switchoffaction = new ActionPopupItem(_("Switch"), "switchrelay", 'stop', "", "admin", "admin");
$switchonaction = new ActionPopupItem(_("Switch"), "switchrelay", 'start', "", "admin", "admin");
$switchemptyaction = new EmptyActionItem1(_("Switch"), "switchrelay", 'stopg', "", "admin", "admin");

$reconfigureaction = new ActionPopupItem(_("Reconfigure Machines"), "reconfiguremachines", 'restart', "nopropagate", "admin", "admin");
$reconfigureemptyaction = new EmptyActionItem1(_("Reconfigure Machines"), "reconfiguremachines", 'restartg', "nopropagate", "admin", "admin");

$qalisteaction = new ActionItem(_("QA Launched"), "qalaunched", 'inventory', "", "admin", "admin");

$vncaction = new ActionPopupItem(_("Remote control"), "vnc_client", "guaca", "computer", "base", "computers");
$vncemptyaction = $vncClientActiongriser = new EmptyActionItem1(_("Remote control"), "vnc_client", "guacag", "computer", "base", "computers");

$packageaction = new ActionItem(_("Packages List"), "packageslist", 'package', "", "admin", "admin");
$packageemptyaction = new EmptyActionItem1(_("Packages List"), "packageslist", 'packageg', "", "admin", "admin");

$relayRulesAction = new ActionItem(_("Relay Rules"), "rules_tabs", 'inventory', "", "admin", "admin");

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
    'agenttype'=> 'relayserver',
    'switch'=> $relays['datas']['switchonoff'][$raw],
    'vnctype' => (in_array("guacamole", $_SESSION["supportModList"])) ? "guacamole" : ((web_def_use_no_vnc()==1) ? "novnc" : "appletjava")
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
    $reconfigurationActions[] = $reconfigureaction;
    $quickActions[] = $quickaction;
    $vncActions[] = $vncaction;
    $packagesAction[] = $packageaction;
  }
  else{
    $configActions[] =$editremoteconfigurationempty;
    $consoleActions[] = $consoleactionempty;
    $reconfigurationActions[] = $reconfigureemptyaction;
    $quickActions[] = $quickactionempty;
    $vncActions[] = $vncemptyaction;
    $packagesAction[] = $packageemptyaction;
  }
  $relayRulesActions[] = $relayRulesAction;

  if($relays['datas']['mandatory'][$raw] == 1){
    $switchActions[] = $switchemptyaction;
  }
  else if($relays['datas']['switchonoff'][$raw] == 1)
  {
    $switchActions[] = $switchoffaction;
  }
  else if($relays['datas']['switchonoff'][$raw] == 0)
  {
    $switchActions[] = $switchonaction;
  }
  $qalistActions[] = $qalisteaction;
  $raw++;
}
echo '<div id="switchresult"></div>';
$n = new OptimizedListInfos( $cn, _T("Relays Xmpp", "admin"));
$n->setMainActionClasses($relays['datas']['enabled_css']);
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $relays['datas']['jid'], _T("Jid", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['cluster_name'], _T("Cluster Name", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['cluster_description'], _T("Cluster Description", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['total_machines'], _T("Total Machines", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['uninventoried_online'], _T("Uninventoried Online", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['classutil'], _T("Class Util", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['macaddress'], _T("Mac Address", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['ip_xmpp'], _T("Xmpp IP", "xmppmaster"));


$n->setTableHeaderPadding(0);
$n->setItemCount($relays['total']);
$n->setNavBar(new AjaxNavBar($relays['total'], $filter, "updateSearchParamformRunning"));
$n->addActionItemArray($packagesAction);
$n->addActionItemArray($reconfigurationActions);
$n->addActionItemArray($switchActions);
$n->addActionItemArray($configActions);
$n->addActionItemArray($qalistActions);
$n->addActionItemArray($quickActions);
$n->addActionItemArray($vncActions);
$n->addActionItemArray($relayRulesActions);
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
