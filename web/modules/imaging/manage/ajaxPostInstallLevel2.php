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

/*
 * Post-installation scripts list page
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

list($count, $scripts) = xmlrpc_getAllPostInstallScripts($location, $start, $end, $filter);

$editAction = new ActionItem(_T("Edit script", "imaging"), "postinstall_edit", "edit", "image", "imaging", "manage");
$deleteAction = new ActionPopupItem(_T("Delete", "imaging"), "postinstall_delete", "delete", "image", "imaging", "manage");
$emptyAction = new EmptyActionItem();

$a_edit = array();
$a_delete = array();
$a_label = array();
$a_desc = array();
foreach($scripts as $script) {

    if ($script['is_local']) {
        $url = '<img src="modules/imaging/graph/images/postinst-action.png" style="vertical-align: middle" /> ';
        $a_edit[] = $editAction;
        $a_delete[] = $deleteAction;
    } else {
        $url = '<img src="modules/imaging/graph/images/postinst-action-ro.png" style="vertical-align: middle" /> ';
        $a_edit[] = $emptyAction;
        $a_delete[] = $emptyAction;
    }
    $a_label[]= sprintf("%s%s", $url, $script['default_name']);
    $a_desc[] = $script["default_desc"];
    $l_params = array();
    $l_params["itemid"] = $script['imaging_uuid'];
    $l_params["itemlabel"] = $script["default_name"];
    $list_params[] = $l_params;

}

// show scripts list
$l = new OptimizedListInfos($a_label, _T("Name", "imaging"));
$l->addExtraInfo($a_desc, _T("Description", "imaging"));
$l->setParamInfo($list_params);
$l->addActionItemArray($a_edit);
$l->addActionItem(
    new ActionItem(_T("Duplicate", "imaging"),
    "postinstall_duplicate", "duplicatescript", "image", "imaging", "manage")
);
$l->addActionItem(
    new ActionItem(_T("Create Boot Service", "imaging"),
    "postinstall_create_boot_service", "duplicatescript", "image", "imaging", "manage")
);
$l->addActionItemArray($a_delete);

$l->setTableHeaderPadding(19);
$l->disableFirstColumnActionLink();
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamformLevel2"));
$l->start = 0;
$l->end = $maxperpage;
$l->display();

?>
