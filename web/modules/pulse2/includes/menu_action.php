<?php

/**
 * (c) 2012 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/base/includes/users-xmlrpc.inc.php");
if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    require_once("modules/xmppmaster/includes/xmlrpc.php");
}


if (isset($_GET['cn'])) $_SESSION['cn'] = $_GET['cn'];
if (isset($_GET['objectUUID']))
    $_SESSION['objectUUID'] = $_GET['objectUUID'];
else if (isset($_GET['uuid']))
    $_SESSION['objectUUID'] = $_GET['uuid'];
if (isset($_GET['action']))
    $_SESSION['action'] = $_GET['action'];

    $presencemachinexmpp = xmlrpc_getPresenceuuid( $_SESSION['objectUUID']);

    if (in_array("guacamole", $_SESSION["supportModList"])) {
        $element = "guacamole";
    }
    else{
        try {
            if (web_def_use_no_vnc()==1){
                $element="novnc";
            }
            else{
                $element="appletjava";
            }
        }catch (Exception $e) {
            $element="novnc";
        }
    }
$_SESSION['cn'] = isset($_SESSION['cn']) ? $_SESSION['cn'] : null;
$paramArray = array('cn' => $_SESSION['cn'], 'objectUUID' => $_SESSION['objectUUID'],'vnctype' => $element, "presencemachinexmpp" => $presencemachinexmpp);

$inventAction = new ActionItem(_T("Inventory", "pulse2"),"invtabs","inventory","inventory", "base", "computers");
$extticketAction = new ActionItem(_T("extTicket issue"), "extticketcreate", "extticket", "computer", "base", "computers");
$backupAction = new ActionItem(_T("Backup status"),"hostStatus","backuppc","backuppc", "backuppc", "backuppc");
$imgAction = new ActionItem(_T("Imaging management", "pulse2"),"imgtabs","imaging","computer", "base", "computers");

if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "guaca", "computer", "base", "computers");
}
else{
    $vncClientAction = new ActionItem(_T("Remote control", "pulse2"), "vnc_client", "vncclient", "computer", "base", "computers");
}

if (in_array("xmppmaster", $_SESSION["supportModList"])) {

    $inventconsole = new ActionItem(_("xmppconsole"),"consolecomputerxmpp","console","computers", "xmppmaster", "xmppmaster");
    $DeployQuickxmpp = new ActionPopupItem(_("Quick action"), "deployquick", "quick", "computer", "xmppmaster", "xmppmaster");
    $DeployQuickxmpp->setWidth(600);

    if ($presencemachinexmpp != 1) {
        $mscAction = new EmptyActionItem1(_T("Software deployment", "pulse2"),"msctabs","install","computer", "base", "computers");
    }
    else{
        $mscAction = new ActionItem(_T("Software deployment", "pulse2"),"msctabs","install","computer", "base", "computers");
        if (isExpertMode()){
            $inventxmppbrowsing = new ActionItem(_("files browsing"),"xmppfilesbrowsing","folder","computers", "xmppmaster", "xmppmaster");
        }else{
            $inventxmppbrowsing   = new ActionItem(_("files browsing"),"xmppfilesbrowsingne","folder","computers", "xmppmaster", "xmppmaster");
        }
    }
}
else{
    $mscAction = new ActionItem(_T("Software deployment", "pulse2"),"msctabs","install","computer", "base", "computers");
}



if (in_array("xmppmaster", $_SESSION["supportModList"]) && isset($_GET['cmd_id']) ) {
    $actions = array();
}
else{
    if (in_array("xmppmaster", $_SESSION["supportModList"])){
        $actions = array($inventAction, $extticketAction, $backupAction,
                            $vncClientAction, $mscAction,
                            $imgAction,$inventxmppbrowsing,$inventconsole,
                            $DeployQuickxmpp);
    }
    else{
        $actions = array($inventAction, $extticketAction, $backupAction, $vncClientAction, $mscAction, $imgAction);
    }
}

/*
 * This function return True if action param is in enabled pulse modules
 *
 * @param string $action an action
 * @return bool
 */
