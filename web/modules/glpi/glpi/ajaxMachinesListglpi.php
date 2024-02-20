<?php
/**
 * (c) 2021 Siveo, http://www.siveo.net/
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

$machines = xmlrpc_get_machines_list1($start, $maxperpage, $ctx);

$count = $machines["count"];
$datas = $machines["data"];
$xmppdatas = $machines['xmppdata'];

$presencesClass = [];
$params = [];

$msc_vnc_show_icon = web_vnc_show_icon();

// Actions for each machines
$glpiAction = new ActionItem(_("GLPI Inventory"), "glpitabs", "inventory", "inventory", "base", "computers");
$mscAction = new ActionItem(_("Software deployment"), "msctabs", "install", "computer", "base", "computers");

$inventAction = new ActionItem(_("Inventory"), "invtabs", "inventory", "inventory", "base", "computers");
$glpiAction = new ActionItem(_("GLPI Inventory"), "glpitabs", "inventory", "inventory", "base", "computers");
$logAction = new ActionItem(_("View deployment details"), "viewlogs", "logfile", "computer", "xmppmaster", "xmppmaster");
$mscAction = new ActionItem(_("Software deployment"), "msctabs", "install", "computer", "base", "computers");

if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    $monitoring = new ActionItem(_("Monitoring"), "monitoringview", "monit", "computers", "xmppmaster", "xmppmaster");
    $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "guaca", "computer", "base", "computers");
    $mscNoAction = new EmptyActionItem1(_("Software deployment"), "msctabs", "installg", "computer", "base", "computers");

    $inventconsole   = new ActionItem(_("xmppconsole"), "consolecomputerxmpp", "console", "computers", "xmppmaster", "xmppmaster");
    $inventnoconsole = new EmptyActionItem1(_("xmppconsole"), "consolecomputerxmpp", "consoleg", "computers", "xmppmaster", "xmppmaster");
    $actionConsole = array();
    $editremoteconfiguration    = new ActionItem(_("Edit config files"), "listfichierconf", "config", "computers", "xmppmaster", "xmppmaster");
    $editnoremoteconfiguration  = new EmptyActionItem1(_("Edit config files"), "remoteeditorconfiguration", "configg", "computers", "xmppmaster", "xmppmaster");
} else {
    $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "vncclient", "computer", "base", "computers");
}
$imgAction = new ActionItem(_("Imaging management"), "imgtabs", "imaging", "computer", "base", "computers");
$extticketAction = new ActionItem(_("extTicket issue"), "extticketcreate", "extticket", "computer", "base", "computers");

$profileAction = new ActionItem(_("Show Profile"), "computersgroupedit", "logfile", "computer", "base", "computers");

$DeployQuickxmpp = new ActionPopupItem(_("Quick action"), "deployquick", "quick", "computer", "xmppmaster", "xmppmaster");
$DeployQuickxmpp->setWidth(600);
// with check presence xmpp
$vncClientActiongriser = new EmptyActionItem1(_("Remote control"), "vnc_client", "guacag", "computer", "base", "computers");

$actionMonitoring = array();
$actionInventory = array();
$action_logs_msc = array();
$action_deploy_msc = array();
$actionImaging = array();
$actionVncClient = array();
$actionExtTicket = array();
$actionProfile = array();
$actionxmppquickdeoloy = array();
$cssClasses = array();
$actioneditremoteconfiguration = array();

$raw = 0;
// Do not modify directly $datas['cn'] it is reused later for $params
// And tabs in detail page will be broken
$cn = [];

foreach($datas['uuid'] as $uuid) {
    if(isset($xmppdatas['UUID'.$uuid])) {
        $cnstr = '<span ';
        $cnstr .= 'title="';
        $cnstr .= "jid : \t ". $xmppdatas['UUID'.$uuid]['jid']."\n";
        $cnstr .= "classutil : \t ". $xmppdatas['UUID'.$uuid]['classutil']."\n";
        $cnstr .= "ad_ou_user : \t ". $xmppdatas['UUID'.$uuid]['ad_ou_user']."\n";
        $cnstr .= "ad_ou_machine : \t ". $xmppdatas['UUID'.$uuid]['ad_ou_machine']."\n";
        $cnstr .= "need_reconf : \t ". $xmppdatas['UUID'.$uuid]['need_reconf']."\n";
        $cnstr .= "keysyncthing : \t ". $xmppdatas['UUID'.$uuid]['keysyncthing']."\n";
        $cnstr .= "groupdeploy : \t ". $xmppdatas['UUID'.$uuid]['groupdeploy']."\n";
        $cnstr .= "subnetxmpp : \t ". $xmppdatas['UUID'.$uuid]['subnetxmpp']."\n";
        $cnstr .= "ip_xmpp : \t ". $xmppdatas['UUID'.$uuid]['ip_xmpp']."\n";
        $cnstr .= "ippublic : \t ". $xmppdatas['UUID'.$uuid]['ippublic']."\n";
        $cnstr .= "kiosk_presence : \t ". $xmppdatas['UUID'.$uuid]['kiosk_presence']."\n";
        $cnstr .= '"';
        $cnstr .= '>'.$datas['cn'][$raw].'</span>';
        $cn[] = $cnstr;
    } else {
        $cn[] = $datas['cn'][$raw];
    }
    $presencesClass[] = ($datas['presence'][$raw] == 1) ? "machineNamepresente" : "machineName";

    if (in_array("inventory", $_SESSION["supportModList"])) {
        $actionInventory[] = $inventAction;
    } else {
        $actionInventory[] = $glpiAction;
    }

    if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        $actionxmppquickdeoloy[] = $DeployQuickxmpp;
        $action_deploy_msc[] = $mscAction;
        $action_logs_msc[]   = $logAction;
        $actionMonitoring[] = $monitoring;
        if ($datas['presence'][$raw]) {
            if (isExpertMode()) {
                $actionConsole[] = $inventconsole;
                $actioneditremoteconfiguration[] = $editremoteconfiguration;
            }
        } else {
            if (isExpertMode()) {
                $actionConsole[] = $inventnoconsole;
                $actioneditremoteconfiguration[] = $editnoremoteconfiguration;
            }
        }
    } else {
        if (in_array("msc", $_SESSION["supportModList"])) {
            $action_deploy_msc[] = $mscAction;
            $action_logs_msc[]   = $logAction;
        }
    }

    if (in_array("imaging", $_SESSION["supportModList"])) {
        $actionImaging[] = $imgAction;
    }

    if (in_array("extticket", $_SESSION["supportModList"])) {
        $actionExtTicket[] = $extticketAction;
    }

    if (in_array("guacamole", $_SESSION["supportModList"]) && in_array("xmppmaster", $_SESSION["supportModList"])) {
        if ($datas['presence'][$raw]) {
            $actionVncClient[] = $vncClientAction;
        } else {//show icone vnc griser
            $actionVncClient[] = $vncClientActiongriser;
        }
    } elseif ($msc_vnc_show_icon) {
        $actionVncClient[] = $vncClientAction;
    }

    $params[] = [
        'objectUUID' => 'UUID'.$datas['uuid'][$raw],
        'UUID' => $datas['uuid'][$raw],
        'cn' => $datas['cn'][$raw],
        'os' => $datas['os'][$raw],
        'type' => $datas['type'][$raw],
        'presencemachinexmpp' => $datas['presence'][$raw],
        'entity' => $datas['entity'][$raw],
        'user' => $datas['user'][$raw],
    'vnctype' => (in_array("guacamole", $_SESSION["supportModList"])) ? "guacamole" : ((web_def_use_no_vnc() == 1) ? "novnc" : "appletjava"),
        'from' => "machinesListglpi",
    ];

    foreach($datas as $field => $table) {
        /*The reg array is composed of multiple array. This example reproduces the datas structure with the reg key
            $datas = [
                'description' => [
                    'description for computer 1',
                    'description for computer 2',
                    'description for computer 3'
                ],
                'os' => [
                    'os for computer 1',
                    'os for computer 2',
                    'os for computer 3'
                ],
                'reg' => [
                    'enableLUA' => [
                        'enableLUA value for computer 1',
                        'enableLUA value for computer 2',
                        'enableLUA value for computer 3'
                    ],
                    'MyKey2'=> [
                        'MyKey2 value for computer 1',
                        'MyKey2 value for computer 2',
                        'MyKey2 value for computer 3'
                    ]
                ]
            ]
        */
        if($field != 'reg' && $field != 'cn') { // The selectable class is used to fill the search field;
            $datas[$field][$raw] = '<span class="selectable">'.$datas[$field][$raw].'</span>';
        }
    }
    $raw++;
}

