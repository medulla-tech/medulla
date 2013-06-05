<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * dashboard module declaration
 */

$MMCApp =& MMCApp::getInstance();
/* Get the base module instance reference */
$base = &$MMCApp->getModule('base');
/* Get the main sub-module instance reference */
$main = &$base->getSubmod('main');

$mod = new Module("dashboard");
$mod->setVersion("3.1.0");
$mod->setRevision('');
$mod->setDescription(_T("Dashboard", "dashboard"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(-10);

$submod = new SubModule("main", _T("Dashboard", "dashboard"));
$submod->setImg('modules/dashboard/graph/navbar/dashboard');
$submod->setDefaultPage("dashboard/main/default");
$submod->setPriority(-10);

/* Add the dashboard to the main module */
$page = new Page("default", _T("Dashboard", "dashboard"));
$page->setFile("modules/dashboard/main/default.php");
$submod->addPage($page);
$main->addPage($page);

$page = new Page("ajaxPanels", _T("Panels", "dashboard"));
$page->setOptions(array("visible" => False, "AJAX" =>True));
$submod->addPage($page);

$mod->addSubmod($submod);
$MMCApp->addModule($mod);

# hide status submod in base module
$status = &$base->getSubmod('status');
$status->setVisibility(False);

?>
