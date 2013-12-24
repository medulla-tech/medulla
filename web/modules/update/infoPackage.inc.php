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
$MMCApp = & MMCApp::getInstance();

$mod = new Module("update");
$mod->setVersion("1.0.0");
$mod->setRevision('');
$mod->setDescription(_T("Update manager", "update"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(990);

$submod = new SubModule("update", _T("Update manager", "update"));
$submod->setDefaultPage("update/update/index");
$submod->setImg('modules/update/graph/navbar/update');
$submod->setPriority(990);

$page = new Page("index", _T("Update manager", "update"));
$submod->addPage($page);

$page = new Page("viewUpdates", _T("View updates", "update"));
$submod->addPage($page);

$page = new Page("ajaxUpdates", _T("Update managment", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("enableUpdate", _T("Enable update", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("disableUpdate", _T("Disable update", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp->addModule($mod);
?>
