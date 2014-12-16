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
 * update module declaration
 */
require_once("modules/pulse2/version.php");

$MMCApp = & MMCApp::getInstance();

$mod = new Module("update");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Update manager", "update"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(990);

$submod = new SubModule("update", _T("Updates", "update"));
$submod->setDefaultPage("update/update/index");
$submod->setImg('modules/update/graph/navbar/update');
$submod->setPriority(990);

$page = new Page("index", _T("All updates", "update"));
$submod->addPage($page);

$page = new Page("viewUpdates", _T("Updates", "update"));
$submod->addPage($page);

$page = new Page("ajaxUpdates", _T("Updates list", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("enableUpdate", _T("Enable update", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("disableUpdate", _T("Disable update", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("settings", _T("Settings", "update"));
$submod->addPage($page);

//$mod->addSubmod($submod);

/*$submod = new SubModule("product_updates", _T("Product updates", "update"));
//$submod->setDefaultPage("update/product_updates/installProductUpdates");
$submod->setImg('modules/update/graph/navbar/update');
$submod->setPriority(990);*/

$page = new Page("installProductUpdates", _T("Product Updates installation", "update"));
$page->setOptions(array("visible" => True, "noHeader" => False));
$submod->addPage($page);

$page = new Page("viewProductUpdates", _T("Product Updates list", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);



$page = new Page("ajaxInstallProductUpdates", _T("Product Updates installation (ajax)", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp->addModule($mod);

/* Add update for Group pages */
$base = &$MMCApp->getModule('base');
$submod = & $base->getSubmod('computers');
$page = new Page("view_updates", _T("Updates", "update"));
$page->setFile("modules/update/update/viewGroupUpdates.php");
$page->setOptions(array("visible"=>False));
$submod->addPage($page);
?>
