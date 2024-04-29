<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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


require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/medulla/includes/utilities.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$cn = "";
if (isset( $_GET['objectUUID'])) {
    $filter = array('hostname' => $_POST["uuid"]);
    $cl = getRestrictedComputersList(0, -1, $filter, False);
    foreach ($cl as $k => $v) {
        $cn = $v[1]['cn'][0];
    }
    // xmlrpc_getPresenceuuid
    // xmlrpc_getjidMachinefromuuid
}

// Unset backup for selected host
if (isset($_GET['objectUUID'])){
    unset_backup_for_host($_GET['objectUUID']);
    if (!isXMLRPCError()) {
    xmlrpc_setfromxmppmasterlogxmpp("Notify : The computer $cn has been removed from the backup system.",
                                    "BPC",
                                    '',
                                    0,
                                    $cn ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Backup | Full Removed Starting | Manual');
        new NotifyWidgetSuccess(_("The computer has been removed from the backup system."));
    }
}

$p = new PageGenerator(_T("Backup status", 'backuppc'));
$p->setSideMenu($sidemenu);
$p->display();

/*if (displayLocalisationBar()) {
    $location = getCurrentLocation();*/

$ajax = new AjaxFilterLocation(urlStrRedirect("backuppc/backuppc/ajaxBackupStatus"));

list($list, $values) = getEntitiesSelectableElements();
$ajax->setElements($list);
$ajax->setElementsVal($values);
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();

?>
<script>jQuery('#location option[value="UUID1"]').prop('selected', true);</script>
