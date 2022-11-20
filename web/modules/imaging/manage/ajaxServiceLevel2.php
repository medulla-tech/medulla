<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require('../includes/xmlrpc.inc.php');

$location = $_SESSION['imaging_location']['used'];

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$start = empty($_GET["start"]) || $_GET["start"] == ''    ? 0              : $_GET["start"];
$end = empty($_GET["end"]) || $_GET["end"] == ''          ? $maxperpage    : $_GET["end"];
$filter = empty($_GET["filter"])                          ? ''             : $_GET['filter'];


list($count, $services) = xmlrpc_getLocationBootServices($location, $start, $end, $filter);

// forge params
$params = getParams();
$addAction = new ActionPopupItem(_T("Add service to default boot menu", "imaging"), "service_add", "addbootmenu", "master", "imaging", "manage");
$delAction = new ActionPopupItem(_T("Remove service from default boot menu", "imaging"), "service_del", "delbootmenu", "master", "imaging", "manage");
$remAction = new ActionPopupItem(_T("Delete service", "imaging"), "service_remove", "removebootmenu", "master", "imaging", "manage");
$showAction = new ActionPopupItem(_T("Show where service is used", "imaging"), "service_show_used", "showbootmenu", "master", "imaging", "manage");
$emptyAction = new EmptyActionItem();

$addActions = array();
$remActions = array();

$a_label = array();
$a_desc = array();
$a_in_boot_menu = array();
$i = -1;

foreach ($services as $entry) {
    $i = $i+1;
    $list_params[$i] = $params;
    $list_params[$i]["itemlabel"] = $entry['default_name'];
    $list_params[$i]["itemid"] = $entry['imaging_uuid'];
    // don't show action if service is in bootmenu
    if(!isset($entry['menu_item'])) {
        $addActions[] = $addAction;
    } else {
        $addActions[] = $delAction;
    }

    if ($entry['id'] >= 1000) {
        $remActions[] = ($entry['used_bs_id']) ? $showAction : $remAction;
    }
    else {
        $remActions[] = $emptyAction;
    }

    $icon = '<img src="img/other/confitem.svg" style="vertical-align: middle" width="25" height="25" /> ';

    $a_label[]= sprintf("%s%s", $icon, $entry['default_name']);
    $a_desc[]= $entry['default_desc'];
    $a_in_boot_menu[]= (isset($entry['menu_item'])? True:False);
}


// show images list
$l = new OptimizedListInfos($a_label, _T("Label", "imaging"));
$l->setParamInfo($list_params);
$l->addExtraInfo($a_desc, _T("Description", "imaging"));
$l->addExtraInfo($a_in_boot_menu, _T("In boot menu", "imaging"));
$l->addActionItemArray($addActions);
/* should we be able to to that ?!
$l->addActionItem(
    new ActionItem(_T("Edit service", "imaging"),
    "service_edit", "edit", "master", "imaging", "manage")
);*/
$l->addActionItemArray($remActions);
$l->setTableHeaderPadding(19);
$l->disableFirstColumnActionLink();
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamformLevel2"));
$l->start = 0;
$l->end = $maxperpage;
$l->display();
?>
