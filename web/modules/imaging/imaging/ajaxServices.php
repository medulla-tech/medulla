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

require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require_once('../includes/xmlrpc.inc.php');

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$type = $_GET['target_type'];
$target_uuid = $_GET['target_uuid'];
$target_name = $_GET['target_name'];

$start = empty($_GET["start"])              ? 0              : $_GET["start"];
$end = empty($_GET["end"])                  ? $maxperpage    : $_GET["end"];
$filter = empty($_GET["filter"])            ? ''             : $_GET['filter'];
$is_in_profile = False;

list($count, $menu) = xmlrpc_getPossibleBootServices($target_uuid, $start, $end, $filter);

$params = getParams();

$addActions = array();
$addAction = new ActionPopupItem(_T("Add service to boot menu", "imaging"), "addservice", "addbootmenu", "image", "base", "computers", null, 300, "add");
$delAction = new ActionPopupItem(_T("Remove service from boot menu"), "bootmenu_remove", "delbootmenu", "item", "base", "computers", $type."tabbootmenu", 300, "delete");
$emptyAction = new EmptyActionItem();

// show services list
$a_label = array();
$a_desc = array();
$a_in_boot_menu = array();
$a_from_profile = array();
$params['from'] = 'tabservices';

foreach ($menu as $entry) {
    $l_params = $params;
    $l_params["itemlabel"] = $entry['default_name'];
    $l_params["itemid"] = $entry['imaging_uuid'];
    $l_params['targetid'] = $targetid;

    // don't show action if service is in bootmenu
    if(!isset($entry['menu_item'])) {
        $addActions[] = $addAction;
    } elseif ($entry['menu_item']['read_only']) {
        $is_in_profile = True;
        $addActions[] = $emptyAction;
    } else {
        $addActions[] = $delAction;
        $l_params["mi_itemid"] = $entry['menu_item']['imaging_uuid'];
    }

    $list_params[]= $l_params;
    $icon = '<img src="modules/imaging/graph/images/service-action.png" style="vertical-align: middle" /> ';
    $a_label[]= sprintf("%s%s", $icon, $entry['default_name']);
    $a_desc[]= $entry['default_desc'];
    $a_in_boot_menu[]= (isset($entry['menu_item'])? True:False);
    $a_from_profile[]= (isset($entry['menu_item'])? ($entry['menu_item']['read_only'] ? True:False):False);
}

$l = new OptimizedListInfos($a_label, _T("Label", "imaging"));
$l->addExtraInfo($a_desc, _T("Description", "imaging"));
$l->addExtraInfo($a_in_boot_menu, _T("In bootmenu", "imaging"));
if ($is_in_profile) {
    $l->addExtraInfo($a_from_profile, _T("From profile", "imaging"));
}
$l->setParamInfo($list_params);
$l->addActionItemArray($addActions);
$l->disableFirstColumnActionLink();
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamLevel2"));
$l->start = 0;
$l->end = $maxperpage;
$l->setTableHeaderPadding(19);
$l->display();

?>
