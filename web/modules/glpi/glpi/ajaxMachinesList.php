<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id$
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
 * file : /glpi/glpi/ajaxMachinesList.php
 */

require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/mscoptions_xmlrpc.php");

global $config;

?>
<style>
.selectable{
	cursor:pointer;
}
</style>

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

$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$filter = (isset($_GET['filter'])) ? $_GET['filter'] : "";
$field = (isset($_GET['field'])) ? $_GET['field'] : "";
$contains = (isset($_GET['contains'])) ? $_GET['contains'] : "";

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$maxperpage = (isset($_GET['maxperpage'])) ? $_GET['maxperpage'] : $config['maxperpage'];
$end = (isset($_GET['end'])) ? $_GET['end'] : $maxperpage - 1;

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filter;
$ctx['field'] = $field;
$ctx['contains'] = $contains;

$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;



if (isset($_SESSION['computerpresence'])  && $_SESSION['computerpresence'] != "all_computer") {
    $ctx['computerpresence'] = $_SESSION['computerpresence'];
}

try {
    $machines1 = xmlrpc_xmppmaster_get_machines_list($start, $maxperpage, $ctx);
} catch(Exception $e) {
    echo 'error';
}


$count = (!empty($machines1["count"])) ? $machines1["count"] : 0;
$total = $machines1["total"];
$datas = $machines1["data"];

$br = array("<br />","<br>","<br/>","<br />","&lt;br /&gt;","&lt;br/&gt;","&lt;br&gt;");
foreach ($datas as $nametableau => $tableau) {
    foreach($datas[$nametableau] as  $key => &$value) {
        $value = str_ireplace(array("\\r\\n"), "\r\n", $value);
        $value = str_ireplace(array("\\n"), "\r\n", $value);
        $value = str_ireplace($br, "\r\n", $value);
        if(stripos($value, "script") !== false) {
            $value  = htmlspecialchars($value);
        }
        $value =  htmlentities($value);
    }
}

$presencesClass = [];
$params = [];

$msc_vnc_show_icon = web_vnc_show_icon();

$glpinoAction = new EmptyActionItem1(_("GLPI Inventory"), "glpitabs", "inventoryg", "inventory", "base", "computers");

// Actions for each machines
$glpiAction = new ActionItem(_("GLPI Inventory"), "glpitabs", "inventory", "inventory", "base", "computers");


if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    $monitoring = new ActionItem(_("Monitoring"), "monitoringview", "monit", "computers", "xmppmaster", "xmppmaster");
    $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "guaca", "computer", "base", "computers");


    $mscAction = new ActionItem(_("Software deployment"), "msctabs", "install", "computer", "base", "computers");
    $mscNoAction = new EmptyActionItem1(_("Software deployment"), "msctabs", "installg", "computer", "base", "computers");

    $inventconsole   = new ActionItem(_("xmppconsole"), "consolecomputerxmpp", "console", "computers", "xmppmaster", "xmppmaster");
    $inventnoconsole = new EmptyActionItem1(_("xmppconsole"), "consolecomputerxmpp", "consoleg", "computers", "xmppmaster", "xmppmaster");

    $editremoteconfiguration    = new ActionItem(_("Edit config files"), "listfichierconf", "config", "computers", "xmppmaster", "xmppmaster");
    $editnoremoteconfiguration  = new EmptyActionItem1(_("Edit config files"), "remoteeditorconfiguration", "configg", "computers", "xmppmaster", "xmppmaster");

} else {
    $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "vncclient", "computer", "base", "computers");
}

$imgAction = new ActionItem(_("Imaging management"), "imgtabs", "imaging", "computer", "base", "computers");

$extticketAction = new ActionItem(_("extTicket issue"), "extticketcreate", "extticket", "computer", "base", "computers");

// $profileAction = new ActionItem(_("Show Profile"), "computersgroupedit", "logfile","computer", "base", "computers");

$DeployQuickxmpp = new ActionPopupItem(_("Quick action"), "deployquick", "quick", "computer", "xmppmaster", "xmppmaster");
$DeployQuickxmpp->setWidth(600);
// with check presence xmpp
$vncClientActiongriser = new EmptyActionItem1(_("Remote control"), "vnc_client", "guacag", "computer", "base", "computers");