function modIsActive($action) {
    $modActionAssoc = array(
        "img" => "imaging",
        "inv" => "inventory",
        "vnc" => "msc",
        "msc" => "msc",
        "hos" => "backuppc",
        "cre" => "extticket",
        "console" => "xmppmaster",
        "xmpp" => "xmppmaster",
        "quick" => "xmppmaster"
    );
    $modList = $_SESSION['supportModList'];
    if (in_array('glpi', $modList)) $modList[] = 'inventory';
    $action = strtolower($action);
    foreach ($modActionAssoc as $key => $value) {
        $mod = '';
        if (strpos($action, $key) !== false) {
            $mod = $value;
        }
        if (in_array($mod, $modList)) {
            if (strpos($action, "vnc") !== false) {
                // if VNC icon, check if "Take control of this computer" ACL
                // is True or not
                return hasCorrectAcl('base', 'computers', "vnc_client");
            }
            return True;
        }
    }
    return False;
}
echo "<ul class='action'>";
foreach ($actions as $action){
        if (is_array($paramArray)) {
            $paramArray['mod'] = $action->mod;
            if ($action->action == "vnc_client") {
                $paramArray['establishproxy'] = "yes";
            }
        }
        if($action->action !="invtabs" && hasCorrectAcl($action->module, $action->submod, $action->action))
            echo "<li class=\"".$action->classCss."\" style=\"list-style-type: none; border: none; float:left; \" >";
        else if($action->action =="invtabs" && hasCorrectAcl($action->module, $action->submod, 'glpitabs'))
            echo "<li class=\"".$action->classCss."\" style=\"list-style-type: none; border: none; float:left; \" >";
        else
            echo "<li class=\"".$action->classCss."\" style=\"list-style-type: none; border: none; float:left; opacity:0.5;\" >";



        $urlChunk = "&".strval(http_build_query($paramArray));
//         if (is_array($paramArray) & !empty($paramArray)){
//             $urlChunk = $action->buildUrlChunk($paramArray);
//         }
//         else{
//             $urlChunk = "&amp;" . $action->paramString."=" . rawurlencode($paramArray);
//
//         }

        if (modIsActive($action->action)) {
            switch($action->action){
                case "vnc_client":
                    if ($presencemachinexmpp == 1){
                        if (in_array("xmppmaster", $_SESSION["supportModList"])) {
                            echo '<a title="' . $action->desc . '" onclick="PopupWindow(event, \'' . urlStr($action->path) . $urlChunk . '\'); return false;" href="#">&nbsp;</a>';
                        }
                        else{
                            echo "<a title=\"".$action->desc.
                                "\" onclick=\"window.open('" .
                                urlStr($action->path) .
                                $urlChunk .
                                "','mywin','left=20,top=20,width=300,height=150,toolbar=1,resizable=0');\">&nbsp;</a>";
                        }
                    }
                    break;
                case "deployquick" :
                    if(hasCorrectAcl($action->module,$action->submod, $action->action))
                      echo '<a title="' . $action->desc . '" onclick="PopupWindow(event, \'' . urlStr($action->path) . $urlChunk . '\'); return false;" href="#">&nbsp;</a>';
                    else
                      echo '<a title="' . $action->desc . '" href="#">&nbsp;</a>';
                    break;

                case "consolecomputerxmpp":
                    if ($presencemachinexmpp == 1){
                        $url =  $action->path;
                        if (hasCorrectAcl($action->module, $action->submod, $action->action))
                          echo "<a title=\"".$action->desc."\" href=\"" . urlStr($url) . $urlChunk . "\">&nbsp;</a>";
                        else {
                          echo "<a title=\"".$action->desc."\" href=\"\">&nbsp;</a>";
                        }
                    }
                    break;
                default:
                    $url = (in_array('glpi', $_SESSION['supportModList']) && $action->path == 'base/computers/invtabs') ? 'base/computers/glpitabs' : $action->path;
                    if($action->action=="invtabs")
                      $action->action ="glpitabs";
                    if (hasCorrectAcl($action->module, $action->submod, $action->action))
                      echo "<a title=\"".$action->desc."\" href=\"" . urlStr($url) . $urlChunk . "\">&nbsp;</a>";
                    else
                      echo "<a title=\"".$action->desc."\" href=\"#\">&nbsp;</a>";
                    break;
            }
        }
        echo "</li>";
}
echo "</ul>";
?>
