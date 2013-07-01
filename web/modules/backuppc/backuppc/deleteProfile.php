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


require_once("modules/backuppc/includes/xmlrpc.php");


if (isset($_POST["bconfirm"])) {
    $id = intval($_POST["id"]);
    $type = $_POST["type"];
    
    // If id not set, or default profile exit script
    if (!$id or $id<1000) return;

    // Deleting fileset or period according to type
    if ($type == 0)
        $ret = delete_backup_profile($id);
    else
        $ret = delete_period_profile($id);
    
    if (!isXMLRPCError() and $ret != -1) 
        new NotifyWidgetSuccess(_T("The profile has been deleted successfully.", "backuppc"));
    
    if ($ret == -1) 
        new NotifyWidgetFailure(_T("Failed to delete the selected profile", "backuppc"));
    
    header("Location: " . urlStrRedirect("backuppc/backuppc/ViewProfiles"));
    return;    
} 
else 
{
    $id = $_GET["id"];
    $type = $_GET["type"];

    // If default profile, we can't delete
    if ($id < 1000)
        print _T('Error : Default profiles cannot be deleted','backuppc');
    
    $f = new PopupForm(_T("Delete this profile"));
    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $id, "hide" => True));
    $hidden = new HiddenTpl("type");
    $f->add($hidden, array("value" => $type, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

?>
