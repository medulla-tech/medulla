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
 * services module declaration
 */

$mod = new Module("services");
$mod->setVersion("3.0.90");
$mod->setRevision('');
$mod->setDescription(_T("Services", "services"));
$mod->setAPIVersion("0:0:0");

$submod = new SubModule("control", _T("Services", "services"));
$submod->setDefaultPage("services/control/index");
$submod->setImg('img/navbar/load');
$submod->setPriority(20000);

/* Add the page to the module */
$page = new Page("index", _T("Core services", "services"));
$submod->addPage($page);

$page = new Page("ajaxServicesFilter", _T("Core services", "services"));
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("others", _T("Others services", "services"));
$submod->addPage($page);

$page = new Page("action");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("start");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("stop");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("restart");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("reload");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("status");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("log", _T("Services log"));
$page->setOptions(array("visible" => True));
$submod->addPage($page);

$page = new Page("ajaxLogFilter");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$page = new Page("ajaxOthersServicesFilter");
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

# hide log submod in base module
$base = &$MMCApp->getModule('base');
$logview = &$base->getSubmod('logview');
if ($logview)
    $logview->setVisibility(False);

?>
