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

// Prevent from corrupting files due to indesirable prints
//ob_end_clean();
//set_time_limit(-1);

require_once("includes/xmlrpc.inc.php");
require_once('modules/backuppc/includes/xmlrpc.php');

$host = $_POST['host'];
$backupnum = $_POST['backupnum'];
$sharename = $_POST['sharename'];

// unset no-files vars
unset($_POST['host']);
unset($_POST['backupnum']);
unset($_POST['sharename']);
unset($_POST['restoredir']);

if (isset($_GET['dir']))
    $files=array($_GET['dir']);
else
    $files = array_values($_POST);

$files[]=':';

restore_file($host,$backupnum,$sharename,$files);

$_GET['host'] = $host;
$_GET['backupnum'] = $backupnum;
$_GET['sharename'] = $sharename;
include('modules/backuppc/backuppc/BrowseFiles.php');

new NotifyWidgetSuccess(_T('Your ZIP file is being prepared, please wait.','backuupc'));

?>
