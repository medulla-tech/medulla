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
require_once("modules/medulla_server/version.php");

$mod = new Module("medulla_server");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Medulla", "medulla"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(700);


/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

$page = new Page("computers_list", _T("Computers list", "medulla"));
$page->setOptions(array("visible"=>False));
$page->setFile("modules/medulla_server/medulla_server/computers_list.php");
$submod->addPage($page);

$page = new Page("select_location", _T("Location selection in computer edit", "medulla"));
$page->setOptions(array("visible"=>False));
$page->setFile("modules/medulla_server/includes/select_location.php");
$submod->addPage($page);

unset($submod);

// Module update
$submod = new SubModule("update");
$submod->setImg('modules/xmppmaster/img/navbar/xmppmaster');
$submod->setDescription(_T("update", "medulla"));
$submod->setVisibility(False);
// $submod->setDefaultPage("xmppmaster/update/viewProductUpdates.php");



$page = new Page("viewProductUpdates", _T("viewProductUpdates", "medulla"));
$page->setFile("modules/medulla_server/update/viewProductUpdates.php");
 $page->setOptions(array("visible" => False, "noHeader" => True));
//$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("installProductUpdates",_T('install Product Updates', 'medulla'));
$page->setFile("modules/medulla_server/update/installProductUpdates.php");
// $page->setOptions(array("visible" => True, "noHeader" => False));
$submod->addPage($page);


$page = new Page("ajaxInstallProductUpdates", _T("Product Updates installation (ajax)", "update"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);



$mod->addSubmod($submod);


$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);


?>