$actionMonitoring = array();
$actionInventory = array();
$actionConsole = array();
$action_deploy_msc = array();
$actionImaging = array();
$actionVncClient = array();
$actionExtTicket = array();
$actionProfile = array();
$actionxmppquickdeoloy = array();
$cssClasses = array();
$actioneditremoteconfiguration = array();

$dissociatedFirstColumns = [];

$raw = 0;
// Do not modify directly $datas['cn'] it is reused later for $params
// And tabs in detail page will be broken
$cn = [];
$chaine = array(
        'hostname'              => _T("Hostname", 'xmppmaster'),
        'jid'                   => _T("Jabber ID", 'xmppmaster'),
        'platform'              => _T("Platform", 'xmppmaster'),
        'archi'                 => _T("Architecture", 'xmppmaster'),
        'uuid_serial_machine'   => _T("Machine UUID", 'xmppmaster'),
        'need_reconf'           => _T("Reconf. requested", 'xmppmaster'),
        'enabled'               => _T("Online", 'xmppmaster'),
        'ip_xmpp'               => _T("IP address", 'xmppmaster'),
        'subnetxmpp'            => _T("Subnet", 'xmppmaster'),
        'ippublic'              => _T("Public IP", 'xmppmaster'),
        'macaddress'            => _T("Mac address", 'xmppmaster'),
        'agenttype'             => _T("Agent type", 'xmppmaster'),
        'classutil'             => _T("Usage class", 'xmppmaster'),
        'groupdeploy'           => _T("Relay JID", 'xmppmaster'),
        'ad_ou_machine'         => _T("AD machine OU", 'xmppmaster'),
        'ad_ou_user'            => _T("AD user OU", 'xmppmaster'),
        'kiosk_presence'        => _T("Kiosk enabled", 'xmppmaster'),
        'lastuser'              => _T("Last user connected", 'xmppmaster'),
        'keysyncthing'          => _T("Syncthing ID", 'xmppmaster'),
        'regedit'               => _T("Registry keys", 'xmppmaster'),
        'id'                    => _T("Machine ID", 'xmppmaster'),
        'uuid_inventorymachine' => _T("GLPI ID", 'xmppmaster'),
        'glpi_description'      => _T("GLPI description", 'xmppmaster'),
        'glpi_owner_firstname'  => _T("Owner firstname", 'xmppmaster'),
        'glpi_owner_realname'   => _T("Owner lastname", 'xmppmaster'),
        'glpi_owner'            => _T("Owner", 'xmppmaster'),
        'model'                 => _T("Model", 'xmppmaster'),
        'manufacturer'          => _T("Manufacturer", 'xmppmaster'),
        'entityname'            => _T("Short entity name", 'xmppmaster'),
        'entitypath'            => _T("Full entity name", 'Xmppmaster'),
        'entityid'              => _T("Entity ID", 'xmppmaster'),
        'locationname'          => _T("Short location name", 'xmppmaster'),
        'locationpath'          => _T("Full location name", 'Xmppmaster'),
        'locationid'            => _T("Location ID", 'xmppmaster'),
        'listipadress'          => _T("IP addresses", 'xmppmaster'),
        'mask'                  => _T("Network mask", 'xmppmaster'),
        'broadcast'             => _T("Broadcast address", 'xmppmaster'),
        'gateway'               => _T("Gateway address", 'xmppmaster'));


foreach ($machines1['list_reg_columns_name'] as $columns_name) {
    $chaine[$columns_name] = $columns_name;
}


