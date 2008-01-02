<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */


/**
 * module declaration
 */

$mod = new Module("msc");
$mod->setVersion("2.0.0");
$mod->setRevision("$Rev$");
$mod->setDescription(_T("Secure Control", "msc"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(700);


$submod = new SubModule("msc");
$submod->setDescription(_T("MSC", "msc"));
$submod->setImg('modules/msc/graph/img/msc');
$submod->setDefaultPage("msc/msc/repository");

$page = new Page("repository",_T("Repository","msc"));
$submod->addPage($page);

$page = new Page("download",_T("Download", "msc"));
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);
$page = new Page("edit",_T("Edit","msc"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);


/* put in base/computer */

/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

$page = new Page("mscdetails", _T("General", "msc"));
$page->setOptions(array("visible"=>False));
$page->setFile("modules/msc/msc/mscdetails.php");
$submod->addPage($page);

$page = new Page("msctabs", _T("Secure Control on machine"));
$page->setFile("modules/msc/msc/tabs.php");
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("msctabsplay");
$page->setFile("modules/msc/msc/msctabsplay.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("msctabspause");
$page->setFile("modules/msc/msc/msctabspause.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("msctabsstop");
$page->setFile("modules/msc/msc/msctabsstop.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("package_detail");
$page->setFile("modules/msc/msc/package_detail.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("start_tele_diff");
$page->setFile("modules/msc/msc/start_tele_diff.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("tablogs");
$page->setFile("modules/msc/msc/logs.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("tablaunch");
$page->setFile("modules/msc/msc/launch.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("packages",_T("Packages","msc"));
$page->setFile("modules/msc/msc/packages.php");
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

unset($submod);


?>
