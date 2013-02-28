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

if ($_GET['cn']) $_SESSION['cn'] = $_GET['cn'];
if ($_GET['objectUUID']) $_SESSION['objectUUID'] = $_GET['objectUUID'];
if ($_GET['action']) $_SESSION['action'] = $_GET['action'];

$paramArray = array('cn' => $_SESSION['cn'], 'objectUUID' => $_SESSION['objectUUID']);

$inventAction = new ActionItem(_T("Inventory", "pulse2"),"invtabs","inventory","inventory", "base", "computers");
$vncClientAction = new ActionItem(_T("Remote control", "pulse2"), "vnc_client", "vncclient", "computer", "base", "computers");
$logAction = new ActionItem(_T("Read log", "pulse2"),"msctabs","logfile","computer", "base", "computers", "tablogs");
$mscAction = new ActionItem(_T("Software deployment", "pulse2"),"msctabs","install","computer", "base", "computers");
$imgAction = new ActionItem(_T("Imaging management", "pulse2"),"imgtabs","imaging","computer", "base", "computers");

    
$actions = array($inventAction, $vncClientAction, $logAction, $mscAction, $imgAction);

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
                return hasCorrectAcl('base', 'computers', "index&vnc=");
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
        echo "<li class=\"".$action->classCss."\" style=\"list-style-type: none; border: none; float:left; \" >";
        if (is_array($paramArray) & !empty($paramArray)) $urlChunk = $action->buildUrlChunk($paramArray);
        else $urlChunk = "&amp;" . $action->paramString."=" . rawurlencode($paramArray);
        if (modIsActive($action->action)) {
            if ($action->action == "vnc_client") {
                echo "<a title=\"".$action->desc."\" onclick=\"window.open('" . urlStr($action->path) . $urlChunk . "','mywin','left=20,top=20,width=300,height=150,toolbar=1,resizable=0');\">&nbsp;</a>";
            }
            else {
                $url = (in_array('glpi', $_SESSION['supportModList']) && $action->path == 'base/computers/invtabs') ? 'base/computers/glpitabs' : $action->path;
                echo "<a title=\"".$action->desc."\" href=\"" . urlStr($url) . $urlChunk . "\">&nbsp;</a>";
            }
        }
        echo "</li>";
}
echo "</ul>";
?>
