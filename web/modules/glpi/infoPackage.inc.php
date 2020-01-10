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

require_once("modules/pulse2/version.php");

$MMCApp =& MMCApp::getInstance();

$mod = new Module("glpi");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("GLPI Inventory", "glpi"));
$mod->setAPIVersion("0:0:0");

// Create a glpi submodule only for Glpi Dashboard ACL
// (Antivirus, Inventory, WinXP -> 7 migration,...)
$submod = new SubModule("glpi");
$submod->setDescription(_T("Glpi", "glpi"));

// BTW, hide this submodule from Web UI
$submod->setVisibility(False);

$page = new Page('glpi_dashboard', _T('Glpi Dashboard', 'glpi'));
$submod->addPage($page);
$mod->addSubmod($submod);

// Set the rights for glpi/includes/panels/antivirus.inc.php
$page = new Page('antivirus_dashboard', _T('Antivirus Panel', 'glpi'));
$submod->addPage($page);
$mod->addSubmod($submod);

// Set the rights for glpi/includes/panels/inventory.inc.php
$page = new Page('inventory_dashboard', _T('Inventory Panel', 'glpi'));
$submod->addPage($page);
$mod->addSubmod($submod);

// Set the rights for glpi/includes/panels/os_repartition.inc.php
$page = new Page('os_repartition_dashboard', _T('Os Repartition Panel', 'glpi'));
$submod->addPage($page);
$mod->addSubmod($submod);

$MMCApp->addModule($mod);

/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

$page = new Page("machinesList", _T("Get the whole machines list", "glpi"));
$page->setFile("modules/glpi/glpi/machinesList.php");
$submod->addPage($page);

$page = new Page("ajaxMachinesList", _T("Machines List", "glpi"));
$page->setFile("modules/glpi/glpi/ajaxMachinesList.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("createStaticGroup", _T("Create static group from dashboard widgets (GLPI)", "glpi"));
$page->setFile("modules/glpi/glpi/createStaticGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("createAntivirusStaticGroup", _T("Create static group from antivirus dashboard widget (GLPI)", "glpi"));
$page->setFile("modules/glpi/glpi/createAntivirusStaticGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("createOSStaticGroup", _T("Create static group from OS distribution dashboard widget (GLPI)", "glpi"));
$page->setFile("modules/glpi/glpi/createOSStaticGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("createMachinesStaticGroup", _T("Create static group from machines dashboard widget (GLPI)", "glpi"));
$page->setFile("modules/glpi/glpi/createMachinesStaticGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("createMachinesStaticGroupdeploy", _T("Create static group from machines dashboard widget (GLPI)", "glpi"));
$page->setFile("modules/glpi/glpi/createMachinesStaticGroupdeploy.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("createBackupStaticGroup", _T("Create static group from machines backup widget (GLPI)", "glpi"));
$page->setFile("modules/glpi/glpi/createBackupStaticGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("entityList", _T('Entities', 'glpi'));
$page->setFile("modules/glpi/glpi/entityList.php");
$submod->addPage($page);

$page = new Page("ajaxEntityList", _T('Entities (ajax)', 'glpi'));
$page->setFile("modules/glpi/glpi/ajaxEntityList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("addEntity", _T('Add entity', 'glpi'));
$page->setFile("modules/glpi/glpi/addEntity.php");
$submod->addPage($page);

$page = new Page("locationList", _T('Locations', 'glpi'));
$page->setFile("modules/glpi/glpi/locationList.php");
$submod->addPage($page);

$page = new Page("ajaxLocationList", _T('Entities (ajax)', 'glpi'));
$page->setFile("modules/glpi/glpi/ajaxLocationList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("addLocation", _T('Add entity', 'glpi'));
$page->setFile("modules/glpi/glpi/addLocation.php");
$submod->addPage($page);

$page = new Page("entityRules", _T('Entity rules', 'glpi'));
$page->setFile("modules/glpi/glpi/entityRules.php");
$submod->addPage($page);

$page = new Page("ajaxEntityRules", _T('Entity rules (ajax)', 'glpi'));
$page->setFile("modules/glpi/glpi/ajaxEntityRules.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("addEntityRule", _T('Add entity rule', 'glpi'));
$page->setFile("modules/glpi/glpi/addEntityRule.php");
$submod->addPage($page);

$page = new Page("deleteEntityRule", _T("Delete entity rule", "glpi"));
$page->setFile("modules/glpi/glpi/deleteEntityRule.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("moveRuleUp", _T("Change entity rule order (up)", "glpi"));
$page->setFile("modules/glpi/glpi/moveRuleUp.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("moveRuleDown", _T("Change entity rule order (down)", "glpi"));
$page->setFile("modules/glpi/glpi/moveRuleDown.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
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

$page = new Page("ajaxSetGlpiEditableValue");
$page->setFile("modules/glpi/glpi/ajaxSetGlpiEditableValue.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);


$page = new Page("glpitabs", _T("Inventory (GLPI) on machine", "glpi"));
$page->setFile("modules/glpi/glpi/tabs.php");
$page->setOptions(array("visible"=>False));
$tab = new Tab("tab0", _T("Summary tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab1", _T("Hardware tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab2", _T("Storage tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab3", _T("Network tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab4", _T("Softwares tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab5", _T("Administrative tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab6", _T("History tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab7", _T("Antivirus tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab8", _T("Registry tab (GLPI)", 'glpi'));
$page->addTab($tab);

$tab = new Tab("tab9", _T("Connections tab (GLPI)", "glpi"));
$page->addTab($tab);

$submod->addPage($page);

$page = new Page("ajaxViewPart");
$page->setFile("modules/glpi/glpi/ajaxViewPart.php", array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

unset($submod);
/* groupes dynamiques end */
?>
