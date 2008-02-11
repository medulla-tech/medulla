<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id$
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/dyngroup/includes/includes.php");

$MMCApp =& MMCApp::getInstance();

/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

/* groupes dynamiques */

if (isDynamicEnable()) {
    $page = new Page("creator",_T("Machines Group Creator","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/tab.php");
    $submod->addPage($page);
    
    $page = new Page("edit",_T("Machines Group Editor","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/edithead.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);
} else {
    $page = new Page("creator",_T("Machines Group Creator","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
    $submod->addPage($page);
    
    $page = new Page("edit",_T("Machines Group Editor","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);
}

$page = new Page("display",_T("Display a groups of machines","dyngroup"));
$page->setFile("modules/dyngroup/dyngroup/display.php");
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("save",_T("Save a group of machines","dyngroup"));
$page->setFile("modules/dyngroup/dyngroup/save.php");
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("list",_T("List all groups of machines","dyngroup"));
$page->setFile("modules/dyngroup/dyngroup/list.php");
$submod->addPage($page);

$page = new Page("delete_group",_T("Delete a group of machines","dyngroup"));
$page->setFile("modules/dyngroup/dyngroup/delete_group.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("details",_T("Group of machines details","dyngroup"));
$page->setFile("modules/dyngroup/dyngroup/details.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("remove_machine",_T("Remove a machine from a group","dyngroup"));
$page->setFile("modules/dyngroup/dyngroup/remove_machine.php");
$page->setOptions(array("visible"=>False, "noHeader" =>True));
$submod->addPage($page);

$page = new Page("ajaxAutocompleteSearch");
$page->setFile("modules/dyngroup/dyngroup/ajaxAutocompleteSearch.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxAutocompleteSearchWhere");
$page->setFile("modules/dyngroup/dyngroup/ajaxAutocompleteSearchWhere.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

unset($submod);
/* groupes dynamiques end */
?>
