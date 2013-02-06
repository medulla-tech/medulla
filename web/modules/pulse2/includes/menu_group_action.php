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

$paramArray = array(
    // if no $_GET['id'], get the $_GET['gid'] value
    // to be checked with profiles activated...
    'id' => ($_GET['id']) ? $_GET['id'] : $_GET['gid'],
    'gid' => $_GET['gid'],
    'groupname' => $_GET['groupname'],
    'type' => $_GET['type'],
);

$actions = array();

if(isset($_GET['type']))
    $is_gp = $_GET['type'];
else
    $is_gp = 0;

if ($is_gp && $is_gp == 1) { # Profile
    $list = getAllProfiles(array());
} else {
    $list = getAllGroups(array());
}

if ($is_gp != 1) {
    $delete = new ActionPopupItem(_T("Delete this group", 'dyngroup'), "delete_group", "delete", "id", "base", "computers");
} else {
    $delete = new ActionPopupItem(_T("Delete this profile", 'dyngroup'), "delete_group", "delete", "id", "base", "computers");
}

if ($is_gp != 1) {
    $actions['displayGroup'] = new ActionItem(_T("Display this group's content", 'dyngroup'), "display", "display", "id", "base", "computers");

    if (in_array("inventory", $_SESSION["supportModList"])) {
        $actions['inventory'] = new ActionItem(_T("Inventory on this group", "dyngroup"),"groupinvtabs","inventory","inventory", "base", "computers");
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this group", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $actions['edit'] = new ActionItem(_T("Edit this group", 'dyngroup'), "computersgroupedit", "edit", "id", "base", "computers");
    $actions['share'] = new ActionItem(_T("Share this group", 'dyngroup'), "edit_share", "groupshare", "id", "base", "computers");
    if (in_array("msc", $_SESSION["supportModList"])) {
        $actions['log'] = new ActionItem(_T("Read log", "dyngroup"),"groupmsctabs","logfile","computer", "base", "computers", "grouptablogs");
        $actions['deploy'] = new ActionItem(_T("Software deployment on this group", "dyngroup"),"groupmsctabs","install","computer", "base", "computers");
    }
} else {
    if (in_array("inventory", $_SESSION["supportModList"])) {
        $actions['inventory'] = new ActionItem(_T("Inventory on this profile", "dyngroup"),"groupinvtabs","inventory","inventory", "base", "computers");
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this profile", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $actions['edit'] = new ActionItem(_T("Edit this profile", 'dyngroup'), "computersgroupedit", "edit", "id", "base", "computers");
    $actions['share'] = new ActionItem(_T("Share this profile", 'dyngroup'), "edit_share", "groupshare", "id", "base", "computers");
    if (in_array("msc", $_SESSION["supportModList"])) {
        $actions['log'] = new ActionItem(_T("Read log", "dyngroup"),"groupmsctabs","logfile","computer", "base", "computers", "grouptablogs");
        $actions['deploy'] = new ActionItem(_T("Software deployment on this profile", "dyngroup"),"groupmsctabs","install","computer", "base", "computers");
    }
    if (in_array("imaging", $_SESSION["supportModList"])) {
        if (xmlrpc_isImagingInProfilePossible()) {
            $actions['imaging'] = new ActionItem(_("Imaging management"),"groupimgtabs","imaging","computer", "base", "computers");
        }
    }
}

foreach ($list as $group) {
    if ($group->id == $_GET['id']) {
        if ($group->is_owner == 1) {
            $actions['delete'] = $delete;
        } 
    }
}

$actions['csv'] = new ActionItem(_T("Csv export", "dyngroup"),"csv","csv","computer", "base", "computers");

echo "<ul class='action'>";
foreach ($actions as $action){
        if (is_array($paramArray)) {
            $paramArray['mod'] = $action->mod;
        }    
        echo "<li class=\"".$action->classCss."\" style=\"list-style-type: none; border: none; float:left; \" >";
        if (is_array($paramArray) & !empty($paramArray)) $urlChunk = $action->buildUrlChunk($paramArray);
        else $urlChunk = "&amp;" . $action->paramString."=" . rawurlencode($paramArray);
        echo "<a title=\"".$action->desc."\" href=\"" . urlStr($action->path) . $urlChunk . "\">&nbsp;</a>";
        echo "</li>";
}
echo "</ul>";
?>