// Avoiding the CSS selector (tr id) to start with a number
$ids = [];
foreach($datas['cn'] as $cn_machine) {
    $ids[] = 'm_'.$cn_machine;
}

$n = new OptimizedListInfos($cn, _T("Computer Name", "glpi"));
$n->setcssIds($ids);
$n->setParamInfo($params); // [params]
if(array_key_exists("description", $datas)) {
    $n->addExtraInfo($datas["description"], _T("Description", "glpi"));
}
if(array_key_exists("os", $datas)) {
    $n->addExtraInfo($datas["os"], _T("Operating System", "glpi"));
}
if(array_key_exists("type", $datas)) {
    $n->addExtraInfo($datas["type"], _T("Computer Type", "glpi"));
}
if(array_key_exists('user', $datas)) {
    $n->addExtraInfo($datas["user"], _T("Last Logged User", "glpi"));
}
if(array_key_exists('owner', $datas)) {
    $n->addExtraInfo($datas["owner"], _T("Owner", "glpi"));
}
if(array_key_exists("entity", $datas)) {
    $n->addExtraInfo($datas["entity"], _T("Entity", "glpi"));
}
if(array_key_exists("location", $datas)) {
    $n->addExtraInfo($datas["location"], _T("Localization", "glpi"));
}
if(array_key_exists("owner_firstname", $datas)) {
    $n->addExtraInfo($datas["owner_firstname"], _T("Owner Firstname", "glpi"));
}
if(array_key_exists("owner_realname", $datas)) {
    $n->addExtraInfo($datas["owner_realname"], _T("Owner Real Name", "glpi"));
}
if(array_key_exists("model", $datas)) {
    $n->addExtraInfo($datas["model"], _T("Model", "glpi"));
}
if(array_key_exists("manufacturer", $datas)) {
    $n->addExtraInfo($datas["manufacturer"], _T("Manufacturer", "glpi"));
}
if(array_key_exists("reg", $datas)) {
    foreach($datas['reg'] as $key => $value) {
        // Here $value is the table of reg values
        foreach($datas["reg"][$key] as $id => $regvalue) {
            $regvalue = '<span class="selectable">'.$regvalue.'</span>';
        }
        $n->addExtraInfo($datas["reg"][$key], _T($key, "glpi"));
    }
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

if (in_array("msc", $_SESSION["supportModList"]) || in_array("xmppmaster", $_SESSION["supportModList"])) {
    if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        $n->addActionItemArray($action_deploy_msc);
    } else {
        $n->addActionItemArray($action_logs_msc);
    }
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
$n->setItemCount($count);

$n->setNavBar(new AjaxNavBar($count, $location));
$n->start = 0;
$n->end = $count;
$n->display();
?>

<script>
jQuery(".selectable").on("click", function(){
	jQuery("#param").val(jQuery(this).text());
	pushSearch();
});
</script>
