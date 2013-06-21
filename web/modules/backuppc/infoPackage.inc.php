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

/**
 * module declaration
 */
require_once("modules/pulse2/version.php");

$mod = new Module("backuppc");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Backup", "backuppc"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(800);

$submod = new SubModule("backuppc");
$submod->setDescription(_T("Backup", "backuppc"));
$submod->setImg('modules/backuppc/img/navbar/bpc');
$submod->setDefaultPage("backuppc/backuppc/index");

$page = new Page("index", _T('Backup status', 'backuppc'));
$submod->addPage($page);

$page = new Page("hostStatus", _T('Host backup status', 'backuppc'));
$submod->addPage($page);

$page = new Page("hostSummary", _T('Host summary', 'backuppc'));
$page->setOptions(array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("edit", _T('Edit host config', 'backuppc'));
$page->setOptions(array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("EditBackupProfile", _T('Edit Backup Profile', 'backuppc'));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("EditPeriodProfile", _T('Edit Backup period Profile', 'backuppc'));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("pending", _T('See pending packages', 'backuppc'));
$submod->addPage($page);

$page = new Page("BrowseBackups", _T('Restore points', 'backuppc'));
$submod->addPage($page);

$page = new Page("BrowseShareNames", _T('Share names', 'backuppc'));
$submod->addPage($page);

$page = new Page("BrowseFiles", _T('Browse files', 'backuppc'));
$submod->addPage($page);

$page = new Page("ViewProfiles", _T('Backup Profiles', 'backuppc'));
$submod->addPage($page);

$page = new Page("deleteProfile",_T("Delete profile", 'backuppc'));
$page->setFile("modules/backuppc/backuppc/deleteProfile.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

// ========= RESTORE PAGES ===============

$page = new Page("download");
$page->setFile("modules/backuppc/backuppc/download.php");
$submod->addPage($page);

$page = new Page("restorePopup");
$page->setFile("modules/backuppc/backuppc/restorePopup.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxRestoreFile");
$page->setFile("modules/backuppc/backuppc/ajaxRestoreFile.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxDownloadsTable");
$page->setFile("modules/backuppc/backuppc/ajaxDownloadsTable.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("viewFileVersions");
$page->setFile("modules/backuppc/backuppc/viewFileVersions.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("viewXferLog");
$page->setFile("modules/backuppc/backuppc/viewXferLog.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("restoreZip");
$page->setFile("modules/backuppc/backuppc/restoreZip.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("restoreToHost");
$page->setFile("modules/backuppc/backuppc/restoreToHost.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);


// AJAX PAGES
$page = new Page("ajaxHostsList");
$page->setFile("modules/backuppc/backuppc/ajaxHostsList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxBrowseBackups");
$page->setFile("modules/backuppc/backuppc/ajaxBrowseBackups.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxBrowseShareNames");
$page->setFile("modules/backuppc/backuppc/ajaxBrowseShareNames.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);


$page = new Page("ajaxBrowseFiles");
$page->setFile("modules/backuppc/backuppc/ajaxBrowseFiles.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);


$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
