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
require_once("modules/backuppc/includes/functions.php");
require_once("modules/backuppc/includes/html.inc.php");

// ===========================================================================
// Receive form data
if (isset($_POST['bAdvScripts'])){
    
    $host = $_POST['host'];
    
    // Setting the scripts
    set_host_pre_backup_script($host, $_POST['pre_backup_script']);
    set_host_post_backup_script($host, $_POST['post_backup_script']);
    set_host_pre_restore_script($host, $_POST['pre_restore_script']);
    set_host_post_restore_script($host, $_POST['post_restore_script']);
    
    new NotifyWidgetSuccess(_T('Configuration saved', 'backuppc'));
    
}
// ===========================================================================

// display an edit config form
$f = new ValidatingForm();
$f->push(new Table());

$host = $_GET['objectUUID'];

$pre_backup_script = get_host_pre_backup_script($host);
$post_backup_script = get_host_post_backup_script($host);
$pre_restore_script = get_host_pre_restore_script($host);
$post_restore_script = get_host_post_restore_script($host);



// BackupPC config for this host
$host_config = $response['host_config'];

$f->add(new HiddenTpl("host"), array("value" => $host, "hide" => True));

$f->add(
    new TrFormElement(_T("Pre-backup script", "backuppc"), new TextareaTpl('pre_backup_script')), array("value" => htmlspecialchars($pre_backup_script))
);

$f->add(
        new TrFormElement(_T("Post-backup script", "backuppc"), new TextareaTpl('post_backup_script')), array("value" => htmlspecialchars($post_backup_script))
);

$f->add(
        new TrFormElement(_T("Pre-restore script", "backuppc"), new TextareaTpl('pre_restore_script')), array("value" => htmlspecialchars($pre_restore_script))
);

$f->add(
        new TrFormElement(_T("Post-restore script", "backuppc"), new TextareaTpl('post_restore_script')), array("value" => htmlspecialchars($post_restore_script))
);

$f->pop();
$f->addValidateButton("bAdvScripts");
$f->display();
?>
