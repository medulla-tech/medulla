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
 * monitoring module declaration
 */

require_once("modules/pulse2/version.php");

$mod = new Module("monitoring");
$mod->setDescription(_T("monitoring service", "monitoring"));
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setAPIVersion("4:1:3");

$submod = new SubModule("monitoring");
$submod->setDescription(_T("Monitoring", "monitoring"));
$submod->setImg("modules/monitoring/graph/imaging");
$submod->setDefaultPage("monitoring/monitoring/index");
$submod->setPriority(900);

$page = new Page("index", _T('dashboard', 'monitoring'));
$submod->addPage($page);

$page = new Page("viewgraphics", _T('graphics', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/viewgraphics.php");
$submod->addPage($page);

$page = new Page("editconfiguration", _T('configuration', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/editconfiguration.php");
$submod->addPage($page);

$page = new Page("mediaManager", _T('manage media', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/mediaManager.php");
$submod->addPage($page);

$page = new Page("triggerManager", _T('manage trigger', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/triggerManager.php");
$submod->addPage($page);

$page = new Page("deleteTrigger", _T('delete trigger', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/deleteTrigger.php");
$submod->addPage($page);

$page = new Page("modifTrigger", _T('modify trigger', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/modifTrigger.php");
$submod->addPage($page);

$page = new Page("addSnmp", _T('add snmp device', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/addSnmp.php");
$submod->addPage($page);

$page = new Page("deleteSnmp", _T('delete snmp device', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/deleteSnmp.php");
$submod->addPage($page);

$page = new Page("editSnmp", _T('edit snmp device', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/editSnmp.php");
$submod->addPage($page);

$page = new Page("ackalert", _T('ack', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/ackalert.php");
$submod->addPage($page);

$page = new Page("discovery", _T('discovery', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/discovery.php");
$submod->addPage($page);

$page = new Page("history", _T('history', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/history.php");
$submod->addPage($page);

$page = new Page("hostStatus", _T('host status', 'monitoring'));
$page->setFile("modules/monitoring/monitoring/hostStatus.php");
$submod->addPage($page);




// AJAX pages
$page = new Page('ajaxMonitoringIndex');
$page->setFile("modules/monitoring/monitoring/ajaxMonitoringIndex.php");
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$page = new Page('ajaxMonitoringAlert');
$page->setFile("modules/monitoring/monitoring/ajaxMonitoringAlert.php", array("visible"=> False, "AJAX" => True));
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$page = new Page('ajaxGraph');
$page->setFile("modules/monitoring/monitoring/ajaxGraph.php");
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$page = new Page('ajaxDiscoveryDevices');
$page->setFile("modules/monitoring/monitoring/ajaxDiscoveryDevices.php");
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$page = new Page('ajaxHistory');
$page->setFile("modules/monitoring/monitoring/ajaxHistory.php");
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$page = new Page('ajaxMediatype');
$page->setFile("modules/monitoring/monitoring/ajaxMediatype.php");
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$page = new Page('ajaxTrigger');
$page->setFile("modules/monitoring/monitoring/ajaxTrigger.php");
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$page = new Page('ajaxSnmp');
$page->setFile("modules/monitoring/monitoring/ajaxSnmp.php");
$page->setOptions(array("visible"=> False, "AJAX" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);



?>
