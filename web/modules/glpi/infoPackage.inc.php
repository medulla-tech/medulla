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

$MMCApp =& MMCApp::getInstance();

/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

$page = new Page("createStaticGroup", _T("Create static group from dashboard (GLPI)", "glpi"));
$page->setFile("modules/glpi/glpi/createStaticGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

/* groupes dynamiques */

$page = new Page("locations", _T('Display locations', 'glpi'));
$page->setFile("modules/glpi/glpi/locations.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxLocationSearch");
$page->setFile("modules/glpi/glpi/ajaxLocationSearch.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("groupglpitabs", _T("Inventory (GLPI) on a groups of machines", "glpi"));
$page->setFile("modules/glpi/glpi/tabs.php");
$page->setOptions(array("visible"=>False));

$tab = new Tab("tab0", _T("GLPI hardware tab", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab1", _T("GLPI network tab", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab2", _T("GLPI controller tab", 'glpi'));
$page->addTab($tab);

$submod->addPage($page);

$page = new Page("glpitabs", _T("Inventory (GLPI) on machine", "glpi"));
$page->setFile("modules/glpi/glpi/tabs.php");
$page->setOptions(array("visible"=>False));

$tab = new Tab("tab0", _T("GLPI hardware tab", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab1", _T("GLPI network tab", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab2", _T("GLPI controller tab", 'glpi'));
$page->addTab($tab);

$submod->addPage($page);


unset($submod);
/* groupes dynamiques end */
?>
