<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require_once("modules/medulla_server/version.php");
$mod = new Module("store");
$mod->setVersion("1.0");
$mod->setDescription(_T("Store", "store"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);
$submod = new SubModule("store");
$submod->setDescription(_T("Store", "store"));
$submod->setVisibility(True);
$submod->setImg('modules/store/graph/navbar/store');
$submod->setDefaultPage("store/store/index");
$submod->setPriority(3000);

$page = new Page("index", _T('Medulla Store', 'store'));
$page->setFile("modules/store/store/index.php");
$submod->addPage($page);

$page = new Page("deploy", _T('Deploy Package', 'store'));
$page->setFile("modules/store/store/deploy.php");
$page->setOptions(array("visible" => False, "noHeader" => False));
$submod->addPage($page);

$page = new Page("ajaxMachinesListForDeploy", _T('Machines List', 'store'));
$page->setFile("modules/store/store/ajaxMachinesListForDeploy.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

$page = new Page("ajaxGroupsListForDeploy", _T('Groups List', 'store'));
$page->setFile("modules/store/store/ajaxGroupsListForDeploy.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

$page = new Page("ajaxSearchMachines", _T('Search Machines', 'store'));
$page->setFile("modules/store/store/ajaxSearchMachines.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

$page = new Page("startDeploy", _T('Start Deploy', 'store'));
$page->setFile("modules/store/store/startDeploy.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("subscribe", _T('Update Subscription', 'store'));
$page->setFile("modules/store/store/subscribe.php");
$submod->addPage($page);

$page = new Page("ajaxCatalogList");
$page->setFile("modules/store/store/ajaxCatalogList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

$page = new Page("ajaxSubscribeList");
$page->setFile("modules/store/store/ajaxSubscribeList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

$mod->addSubmod($submod);
$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);
?>