$orderkey = array( "glpi_owner",
            "mask",
            "uuid_inventorymachine",
            "id",
            "jid",
            "ip_xmpp",
            "ad_ou_user",
            "columns_name",
            "entityname",
            "hostname",
            "listipadress",
            "platform",
            "locationid",
            "glpi_entity_id",
            "lastuser",
            "ippublic",
            "need_reconf",
            "broadcast",
            "classutil",
            "uuid_serial_machine",
            "agenttype",
            "keysyncthing",
            "groupdeploy",
            "glpi_owner_realname",
            "glpi_owner_firstname",
            "gateway",
            "locationpath",
            "entityid",
            "entitypath",
            "manufacturer",
            "macaddress",
            "glpi_description",
            "archi",
            "enabled",
            "ProductName",
            "subnetxmpp",
            "ad_ou_machine",
            "regedit",
            "locationname",
            "model",
            "EnableLUA",
            "kiosk_presence",
            "glpi_location_id");


$exclud = array('glpi_location_id', 'glpi_entity_id', 'columns_name',"list_reg_columns_name" );
for ($index = 0; $index < safeCount($datas['hostname']); $index++) {
    $chainestr = "<table class='ttable'>";

    /*
     *      FIXME: Do not remove, will be oised to order the entries on the menu
            foreach($orderkey as $key_in_order){
                $data_order=$datas[$key_in_order];
                if(in_array($mach,$exclude ) ||  $data_order[$index] == ""){
                    continue;
                }
             $chainestr .= "<tr class='ttabletr'><td class='ttabletd'>".$chaine[$key_in_order] ."</td><td class='ttabletd'>".$data_order[$index]."</td></tr>";
            }
    */

    foreach($datas as $mach => $value) {
        if(in_array($mach, $exclud) ||  $value[$index] == "" || gettype($value[$index]) == "array") {
            continue;
        }
        $chainestr .= "<tr class='ttabletr'><td class='ttabletd'>".$chaine[$mach] ."</td><td class='ttabletd'>: ".$value[$index]."</td></tr>";
    }
    $chainestr .= "</table>";
    $cn[] = sprintf('<span class="infomach" mydata="%s">%s</pan>', $chainestr, $datas['hostname'][$index]);
}

$index = 0;
foreach($datas['enabled'] as $valeue) {

    if ($datas['uuid_inventorymachine'][$index] == "") {
        $actionInventory[] = $glpinoAction;
        $dissociatedFirstColumns[] = $index;
        $action_deploy_msc[] = $mscNoAction; //deployement
    } else {
        $actionInventory[] = $glpiAction;
        $action_deploy_msc[] = $mscAction; //deployement
    }
    $actionxmppquickdeoloy[] = $DeployQuickxmpp; //Quick action presence ou non presence.
    $actionMonitoring[] = $monitoring;
    if ($valeue == 1) {
        $presencesClass[] = "machineNamepresente";
        if (isExpertMode()) {
            $actionConsole[] = $inventconsole;
            $actioneditremoteconfiguration[] = $editremoteconfiguration;
        }
    } else {
        $presencesClass[] = "machineName";
        if (isExpertMode()) {
            $actionConsole[] = $inventnoconsole;
            $actioneditremoteconfiguration[] = $editnoremoteconfiguration;
        }
    }

    if (in_array("imaging", $_SESSION["supportModList"])) {
        $actionImaging[] = $imgAction;
    }

    if (in_array("extticket", $_SESSION["supportModList"])) {
        $actionExtTicket[] = $extticketAction;
    }

    if (in_array("guacamole", $_SESSION["supportModList"]) && in_array("xmppmaster", $_SESSION["supportModList"])) {
        if ($datas['enabled'][$index]) {
            $actionVncClient[] = $vncClientAction;
        } else {//show icone vnc griser
            $actionVncClient[] = $vncClientActiongriser;
        }
    } elseif ($msc_vnc_show_icon) {
        $actionVncClient[] = $vncClientAction;
    }
    $params[] = [
        'objectUUID' => $datas['uuid_inventorymachine'][$index],
        'UUID' => str_replace("UUID", "", $datas['uuid_inventorymachine'][$index]),
        'cn' => $datas['hostname'][$index],
        'os' => $datas['platform'][$index],
        'type' => $datas['model'][$index],
        'presencemachinexmpp' => $datas['enabled'][$index],
        'entity' => $datas['entityname'][$index],
        'user' => $datas['glpi_owner'][$index],
                    'jid' => $datas['jid'][$index],
    'vnctype' => (in_array("guacamole", $_SESSION["supportModList"])) ? "guacamole" : ((web_def_use_no_vnc() == 1) ? "novnc" : "appletjava"),
        'from' => "machinesList",
    ];

    $index++;
}

