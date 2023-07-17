<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://siveo.net
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

require_once('modules/imaging/includes/xmlrpc.inc.php');
require("modules/pulse2/includes/profiles_xmlrpc.inc.php");
require_once("modules/pulse2/includes/utilities.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$start = 0;
if (isset($_GET["start"])) {
    $start = $_GET['start'];
}

if(isset($_GET['type']))
    $is_gp = $_GET['type'];
else
    $is_gp = 0;

$params = array('min'=>$start, 'max'=>$start + $maxperpage, 'filter'=>$_GET["filter"]);

if (isset($_GET['favourite'])){
    $params['canShow'] = true;
    $params['localSidebar'] = true;
}

if ($is_gp == 1) { # Profile
    $list = getAllProfiles($params);
    $count = countAllProfiles($params);
} else {
    $list = getAllGroups($params);
    $count = countAllGroups($params);
}
$filter = $_GET["filter"];

$ids  = array();
$name = array();
$type = array();
$show = array();
$actionxmppquickdeploy = array();
$action_delete = array();
if ($is_gp != 1) { // Simple Group
    $delete = new ActionPopupItem(_T("Delete this group", 'dyngroup'), "delete_group", "delete", "id", "base", "computers");
} else { // Imaging group
    $delete = new ActionPopupItem(_T("Delete this imaging group", 'dyngroup'), "delete_group", "delete", "id", "imaging", "manage");
}

if (in_array("xmppmaster", $_SESSION["supportModList"])) {
       $DeployQuickxmpp = new ActionPopupItem(_("Quick action"), "deployquickgroup", "quick", "computer", "xmppmaster", "xmppmaster");
        $DeployQuickxmpp->setWidth(600);
    }


$empty = new EmptyActionItem();

foreach ($list as $group) {
    if($is_gp == 1){
        $profile = xmlrpc_getProfileLocation($group->id);
        $ids[] =  array("id"=>clean_xss($group->id), "gid"=>clean_xss($group->id), "groupname"=> clean_xss($group->name), 'type'=>clean_xss($is_gp),'profile'=>clean_xss($profile));
    }else{
        $ids[]=  array("id"=>clean_xss($group->id), "gid"=>clean_xss($group->id), "groupname"=> clean_xss($group->name), 'type'=>clean_xss($is_gp));
    }
    $name[] = clean_xss($group->getName());
    //$name[]= htmlentities($group->getName());
    if ($group->isDyn()) {
        $type[]= (!$group->isRequest() ? sprintf(_T('result (%s)', 'dyngroup'), $group->countResult()) : _T('query', 'dyngroup'));
    } else {
        $type[]= _T('static group', 'dyngroup');
    }
    $show[]= ($group->canShow() ? _T('Yes', 'dyngroup') : _T('No', 'dyngroup'));
    if ($group->is_owner == 1 || $_SESSION['login'] == "root") {
        $action_delete[]= $delete;
    } else {
        $action_delete[]= $empty;
    }
    if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        $actionxmppquickdeploy[]=$DeployQuickxmpp;
    }
}

// Avoiding the CSS selector (tr id) to start with a number
$ids_grp = [];
foreach($ids as $index => $gid_grp){
    $ids_grp[] = 'g_'.$gid_grp['groupname'];
    }

if ($is_gp != 1) { // Simple Group
    $n = new OptimizedListInfos($name, _T('Group name', 'dyngroup'));
} else { // Imaging group
    $n = new OptimizedListInfos($name, _T('Group name', 'dyngroup'));
}
$n->setcssIds($ids_grp);
$n->setTableHeaderPadding(0);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $conf["global"]["maxperpage"];


if ($is_gp != 1) { // Simple group
    $n->addExtraInfo($type, _T('Type', 'dyngroup'));
}
$n->addExtraInfo($show, _T('Favourite', 'dyngroup'));
$n->setParamInfo($ids);

if ($is_gp != 1) { // Simple group
    $n->addActionItem(new ActionItem(_T("Display this group's content", 'dyngroup'), "display", "display", "id", "base", "computers"));
    if (in_array("inventory", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Inventory on this group", "dyngroup"),"groupinvtabs","inventory","inventory", "base", "computers"));
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this group", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $n->addActionItem(new ActionItem(_T("Edit this group", 'dyngroup'), "computersgroupedit", "edit", "id", "base", "computers"));
    $n->addActionItem(new ActionItem(_T("Share this group", 'dyngroup'), "edit_share", "groupshare", "id", "base", "computers"));

    if (in_array("msc", $_SESSION["supportModList"])) {
        if (!in_array("xmppmaster", $_SESSION["supportModList"])) {
            $n->addActionItem(new ActionItem(_T("Read log", "dyngroup"),"groupmsctabs","logfile","computer", "base", "computers", "grouptablogs"));
        }
        $n->addActionItem(new ActionItem(_T("Software deployment on this group", "dyngroup"),"groupmsctabs","install","computer", "base", "computers"));
    }
    if (in_array("update", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Update on this group", "dyngroup"),"view_updates", "reload", "id","base", "computers"));
    }
    $n->addActionItem(new ActionItem(_("Updates compliance by machines"),"detailsByMachines", "auditbymachine","updates", "updates", "updates") );
    //$n->addActionItem(new ActionItem(_("Deploy all update on this group"),"deployAllUpdates", "updateall","updates", "updates", "updates") );
    $n->addActionItem(new ActionItem(_("Deploy specific update on this group"),"deploySpecificUpdate", "updateone","updates", "updates", "updates") );
} else { // Imaging group
    $n->addActionItem(new ActionItem(_T("Display this imaging group's content", 'dyngroup'), "display", "display", "id", "imaging", "manage"));
    if (in_array("inventory", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Inventory on this imaging group", "dyngroup"),"groupinvtabs","inventory","inventory", "imaging", "manage"));
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this profile", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $n->addActionItem(new ActionItem(_T("Edit this imaging group", 'dyngroup'), "computersgroupedit", "edit", "id", "imaging", "manage"));
    $n->addActionItem(new ActionItem(_T("Share this imaging group", 'dyngroup'), "edit_share", "groupshare", "id", "imaging", "manage"));
    if (in_array("msc", $_SESSION["supportModList"])) {
        if (!in_array("xmppmaster", $_SESSION["supportModList"])) {
            $n->addActionItem(new ActionItem(_T("Read log", "dyngroup"),"groupmsctabs","logfile","computer", "imaging", "manage", "grouptablogs"));
        }
        $n->addActionItem(new ActionItem(_T("Software deployment on this imaging group", "dyngroup"),"groupmsctabs","install","computer", "imaging", "manage"));
    }
    if (in_array("imaging", $_SESSION["supportModList"])) {
        if (xmlrpc_isImagingInProfilePossible()) {
            $n->addActionItem(new ActionItem(_("Imaging management"),"groupimgtabs","imaging","computer", "imaging", "manage"));
        }
    }
    $n->addActionItem(new ActionItem(_("Updates compliance by machines"),"detailsByMachines", "auditbymachine","updates", "updates", "updates") );
}
 if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        // quick action for group with xmppmodule
        $n->addActionItemArray($actionxmppquickdeploy);
    }

$n->addActionItemArray($action_delete);

$n->addActionItem(new ActionItem(_T("Csv export", "dyngroup"),"csv","csv","computer", "base", "computers"));
//$n->disableFirstColumnActionLink();

$n->display();
?>
