<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/medulla_server/version.php");

$mod = new Module("security");
$mod->setVersion("1.0");
$mod->setDescription(_T("Security", "security"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("security");
$submod->setDescription(_T("Security", "security"));
$submod->setVisibility(True);
$submod->setImg('modules/security/graph/navbar/security');
$submod->setDefaultPage("security/security/index");
$submod->setPriority(500);

// CVE Summary page (index)
$page = new Page("index", _T('CVE Summary', 'security'));
$page->setFile("modules/security/security/index.php");
$submod->addPage($page);

// Ajax CVE List
$page = new Page("ajaxCVEList", _T('CVE List', 'security'));
$page->setFile("modules/security/security/ajaxCVEList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// All CVEs page (flat list)
$page = new Page("allcves", _T('All CVEs', 'security'));
$page->setFile("modules/security/security/allcves.php");
$submod->addPage($page);

// Results by Software page (hidden, replaced by index)
$page = new Page("softwares", _T('Results by Software', 'security'));
$page->setFile("modules/security/security/softwares.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Ajax Softwares List
$page = new Page("ajaxSoftwaresList", _T('Softwares List', 'security'));
$page->setFile("modules/security/security/ajaxSoftwaresList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Software Detail page
$page = new Page("softwareDetail", _T('Software Vulnerabilities', 'security'));
$page->setFile("modules/security/security/softwareDetail.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Ajax Software CVE List
$page = new Page("ajaxSoftwareCVEList", _T('Software CVE List', 'security'));
$page->setFile("modules/security/security/ajaxSoftwareCVEList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Results by Machine page
$page = new Page("machines", _T('Results by Machine', 'security'));
$page->setFile("modules/security/security/machines.php");
$submod->addPage($page);

// Ajax Machines List
$page = new Page("ajaxMachinesList", _T('Machines List', 'security'));
$page->setFile("modules/security/security/ajaxMachinesList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Machine Detail page
$page = new Page("machineDetail", _T('Machine Vulnerabilities', 'security'));
$page->setFile("modules/security/security/machineDetail.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Ajax Machine CVE List
$page = new Page("ajaxMachineCVEList", _T('Machine CVE List', 'security'));
$page->setFile("modules/security/security/ajaxMachineCVEList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Ajax Machine Softwares List (grouped view)
$page = new Page("ajaxMachineSoftwaresList", _T('Machine Softwares List', 'security'));
$page->setFile("modules/security/security/ajaxMachineSoftwaresList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// CVE Detail page
$page = new Page("cveDetail", _T('CVE Details', 'security'));
$page->setFile("modules/security/security/cveDetail.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Results by Entity page
$page = new Page("entities", _T('Results by Entity', 'security'));
$page->setFile("modules/security/security/entities.php");
$submod->addPage($page);

// Ajax Entities List
$page = new Page("ajaxEntitiesList", _T('Entities List', 'security'));
$page->setFile("modules/security/security/ajaxEntitiesList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Results by Group page
$page = new Page("groups", _T('Results by Group', 'security'));
$page->setFile("modules/security/security/groups.php");
$submod->addPage($page);

// Ajax Groups List
$page = new Page("ajaxGroupsList", _T('Groups List', 'security'));
$page->setFile("modules/security/security/ajaxGroupsList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Group Detail page
$page = new Page("groupDetail", _T('Group Vulnerabilities', 'security'));
$page->setFile("modules/security/security/groupDetail.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Ajax Group Machines List
$page = new Page("ajaxGroupMachinesList", _T('Group Machines List', 'security'));
$page->setFile("modules/security/security/ajaxGroupMachinesList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Start Scan action
$page = new Page("startScan", _T('Start Scan', 'security'));
$page->setFile("modules/security/security/startScan.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Ajax Start Scan popup
$page = new Page("ajaxStartScan", _T('Start Scan', 'security'));
$page->setFile("modules/security/security/ajaxStartScan.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Ajax Start Scan Entity popup
$page = new Page("ajaxStartScanEntity", _T('Scan Entity', 'security'));
$page->setFile("modules/security/security/ajaxStartScanEntity.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Ajax Start Scan Group popup
$page = new Page("ajaxStartScanGroup", _T('Scan Group', 'security'));
$page->setFile("modules/security/security/ajaxStartScanGroup.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Ajax Scan Machine popup
$page = new Page("ajaxScanMachine", _T('Scan Machine', 'security'));
$page->setFile("modules/security/security/ajaxScanMachine.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Ajax Dashboard Summary (for entity filter update)
$page = new Page("ajaxDashboardSummary", _T('Dashboard Summary', 'security'));
$page->setFile("modules/security/security/ajaxDashboardSummary.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Ajax Create Group from Severity popup
$page = new Page("ajaxCreateGroupFromSeverity", _T('Create Group from Severity', 'security'));
$page->setFile("modules/security/security/ajaxCreateGroupFromSeverity.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

$mod->addSubmod($submod);
$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);
?>
