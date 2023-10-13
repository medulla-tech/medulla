<?php
/**
 * (c) 2022-2023 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

require_once("modules/pulse2/version.php");

$mod = new Module("testenv");
$mod->setVersion("1.0");
//$mod->setRevision('');
$mod->setDescription(_T("Testenv", "Testenv"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("testenv");
$submod->setDescription(_T("Testenv", "Testenv"));
$submod->setVisibility(True);
$submod->setImg('modules/testenv/graph/navbar/testenv');
$submod->setDefaultPage("testenv/testenv/index");
$submod->setPriority(500);

$page = new Page("index", _T('List of virtual machines', 'testenv'));
$submod->addPage($page);

$page = new Page("ajaxListVM", _T("List of virtual machines", "testenv"));
$page->setFile("modules/testenv/testenv/ajaxListVM.php");
$page->setOptions(array("AJAX"=>True, "visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("create", _T('Create a virtual machine', 'testenv'));
$page->setFile("modules/testenv/testenv/create.php");
$submod->addPage($page);

$page = new Page("delete", _T('Delete a virtual machine', 'testenv'));
$page->setFile("modules/testenv/testenv/delete.php");
$submod->addPage($page);

$page = new Page("stop", _T('Stop a virtual machine', 'testenv'));
$page->setFile("modules/testenv/testenv/stop.php");
$submod->addPage($page);

$page = new Page("start", _T('Start a virtual machine', 'testenv'));
$page->setFile("modules/testenv/testenv/start.php");
$submod->addPage($page);

$page = new Page("launch", _T('Launch a virtual machine', 'testenv'));
$page->setFile("modules/testenv/testenv/launch_vm.php");
$page->setOptions(array("AJAX"=>True, "visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("launch2", _T('Launch a virtual machine', 'testenv'));
$page->setFile("modules/testenv/testenv/launch_vm.php");
$submod->addPage($page);

$page = new Page("edit", _T('Edit a virtual machine', 'testenv'));
$page->setFile("modules/testenv/testenv/edit.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); 
?>
