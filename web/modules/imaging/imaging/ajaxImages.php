<?

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

//require_once('modules/imaging/includes/includes.php');
//require_once('modules/imaging/includes/xmlrpc.inc.php');
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require_once('../includes/xmlrpc.inc.php');

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET['gid']) && $_GET['gid'] != '') {
    $type = 'group';
    $target_uuid = $_GET['gid'];
    $target_name = $_GET['groupname'];
} else {
    $type = '';
    $target_uuid = $_GET['uuid'];
    $target_name = $_GET['hostname'];
}

$displayMaster = isset($_GET['master']);
$start = empty($_GET["start"])              ? 0              : $_GET["start"];
$end = empty($_GET["end"])                  ? $maxperpage    : $_GET["end"];
$filter = empty($_GET["filter"])            ? ''             : $_GET['filter'];
$actions = !$displayMaster;
$is_in_profile = False;

if ($type == 'group') {
    $all = xmlrpc_getProfileImages($_GET['gid'], $start, $end, $filter);
} else {
    $all = xmlrpc_getComputerImages($_GET['uuid'], $start, $end, $filter);
}

if ($displayMaster) {
    list($count, $images) = $all['masters'];
} else {
    list($count, $images) = $all['images'];
}
$params = getParams();

$addActions = array();
$addAction = new ActionPopupItem(_T("Add image to boot menu", "imaging"), "addimage", "addbootmenu", "image", "base", "computers", null, 300, "add");
$delAction = new ActionPopupItem(_T("Remove from boot menu", "imaging"), "bootmenu_remove", "delbootmenu", "item", "base", "computers", $type."tabbootmenu", 300, "delete");
$emptyAction = new EmptyActionItem();
$destroyAction = new ActionPopupItem(_T("Delete the image", "imaging"), "images_delete", "delete", "image", "base", "computers", $type."tabimages", 300, "delete");
$showImAction = new ActionPopupItem(_T("Show target using that image", "imaging"), "showtarget", "showtarget", "image", "base", "computers");

$editActions = array();
$editAction = new ActionItem(_T("Edit image", "imaging"), "imgtabs", "edit", "image", "base", "computers", $type."tabimages", "edit");

$logAction = new ActionItem(_T("View image log", "imaging"), "imgtabs", "logfile", "image", "base", "computers", $type."tabimages", "log");

// forge params
$params['from'] = 'tabimages';
$list_params = array();
$a_label = array();
$a_desc = array();
$a_desc = array();
$a_date = array();
$a_size = array();
$a_fromprofile = array();
$a_inbootmenu = array();
$a_destroy = array();
$a_logs = array();
$a_info = array();
$l_im = array();
foreach ($images as $image) {
    $name = $image['name'];
    $l_params = $params;
    $l_params["itemid"] = $image['imaging_uuid'];
    $l_params["itemlabel"] = urlencode($name);
    $l_params["target_uuid"] = $_GET['target_uuid'];

    // don't show action if image is in bootmenu
    if(!isset($image['menu_item'])) {
        $addActions[] = $addAction;
    } elseif ($image['read_only']) {
        $addActions[] = $emptyAction;
        $is_in_profile = True;
    } else {
        $addActions[] = $delAction;
        $l_params['mi_itemid'] = $image['menu_item']['imaging_uuid'];
    }

    if ($_GET['target_uuid'] == $image['mastered_on_target_uuid']) {
        $editActions[] = $editAction;
    } else {
        $editActions[] = $emptyAction;
    }

    $list_params[] = $l_params;
    # TODO no label in image!
    $a_label[] = sprintf("%s%s", '<img src="modules/imaging/graph/images/imaging-action.png" style="vertical-align: middle" /> ', $name);
    $a_desc[] = $image['desc'];
    $a_date[] = _toDate($image['creation_date']);
    $a_size[] = humanReadable($image['size']);
    $a_inbootmenu[] = (isset($image['menu_item']) ? True : False);
    $a_fromprofile[] = ($image['read_only'] ? True : False);
    $a_info []= sprintf("Plop: %s", $image['fk_status']);
    $l_im[] = array($image['imaging_uuid'], $_GET['target_uuid'], $type);
}

if (!$actions) {
    if (count($l_im) != 0) {
        $ret = xmlrpc_areImagesUsed($l_im);
        foreach ($images as $image) {
            if ($ret[$image['imaging_uuid']]) {
                $a_destroy[] = $showImAction;
            } else {
                $a_destroy[] = $destroyAction;
            }
        }
    }
}

// show images list
$l = new OptimizedListInfos($a_label, _T("Label", "imaging"));
$l->setParamInfo($list_params);
$l->addExtraInfo($a_desc, _T("Description", "imaging"));
$l->addExtraInfo($a_date, _T("Created", "imaging"));
$l->addExtraInfo($a_size, _T("Size (compressed)", "imaging"));
$l->addExtraInfo($a_inbootmenu, _T("In boot menu", "imaging"));
if ($is_in_profile) {
    $l->addExtraInfo($a_fromprofile, _T("From profile", "imaging"));
}

$l->addActionItemArray($addActions);

$l->addActionItem(
        new ActionPopupItem(_T("Create bootable iso", "imaging"),
        "images_iso", "backup", "image", "base", "computers")
);

// if not in boot menu
if ($actions) {
    $l->addActionItem(
        new ActionItem(_T("Edit image", "imaging"),
        "imgtabs", "edit", "image", "base", "computers", $type."tabimages", "edit")
    );
    $l->addActionItem($logAction);
    $l->addActionItem($destroyAction);
} else {
    $l->addActionItemArray($editActions);
    $l->addActionItem($logAction);
    $l->addActionItemArray($a_destroy);
}

$l->disableFirstColumnActionLink();
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform".($actions?'image':'master')));
$l->start = 0;
$l->end = $maxperpage;
$l->setTableHeaderPadding(19);
$l->display();

?>

<!-- inject styles -->
<link rel="stylesheet" href="modules/imaging/graph/css/imaging.css" type="text/css" media="screen" />


