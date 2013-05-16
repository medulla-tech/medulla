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

$params = getParams();
$location = $_SESSION['imaging_location']['used'];

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$start = empty($_GET["start"]) || $_GET["start"] == ''    ? 0              : $_GET["start"];
$end = empty($_GET["end"]) || $_GET["end"] == ''          ? $maxperpage    : $_GET["end"];
$filter = empty($_GET["filter"])                          ? ''             : $_GET['filter'];

list($count, $masters) = xmlrpc_getLocationImages($location, $start, $end, $filter);

if ($count == 0) {
    $l = new TitleElement(_T('No master available.', 'imaging'), 3);
    $l->display();
    print "<p>" . _T('To define a master, browse to the computers module ' .
           'click on the imaging icon for the computer you wish to make a master from, then choose &quot;Images and ' .
           'Masters&quot;, followed by clicking the edit button on a backup image to convert it to a master.', 'imaging') . "</p>";
    return;
}
// forge params
$addAction = new ActionPopupItem(_T("Add image to default boot menu", "imaging"), "master_add", "addbootmenu", "master", "imaging", "manage");
$delAction = new ActionPopupItem(_T("Remove from boot menu", "imaging"), "master_remove", "delbootmenu", "master", "imaging", "manage", $type."tabbootmenu", 300, "delete");
$emptyAction = new EmptyActionItem();
$addActions = array();

$a_label = array();
$a_desc = array();
$a_date = array();
$a_size = array();
$a_is_in_menu = array();
$a_destroy = array();
$l_im = array();

$destroyAction = new ActionPopupItem(_T("Delete", "imaging"), "master_delete", "delete", "master", "imaging", "manage");
$showImAction = new ActionPopupItem(_T("Show target using that image", "imaging"), "showtarget", "showtarget", "image", "base", "computers");

foreach ($masters as $master) {
    $l_params = array();
    $l_params = $params;
    $l_params["itemid"] = $master['imaging_uuid'];
    $l_params["itemlabel"] = urlencode($master['name']);

    if (!$master['menu_item']) {
        $addActions[] = $addAction;
    } else {
        $addActions[] = $delAction;
    }

    $list_params[] = $l_params;

    $a_label[] = sprintf("%s%s", '<img src="modules/imaging/graph/images/imaging-action.png" style="vertical-align: middle" /> ', $master['name']);
    $a_desc[] = $master['desc'];
    $a_date[] = _toDate($master['creation_date']);
    $a_size[] = humanReadable($master['size']);
    $a_is_in_menu[] = ($master['menu_item']?True:False);
    $l_im[] = array($master['imaging_uuid'], null, null);
}

if (count($l_im) != 0) {
    $ret = xmlrpc_areImagesUsed($l_im);
    foreach ($masters as $image) {
        if ($ret[$image['imaging_uuid']]) {
            $a_destroy[] = $showImAction;
        } else {
            $a_destroy[] = $destroyAction;
        }
    }
}


// show images list
$l = new OptimizedListInfos($a_label, _T("Label", "imaging"));
$l->setParamInfo($list_params);
$l->addExtraInfo($a_desc, _T("Description", "imaging"));
$l->addExtraInfo($a_date, _T("Created", "imaging"));
$l->addExtraInfo($a_size, _T("Size (compressed)", "imaging"));
$l->addExtraInfo($a_is_in_menu, _T("In default boot menu", "imaging"));
$l->addActionItemArray($addActions);
$l->addActionItem(
    new ActionPopupItem(_T("Create bootable iso", "imaging"),
    "master_iso", "backup", "master", "imaging", "manage")
);
$l->addActionItem(
    new ActionItem(_T("Edit image", "imaging"),
    "master_edit", "edit", "master", "imaging", "manage")
);

$l->addActionItemArray($a_destroy);

$l->setTableHeaderPadding(1);
$l->disableFirstColumnActionLink();
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamformLevel2"));
$l->start = 0;
$l->end = $maxperpage;
$l->display();


?>

<!-- inject styles -->
<link rel="stylesheet" href="modules/imaging/graph/css/imaging.css" type="text/css" media="screen" />