// Avoiding the CSS selector (tr id) to start with a number
$ids = [];
foreach($datas['uuid_serial_machine'] as $uuid_machine) {
    $ids[] = 'm_'.$uuid_machine;
}

$n = new OptimizedListInfos($cn, _T("Computer Name", "glpi"));
$n->setcssIds($ids);
$n->setParamInfo($params); // [params]
$n->dissociateColumnActionLink($dissociatedFirstColumns);
if(in_array("description", $machines1["column"])) {
    $n->addExtraInfo($datas["glpi_description"], _T("Description", "glpi"));
}
if(in_array("os", $machines1["column"])) {
    $n->addExtraInfo($datas["platform"], _T("Operating System", "glpi"));
}
if(in_array("type", $machines1["column"])) {
    $n->addExtraInfo($datas["model"], _T("Computer Type", "glpi"));
}
if(in_array('user', $machines1["column"])) {
    $n->addExtraInfo($datas["lastuser"], _T("Last Logged User", "glpi"));
}
if(in_array('owner', $machines1["column"])) {
    $n->addExtraInfo($datas["glpi_owner"], _T("Owner", "glpi"));
}
if(in_array("entity", $machines1["column"])) {
    $n->addExtraInfo($datas["entityname"], _T("Entity", "glpi"));
}
if(in_array("location", $machines1["column"])) {
    $n->addExtraInfo($datas["locationname"], _T("Localization", "glpi"));
}
if(in_array("owner_firstname", $machines1["column"])) {
    $n->addExtraInfo($datas["glpi_owner_firstname"], _T("Owner Firstname", "glpi"));
}
if(in_array("owner_realname", $machines1["column"])) {
    $n->addExtraInfo($datas["glpi_owner_realname"], _T("Owner Real Name", "glpi"));
}
if(in_array("manufacturer", $machines1["column"])) {
    $n->addExtraInfo($datas["manufacturer"], _T("Manufacturer", "glpi"));
}

foreach($machines1['list_reg_columns_name'] as $columnamekey) {
    $n->addExtraInfo($datas[$columnamekey], $columnamekey);
}

if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    $n->addActionItemArray($actionInventory);
    $n->addActionItemArray($actionMonitoring);
}

if (in_array("extticket", $_SESSION["supportModList"])) {
    $n->addActionItemArray($actionExtTicket);
}
if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    if (in_array("backuppc", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_("Backup status"), "hostStatus", "backuppc", "backuppc", "backuppc", "backuppc"));
    }

    if ($msc_vnc_show_icon) {
        $n->addActionItemArray($actionVncClient);
    };
}

if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    if (in_array("urbackup", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_("Urbackup"), "checkMachine", "urbackup", "urbackup", "urbackup", "urbackup"));
    }
}


if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    $n->addActionItemArray($action_deploy_msc);
}

if (in_array("imaging", $_SESSION["supportModList"])) {
    if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        $n->addActionItemArray($actionImaging);
    }
}
if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    if (isExpertMode()) {
        $n->addActionItemArray($actionConsole);
        if (!(isset($_GET['logview']) &&  $_GET['logview'] == "viewlogs")) {
            $n->addActionItemArray($actioneditremoteconfiguration);
        }
        $n->addActionItemArray($actionxmppquickdeoloy);
    } else {
        $n->addActionItemArray($actionxmppquickdeoloy);
    }
}

if(canDelComputer()) {
    $n->addActionItem(new ActionPopupItem(_("Delete computer"), "delete", "delete", "computer", "base", "computers", null, 400));
}


$n->setMainActionClasses($presencesClass);
$n->setItemCount($total);

$n->setNavBar(new AjaxNavBar($total, $location));
$n->start = 0;
$n->end = $total;
$n->display();
?>

<script>
jQuery(".selectable").on("click", function(){
	jQuery("#param").val(jQuery(this).text());
	pushSearch();
});


</script>
