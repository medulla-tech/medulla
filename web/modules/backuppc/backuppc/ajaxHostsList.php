<?
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/msc/includes/utilities.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = array('filter'=> $_GET["filter"], 'location'=> $_GET['location']);
$filter1 = $_GET["filter"]. '##'.$_GET['location'];

if ($_GET['location']) {
    //$filter['packageapi'] = getPApiDetail(base64_decode($_GET['location']));
    print "";
}
if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

$response = get_host_list($_GET['filter']);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

$hosts = $response['data'];
$count = count($hosts);

//print($_GET["filter"]."=");
//print($_GET["location"]);

$n = new OptimizedListInfos($hosts, _T("Host name", "backuppc"));
$n->setCssClass("machineName"); // CSS for icons
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->start = isset($_GET['start'])?$_GET['start']:0;
$n->end = isset($_GET['end'])?$_GET['end']:$maxperpage;

$n->addActionItem(new ActionItem(_T("View", "backuppc"),"BrowseBackups","display","host", "backuppc", "backuppc"));
$n->addActionItem(new ActionItem(_T("Edit config", "backuppc"),"edit","edit","host", "backuppc", "backuppc"));
//$n->addActionItem(new ActionPopupItem(_T("Delete", "pkgs"),"delete","delete","host", "backuppc", "backuppc"));

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();

?>
