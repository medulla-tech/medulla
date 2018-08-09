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

//     if (in_array("guacamole", $_SESSION["supportModList"])) {
        $element = "guacamole";
//     }
//     else{
//         try {
//             if (web_def_use_no_vnc()==1){
//                 $element="novnc";
//             }
//             else{
//                 $element="appletjava";
//             }
//         }catch (Exception $e) {
//             $element="novnc";
//         }
//     }
$paramArray = array('cn' => $_SESSION['cn'], 'objectUUID' => $_SESSION['objectUUID'],'vnctype' => $element, "presencemachinexmpp" => $presencemachinexmpp);

$inventAction = new ActionItem(_T("Inventory", "pulse2"),"invtabs","inventory","inventory", "base", "computers");
//$extticketAction = new ActionItem(_("extTicket issue"), "extticketcreate", "extticket", "computer", "base", "computers");
$backupAction = new ActionItem(_("Backup status"),"hostStatus","backuppc","backuppc", "backuppc", "backuppc");
$imgAction = new ActionItem(_T("Imaging management", "pulse2"),"imgtabs","imaging","computer", "base", "computers");
    $DeployQuickxmpp = new ActionPopupItem(_("Quick action"), "deployquick", "quick", "computer", "xmppmaster", "xmppmaster");
    $DeployQuickxmpp->setWidth(600);
    if ($presencemachinexmpp != 1) {
        $mscAction = new EmptyActionItem1(_T("Software deployment", "pulse2"),"msctabs","install","computer", "base", "computers");
    }
    else{

        $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "guaca", "computer", "base", "computers");
        $mscAction = new ActionItem(_T("Software deployment", "pulse2"),"msctabs","install","computer", "base", "computers");
        if (isExpertMode()){
            $inventconsole = new ActionItem(_("xmppconsole"),"consolecomputerxmpp","console","computers", "xmppmaster", "xmppmaster");
            $inventxmppbrowsing = new ActionItem(_("files browsing"),"xmppfilesbrowsing","folder","computers", "xmppmaster", "xmppmaster");
            $editconfiguration = new ActionItem(_("Edit config files"),"listfichierconf","config","computers", "xmppmaster", "xmppmaster");
        }else{
            $inventxmppbrowsing   = new ActionItem(_("files browsing"),"xmppfilesbrowsingne","folder","computers", "xmppmaster", "xmppmaster");
        }
    }


        $actions = array($inventAction, $backupAction, $vncClientAction, $mscAction, $imgAction,$inventxmppbrowsing,$inventconsole, $editconfiguration, $DeployQuickxmpp);


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
        "list"=> "xmppmaster",
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
foreach ($actions as $actionmodule){
        if (is_array($paramArray)) {
            $paramArray['mod'] = $actionmodule->mod;
            if ($actionmodule->action == "vnc_client") {
                $paramArray['establishproxy'] = "yes";
            }
        }
        echo "<li class=\"".$actionmodule->classCss."\" style=\"list-style-type: none; border: none; float:left; \" >";

//         if (is_array($paramArray) & !empty($paramArray)){
//             //$urlChunk = $actionmodule->buildUrlChunk($paramArray);
//         }
//         else{
//             $urlChunk = "&amp;" . $actionmodule->paramString."=" . rawurlencode($paramArray);
//         }
        $urlChunk = "&".strval(http_build_query($paramArray));

        if (modIsActive($actionmodule->action)) {
            switch($actionmodule->action){
                case "vnc_client":
                    if ($presencemachinexmpp == 1){
                        if (in_array("xmppmaster", $_SESSION["supportModList"])) {
                            echo '<a title="' . $actionmodule->desc . '" onclick="PopupWindow(event, \'' . urlStr($actionmodule->path) . $urlChunk . '\'); return false;" href="#">&nbsp;</a>';
                        }
                        else{
                            echo "<a title=\"".$actionmodule->desc.
                                "\" onclick=\"window.open('" .
                                urlStr($actionmodule->path) .
                                $urlChunk .
                                "','mywin','left=20,top=20,width=300,height=150,toolbar=1,resizable=0');\">&nbsp;</a>";
                        }
                    }
                    break;
                case "deployquick" :
                    echo '<a title="' . $actionmodule->desc . '" onclick="PopupWindow(event, \'' . urlStr($actionmodule->path) . $urlChunk . '\'); return false;" href="#">&nbsp;</a>';
                    break;

                case "consolecomputerxmpp":
                    if ($presencemachinexmpp == 1){
                        $url =  $actionmodule->path;
                        echo "<a title=\"".$actionmodule->desc."\" href=\"" . urlStr($url) . $urlChunk . "\">&nbsp;</a>";
                    }
                    break;
                default:
                    $url = (in_array('glpi', $_SESSION['supportModList']) && $actionmodule->path == 'base/computers/invtabs') ? 'base/computers/glpitabs' : $actionmodule->path;
                    echo "<a title=\"".$actionmodule->desc."\" href=\"" . urlStr($url) . $urlChunk . "\">&nbsp;</a>";
                    break;
            }
        }
        echo "</li>";
}
echo "</ul>";
?>
