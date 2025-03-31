<?php
/*
 * (c) 2022-2024 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse
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
require_once("modules/medulla_server/version.php");

$mod = new Module("urbackup");
$mod->setVersion("1.0");
$mod->setDescription(_T("Backup", "urbackup"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("urbackup");
$submod->setDescription(_T("Backup", "urbackup"));
$submod->setVisibility(True);
$submod->setImg('modules/urbackup/graph/navbar/urbackup');
$submod->setDefaultPage("urbackup/urbackup/index");
$submod->setPriority(500);

$page = new Page("index", _T('Review', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/index.php");
$submod->addPage($page);

$page = new Page("list_backups", _T('List Backups by Client', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/list_backups.php");
$submod->addPage($page);

$page = new Page("ajaxList_backups", _T('List Backups by Client', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/ajaxList_backups.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader"=>true));
$submod->addPage($page);

$page = new Page("start_backup", _T('Start backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/start_backup.php");
$submod->addPage($page);

$page = new Page("checkMachine", _T('Check machine if exist', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/checkMachine.php");
$submod->addPage($page);

$page = new Page("create_group", _T('Create group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/create_group.php");
$submod->addPage($page);

$page = new Page("add_member_togroup", _T('Assign member to group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/add_member_togroup.php");
$submod->addPage($page);

$page = new Page("add_member_togroup_aftercheck", _T('Assign member to group after add client', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/add_member_togroup_aftercheck.php");
$submod->addPage($page);

$page = new Page("edit_profile_settings", _T('Edit profile', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/edit_profile_settings.php");
$submod->addPage($page);

$page = new Page("list_computers_onprofile", _T('List computer on profile', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/list_computers_onprofile.php");
$submod->addPage($page);

$page = new Page("result_search_file", _T('File research by name', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/result_search_file.php");
$submod->addPage($page);

$page = new Page("restart_service", _T('Restart Service', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/restart_service.php");
$submod->addPage($page);

$page = new Page("validate_edit_group", _T('Validate save settings', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/validate_edit_group.php");
$submod->addPage($page);

$page = new Page("deleting_backup", _T('Delete backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/deleting_backup.php");
$submod->addPage($page);

$page = new Page("deleting_group", _T('Delete group', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/deleting_group.php");
$submod->addPage($page);

$page = new Page("deleting_client", _T('Delete client', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/deleting_client.php");
$submod->addPage($page);

$page = new Page("all_files_backup", _T('List of files from on backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/all_files_backup.php");
$submod->addPage($page);

$page = new Page("ajaxAll_files_backup", _T('List of files from on backup', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/ajaxAll_files_backup.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader"=>true));
$submod->addPage($page);

$page = new Page("basket", _T('List of Elements in Basket', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/basket.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader"=>true));
$submod->addPage($page);

$page = new Page("restore_file", _T('Restore file', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/restore_file.php");
$submod->addPage($page);

$page = new Page("download_file", _T('Download file', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/download_file.php");
$submod->addPage($page);

$page = new Page("profileslist", _T('Profiles', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/profileslist.php");
$submod->addPage($page);

$page = new Page("logs", _T('Logs', 'urbackup'));
$page->setFile("modules/urbackup/urbackup/logs.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>
