<?php
/**
 * (c) 2022-2023 Siveo, http://siveo.net
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


require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/utilities.php");


global $conf;
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$maxperpage = $conf['global']['maxperpage'];
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

$login = $_SESSION['login'];

$profiles = xmlrpc_get_profiles_list($login, $start, $maxperpage, $filter);
$count = $profiles['total'];
$profiles = $profiles['datas'];

$action_editProfiles = new ActionItem(_T("Edit Profile", 'kiosk'), "edit", "edit", "profile", "kiosk", "kiosk");
$action_deleteProfile = new ActionItem(_T("Delete Profile", 'kiosk'), "deleteProfile", "delete", "profile", "kiosk", "kiosk");

$profiles_name = [];
$profiles_date = [];
$profiles_status = [];
$action_edit = [];
$action_delete = [];
$action_acknowledge = [];

$params = [];

foreach($profiles as $element) {
    $profiles_name[] = $element['name'];
    $profiles_status[] = ($element['active'] == 1) ? _T("Active", "kiosk") : _T("Inactive", "kiosk");
    $params[] = ['id' => $element['id'], 'name' => $element['name']];

    $action_edit[] = $action_editProfiles;
    $action_delete[] = $action_deleteProfile;
}

// Avoiding the CSS selector (tr id) to start with a number
$ids_kiosk = [];
foreach($profiles as $index => $name_kiosk) {
    $ids_kiosk[] = 'k_'.$name_kiosk['name'];
}

$n = new OptimizedListInfos($profiles_name, _T("Profile Name", "kiosk"));
$n->setcssIds($ids_kiosk);
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
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $count;
$n->display();
