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

if (!isset($_GET['location']))
   return;
else
    $location = $_GET['location'];

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

$response = get_global_status($location);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

$data = $response['data'];

if (count($data) == 0){
    print _T('No entry found.','backuppc');
    return;
}

$count = count($data['hosts']);

$n = new OptimizedListInfos($data['hosts'], _T("Host name", "backuppc"));
$n->addExtraInfo($data['full'], _T("Full number", "backuppc"));
$n->addExtraInfo($data['full_size'], _T("Full size (GB)", "backuppc"));
$n->addExtraInfo($data['incr'], _T("incr. number", "backuppc"));
$n->addExtraInfo($data['last_backup'], _T("Mast backup (days)", "backuppc"));
$n->addExtraInfo($data['state'], _T("Current state", "backuppc"));
$n->addExtraInfo($data['last_attempt'], _T("Last message", "backuppc"));
$n->setCssClass("machineName"); // CSS for icons
$n->setItemCount($count);
$filter1 = $_GET['location'];
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->start = isset($_GET['start'])?$_GET['start']:0;
$n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage)-1;

//$n->addActionItem(new ActionItem(_T("View", "backuppc"),"BrowseBackups","display","host", "backuppc", "backuppc"));
//$n->addActionItem(new ActionItem(_T("Edit config", "backuppc"),"edit","edit","host", "backuppc", "backuppc"));

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();

?>
