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
require_once("modules/pulse2/version.php");

$mod = new Module("inventory");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Inventory", "inventory"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(700);


$submod = new SubModule("inventory");
$submod->setDescription(_T("Inventory", "inventory"));
$submod->setImg('modules/inventory/graph/img/inventory');
$submod->setDefaultPage("inventory/inventory/incoming");

$page = new Page("incoming", _T("Incoming", "inventory"));
$submod->addPage($page);
$page = new Page("index",_T("Bios","inventory"));
$submod->addPage($page);
$page = new Page("hardware",_T("Hardware","inventory"));
$submod->addPage($page);
$page = new Page("network",_T("Network","inventory"));
$submod->addPage($page);
$page = new Page("controller",_T("Controller","inventory"));
$submod->addPage($page);

$page = new Page("drive",_T("Drive","inventory"));
$submod->addPage($page);
$page = new Page("input",_T("Input","inventory"));
$submod->addPage($page);
$page = new Page("memory",_T("Memory","inventory"));
$submod->addPage($page);
$page = new Page("monitor",_T("Monitor","inventory"));
$submod->addPage($page);
$page = new Page("port",_T("Port","inventory"));
$submod->addPage($page);
$page = new Page("printer",_T("Printer","inventory"));
$submod->addPage($page);
$page = new Page("sound",_T("Sound","inventory"));
$submod->addPage($page);
$page = new Page("storage",_T("Storage","inventory"));
$submod->addPage($page);
$page = new Page("videocard",_T("VideoCard","inventory"));
$submod->addPage($page);
$page = new Page("software",_T("Software","inventory"));
$submod->addPage($page);
$page = new Page("registry",_T("Registry","inventory"));
$submod->addPage($page);

$page = new Page("view",_T("View", "inventory"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("infos",_T("Informations", "inventory"));
$page->setFile("modules/inventory/inventory/infos.php",
               array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("graphs",_T("Charts", "inventory"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("graph",_T("Chart", "inventory"));
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("csv",_T("Csv's export", "inventory"));
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("createStaticGroup");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxFilter");
$page->setFile("modules/inventory/inventory/ajaxFilter.php", array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxViewPart");
$page->setFile("modules/inventory/inventory/ajaxViewPart.php", array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxIncoming");
$page->setFile("modules/inventory/inventory/ajaxIncoming.php", array("AJAX" =>True, "visible"=>False));
$submod->addPage($page);

$page = new Page("header", _T('Header', "inventory"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);


/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

if (!empty($submod)) {
    $page = new Page("groupinvtabs", _T("Inventory on a group of computers", "inventory"));
    $page->setFile("modules/inventory/inventory/tabs.php");
    $page->setOptions(array("visible"=>False));
    $tab = new Tab("grouptab0",  _T("Hardware tab for a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("grouptab5",  _T("Bios tab for a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("grouptab1",  _T("Software tab for a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("grouptab2",  _T("Network tab for a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("grouptab3",  _T("Controller tab for a group", "inventory"));
    $page->addTab($tab);
 
    $tab = new Tab("grouptab4",  _T("Registry tab for a group", "inventory"));
    $page->addTab($tab);

    $tab = new Tab("tab0",  _T("Hardware tab for a computer in a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("tab5",  _T("Bios tab for a computer in a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("tab1",  _T("Software tab for a computer in a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("tab2",  _T("Network tab for a computer in a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("tab3",  _T("Controller tab for a computer in a group", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("tab4",  _T("Registry tab for a computer in a group", "inventory"));
    $page->addTab($tab);
   
    $submod->addPage($page);
 
    $page = new Page("invtabs", _T("Inventory on a single computer", "inventory"));
    $page->setFile("modules/inventory/inventory/tabs.php");
    $page->setOptions(array("visible"=>False));

    $tab = new Tab("tab0",  _T("Hardware tab for a computer", "inventory"));
    $page->addTab($tab);

    $tab = new Tab("tab1",  _T("Software tab for a computer", "inventory"));
    $page->addTab($tab);

    $tab = new Tab("tab2",  _T("Network tab for a computer", "inventory"));
    $page->addTab($tab);

    $tab = new Tab("tab3",  _T("Controller tab for a computer", "inventory"));
    $page->addTab($tab);
    
    $tab = new Tab("tab4",  _T("Registry tab for a computer", "inventory"));
    $page->addTab($tab);

    $submod->addPage($page);

    $page = new Page("invdiff", _T("Differences between two inventories", "inventory"));
    $page->setFile("modules/inventory/inventory/inventory_diff.php");
    $page->setOptions(array("visible"=>False));

    $submod->addPage($page);
    
    unset($submod);
}

?>
