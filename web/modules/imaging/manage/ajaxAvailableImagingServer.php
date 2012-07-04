<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
require_once("includes/config.inc.php");
require_once("includes/i18n.inc.php");
require_once("includes/acl.inc.php");
require_once("includes/session.inc.php");
require_once("includes/PageGenerator.php");
require_once("modules/imaging/includes/includes.php");
require_once('modules/imaging/includes/xmlrpc.inc.php');

$location = getCurrentLocation();

list($count, $imaging_server) = xmlrpc_getAllNonLinkedImagingServer();

if ($count == 0) {// we did not received at least one imaging_server
    $t = new TitleElement(_T("No imaging server available for association.", "imaging"), 3);
    $t->display();
    return;
}

// forge params
$params = getParams();
$addAction = new ActionPopupItem(sprintf(_T("Link this Imaging Server to the '%s' entity.", "imaging"), $location), "imaging_server_link", "addbootmenu", "master", "imaging", "manage");
$addActions = array();

$params['loc_id'] = $location;
$params['from'] = $_GET['from'];
$a_label = array();
$a_desc = array();
$a_in_boot_menu = array();
$i = -1;
foreach ($imaging_server as $entry) {
    $i = $i+1;
    $list_params[$i] = $params;
    $list_params[$i]["itemlabel"] = $entry['name'];
    $list_params[$i]["itemid"] = $entry['imaging_uuid'];
    // don't show action if service is in bootmenu
    $addActions[] = $addAction;

    $a_label[]= $entry['name'];
    $a_desc[]= $entry['url'];
    $a_uuid[]= $entry['packageserver_uuid'];
}


$t = new TitleElement(_T("Associate an entity to an imaging server", "imaging"));
$t->display();

// show images list
$l = new ListInfos($a_label, _T("Name", "imaging"));
$l->setParamInfo($list_params);
$l->addExtraInfo($a_desc, _T("Description", "imaging"));
$l->addExtraInfo($a_uuid, _T("Identifier", "imaging"));
$l->addActionItemArray($addActions);
$l->disableFirstColumnActionLink();
$l->setTableHeaderPadding(1);
$l->display();

?>
