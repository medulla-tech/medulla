<?php

/**
 * (c) 2023 Siveo, http://siveo.net
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

require_once("modules/medulla_server/version.php");

$mod = new Module("greenit");
$mod->setVersion("1.0");
//$mod->setRevision('');
$mod->setDescription(_T("Greenit", "greenit"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("greenit");
$submod->setDescription(_T("Greenit", "greenit"));
$submod->setVisibility(True);
$submod->setImg('modules/greenit/graph/navbar/greenit');
$submod->setDefaultPage("greenit/greenit/index");
$submod->setPriority(1000);

$page = new Page("index", _T('Page de tests', 'greenit'));
$page->setFile("modules/greenit/greenit/index.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>

