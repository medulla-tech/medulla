<?php
/**
 * (c) 2018 Siveo, http://siveo.net
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */


require("modules/kiosk/graph/index.css");
require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/pulse2/includes/utilities.php");
require("graph/navbar.inc.php");
require("modules/kiosk/kiosk/localSidebar.php");


if(isset($_GET['action'],$_GET['id']) && $_GET['action'] == "delete")
{
    xmlrpc_delete_profile($_GET['id']);
    //TODO : Add notification when the profile is deleted
}


$p = new PageGenerator(_T("List of profils",'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$profiles = xmlrpc_get_profiles_list();

$action_editProfiles = new ActionItem(_T("Edit Profile",'kiosk'), "edit", "edit", "profile", "kiosk", "kiosk");
$action_deleteProfile = new ActionItem(_T("Delete Profile",'kiosk'), "delete", "delete", "profile", "kiosk", "kiosk");

$profiles_name = [];
$profiles_date = [];
$profiles_status = [];
$action_edit = [];
$action_delete = [];

$params = [];

$count = count($profiles);
foreach($profiles as $element)
{
    $profiles_name[] = $element['name'];
    $profiles_status[] = ($element['active'] == 1) ? _T("Active","kiosk") : _T("Inactive","kiosk");
    $params[] = ['id'=>$element['id'], 'name'=>$element['name']];

    $action_edit[] = $action_editProfiles;
    $action_delete[] = $action_deleteProfile;
}
$n = new OptimizedListInfos($profiles_name, _T("Profile Name", "kiosk"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($profiles_status, _T("Profile Status", "kiosk"));
// parameters are :
// - label
// - action
// - class (icon)
// - profile get parameter
// - module
// - submodule
$n->setParamInfo($params);
$n->addActionItemArray($action_edit);
$n->addActionItemArray($action_delete);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter1));

$n->display();
?>
