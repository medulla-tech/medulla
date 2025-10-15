<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
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

$mod = new Module("medulla_server");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Medulla", "pulse2"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(700);

/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

$page = new Page("computers_list", _T("Computers list", "pulse2"));
$page->setOptions(array("visible"=>False));
$page->setFile("modules/medulla_server/medulla_server/computers_list.php");
$submod->addPage($page);

$page = new Page("select_location", _T("Location selection in computer edit", "pulse2"));
$page->setOptions(array("visible"=>False));
$page->setFile("modules/medulla_server/includes/select_location.php");
$submod->addPage($page);

unset($submod);

// Module update
$submod = new SubModule("update");
$submod->setImg('modules/xmppmaster/img/navbar/xmppmaster');
$submod->setDescription(_T("update", "pulse2"));
$submod->setVisibility(False);

$page = new Page("viewProductUpdates", _T("viewProductUpdates", "pulse2"));
$page->setFile("modules/medulla_server/update/viewProductUpdates.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("installProductUpdates",_T('install Product Updates', 'pulse2'));
$page->setFile("modules/medulla_server/update/installProductUpdates.php");
$submod->addPage($page);

$page = new Page("ajaxInstallProductUpdates", _T("Product Updates installation (ajax)", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("restartAllMedullaServices", _T('Restart All Medulla Services', 'medulla_server'));
$page->setFile("modules/medulla_server/update/restartAllMedullaServices.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("regenerateAgent",_T('Regenerate Agent', 'medulla_server'));
$page->setFile("modules/medulla_server/update/regenerateAgent.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);
