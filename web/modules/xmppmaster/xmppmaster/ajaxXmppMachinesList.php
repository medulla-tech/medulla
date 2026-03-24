<?php
/*
 *  (c) 2021 siveo, http://www.siveo.net
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
 */

require_once("includes/UIComponents.php");
require_once("modules/xmppmaster/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

$machines = xmlrpc_get_xmppmachines_list($start, $maxperpage, $filter, $_SESSION['computerpresence']);

if ($machines['total'] == 0) {
    EmptyStateBox::show(
        _T("No uninventoried machines", "xmppmaster"),
        _T("All connected machines have been inventoried.", "xmppmaster")
    );
    return;
}

$raw = 0;
$params = [];

$editremoteconfigurationempty = new EmptyActionItem1(_("Edit config files"),"listconffile", "configg","computers","xmppmaster", "xmppmaster");
$editremoteconfiguration = new ActionItem(_("Edit config files"),"listconffile","config","computers", "xmppmaster", "xmppmaster");
$consoleaction   = new ActionItem(_("xmppconsole"),"consolecomputerxmpp","console","computers", "xmppmaster", "xmppmaster");
$consoleemptyaction = new EmptyActionItem1(_("xmppconsole"),"consolecomputerxmpp","consoleg","computers","xmppmaster", "xmppmaster");
$vncaction = new ActionPopupItem(_("Remote control"), "vnc_client", "guaca", "computer", "base", "computers");
$vncemptyaction = $vncClientActiongriser = new EmptyActionItem1(_("Remote control"), "vnc_client", "guacag", "computer", "base", "computers");

$configActions = [];
$consoleActions = [];
$vncActions = [];

foreach($machines['datas']['hostname'] as $key=>$array){
  $params[] = [
    'id' => $machines['datas']['id'][$raw],
    'hostname' => $machines['datas']['hostname'][$raw],
    'enabled' => $machines['datas']['enabled'][$raw],
    'enabled_css' => $machines['datas']['enabled_css'][$raw],
    'uninventoried' => true,
    'jid'=> $machines['datas']['jid'][$raw],
    'macaddress'=> $machines['datas']['macaddress'][$raw],
    'ip_xmpp' => $machines['datas']['ip_xmpp'][$raw],
    'agenttype' => 'machine',
    'platform' => $machines['datas']['platform'][$raw],
    'vnctype' => (in_array("guacamole", $_SESSION["supportModList"])) ? "guacamole" : ((web_def_use_no_vnc()==1) ? "novnc" : "appletjava"),
  ];
  // Build tooltip grouped by category
  $tooltipGroups = [
      _T("Identity", "xmppmaster") => [
          _T("Platform", "xmppmaster") => $machines['datas']['platform'][$raw],
          _T("Architecture", "xmppmaster") => $machines['datas']['archi'][$raw],
      ],
      _T("Network", "xmppmaster") => [
          _T("IP address", "xmppmaster") => $machines['datas']['ip_xmpp'][$raw],
          _T("Mac address", "xmppmaster") => formatMacAddress($machines['datas']['macaddress'][$raw]),
      ],
      _T("Agent", "xmppmaster") => [
          _T("Usage class", "xmppmaster") => $machines['datas']['classutil'][$raw],
          _T("Kiosk enabled", "xmppmaster") => $machines['datas']['kiosk_presence'][$raw],
          _T("Cluster", "xmppmaster") => $machines['datas']['cluster_name'][$raw],
          _T("Description", "xmppmaster") => $machines['datas']['cluster_description'][$raw],
      ],
      _T("Other", "xmppmaster") => [
          _T("AD user OU", "xmppmaster") => $machines['datas']['ad_ou_user'][$raw],
          _T("AD machine OU", "xmppmaster") => $machines['datas']['ad_ou_machine'][$raw],
      ],
  ];
  $tooltipData = '<table class="ttable">';
  foreach ($tooltipGroups as $groupLabel => $fields) {
      $groupRows = '';
      foreach ($fields as $label => $val) {
          if (!empty($val)) {
              $groupRows .= '<tr class="ttabletr"><td class="ttabletd">'.$label.'</td><td class="ttabletd">: '.htmlspecialchars($val).'</td></tr>';
          }
      }
      if ($groupRows !== '') {
          $tooltipData .= '<tr class="ttabletr tt-section"><td class="ttabletd" colspan="2">'.$groupLabel.'</td></tr>';
          $tooltipData .= $groupRows;
      }
  }
  $tooltipData .= '</table>';

  $machines['datas']['hostname'][$raw] = '<span class="infomach machine-clickable" mydata="'.htmlentities($tooltipData).'">'.$machines['datas']['hostname'][$raw].'</span>';
  $machines['datas']['jid'][$raw] = '<span class="machine-clickable">'.$machines['datas']['jid'][$raw].'</span>';
  $machines['datas']['archi'][$raw] = '<span class="machine-clickable">'.$machines['datas']['archi'][$raw].'</span>';
  $machines['datas']['macaddress'][$raw] = '<span class="machine-clickable">'.formatMacAddress($machines['datas']['macaddress'][$raw]).'</span>';
  $machines['datas']['ip_xmpp'][$raw] = '<span class="machine-clickable">'.$machines['datas']['ip_xmpp'][$raw].'</span>';


  if ($machines['datas']['enabled'][$raw]){
    $configActions[] =$editremoteconfiguration;
    $consoleActions[] = $consoleaction;
    $vncActions[] = $vncaction;
  }
  else{
    $configActions[] =$editremoteconfigurationempty;
    $consoleActions[] = $consoleemptyaction;
    $vncActions[] = $vncemptyaction;
  }
  $raw++;
}

$n = new OptimizedListInfos( $machines['datas']['hostname'], _T("Computer Name", "glpi"));
$n->setMainActionClasses($machines['datas']['enabled_css']);
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $machines['datas']['jid'], _T("Jid", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['archi'], _T("Arch", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['macaddress'], _T("Mac Address", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['ip_xmpp'], _T("IP address", "xmppmaster"));
$n->setTableHeaderPadding(0);
$n->setItemCount($machines['total']);
$n->setNavBar(new AjaxNavBar($machines['total'], $filter, "updateSearchParamformRunning"));
$n->addActionItemArray($vncActions);
$n->addActionItemArray($consoleActions);
$n->addActionItemArray($configActions);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $machines['total'];

$n->display();
?>

<style>
  .machine-clickable{
    cursor: pointer;
  }
</style>
<script>
jQuery(function() {
    jQuery(".infomach").tooltip({
        position: { my: "left+15 center", at: "right center" },
        items: "[mydata]",
        content: function() {
            var element = jQuery(this);
            if (element.is("[mydata]")) {
                return element.attr("mydata");
            }
        }
    });

    jQuery(".machine-clickable").on("click", function(){
        jQuery("#paramformRunning").val(jQuery(this).text());
        updateSearchformRunning();
    });
});
</script>
