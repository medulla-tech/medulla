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
 * report module declaration
 */

$MMCApp =& MMCApp::getInstance();

$mod = new Module("report");
$mod->setVersion("3.1.1");
$mod->setRevision('');
$mod->setDescription(_T("Reporting", "report"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(990);

$submod = new SubModule("report", _T("Report", "report"));
$submod->setDefaultPage("report/report/index");
$submod->setImg('modules/report/graph/navbar/report');
$submod->setPriority(990);

$page = new Page("index", _T("Report creation", "report"));
$submod->addPage($page);

$page = new Page("get_file", _T("Download a file from report module (report or PNG)", "report"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp->addModule($mod);

?>
