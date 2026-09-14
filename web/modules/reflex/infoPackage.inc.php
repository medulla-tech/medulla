<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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

$mod = new Module("reflex");
$mod->setVersion("1.0");
$mod->setDescription(_T("Reflex", "reflex"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2100);

$submod = new SubModule("reflex");
$submod->setDescription(_T("Reflex", "reflex"));
$submod->setVisibility(True);
$submod->setImg('modules/reflex/graph/navbar/reflex');
$submod->setDefaultPage("reflex/reflex/index");
$submod->setPriority(500);

// Popups and endpoints that write are not flagged AJAX: that flag also drops
// the ACL check.

// Dashboard (index)
$page = new Page("index", _T('Dashboard', 'reflex'));
$page->setFile("modules/reflex/reflex/index.php");
$submod->addPage($page);

// Probes list
$page = new Page("probes", _T('Probes', 'reflex'));
$page->setFile("modules/reflex/reflex/probes.php");
$submod->addPage($page);

// Ajax Probes List
$page = new Page("ajaxProbesList", _T('Probes List', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxProbesList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Probe detail
$page = new Page("probeDetail", _T('Probe Details', 'reflex'));
$page->setFile("modules/reflex/reflex/probeDetail.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Settings of one entity, redrawn when the probe sheet changes entity.
$page = new Page("ajaxProbeEntitySetting", _T('Settings Per Entity', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxProbeEntitySetting.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Probe creation and modification
$page = new Page("probeEdit", _T('Edit Probe', 'reflex'));
$page->setFile("modules/reflex/reflex/probeEdit.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Adapt one alert condition of a probe, shipped ones included.
$page = new Page("ajaxEditCondition", _T('Adapt Alert Condition', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxEditCondition.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Delete probe popup.
$page = new Page("ajaxDeleteProbe", _T('Delete Probe', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxDeleteProbe.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Duplicate probe popup.
$page = new Page("ajaxDuplicateProbe", _T('Duplicate Probe', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxDuplicateProbe.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Probe visibility popup.
$page = new Page("ajaxSetVisibility", _T('Change visibility', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxSetVisibility.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Assign probe popup.
$page = new Page("ajaxAssignProbe", _T('Assign Probe', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxAssignProbe.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Ajax Machine Search, feeding the target field of the assignment popup
$page = new Page("ajaxSearchMachines", _T('Search Machines', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxSearchMachines.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Cadence change of an assignment popup.
$page = new Page("ajaxEditAssignmentInterval", _T('Change the cadence', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxEditAssignmentInterval.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Unassign probe popup.
$page = new Page("ajaxUnassignProbe", _T('Unassign Probe', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxUnassignProbe.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Bulk assignment removal, called by the selection bar of the assignment table.
$page = new Page("ajaxUnassignProbesBulk", _T('Remove Selected Assignments', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxUnassignProbesBulk.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Exclude probe on machine popup.
$page = new Page("ajaxExcludeProbe", _T('Remove Probe From This Machine', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxExcludeProbe.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Include probe back on machine popup.
$page = new Page("ajaxIncludeProbe", _T('Put Probe Back On This Machine', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxIncludeProbe.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Open alerts page
$page = new Page("alerts", _T('Alerts', 'reflex'));
$page->setFile("modules/reflex/reflex/alerts.php");
$submod->addPage($page);

// Ajax Alerts List
$page = new Page("ajaxAlertsList", _T('Alerts List', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxAlertsList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Alert detail popup, opened by the magnifier of the three alert lists.
$page = new Page("ajaxAlertDetail", _T('Alert detail', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxAlertDetail.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Alerts history page
$page = new Page("alertsHistory", _T('Alerts History', 'reflex'));
$page->setFile("modules/reflex/reflex/alertsHistory.php");
$submod->addPage($page);

// Ajax Alerts History List
$page = new Page("ajaxAlertsHistory", _T('Alerts History List', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxAlertsHistory.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Acknowledge alert popup.
$page = new Page("ajaxAckAlert", _T('Acknowledge Alert', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxAckAlert.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Bulk alert acknowledgement, called by the selection bar of the alerts list.
$page = new Page("ajaxAckAlertsBulk", _T('Acknowledge Selected Alerts', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxAckAlertsBulk.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Machines status page
$page = new Page("machines", _T('Machines', 'reflex'));
$page->setFile("modules/reflex/reflex/machines.php");
$submod->addPage($page);

// Ajax Machines List
$page = new Page("ajaxMachinesList", _T('Machines List', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxMachinesList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Machine detail page
$page = new Page("machineDetail", _T('Machine Supervision', 'reflex'));
$page->setFile("modules/reflex/reflex/machineDetail.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Ajax Probe Chart, one time series per probe.
$page = new Page("ajaxProbeChart", _T('Probe Chart', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxProbeChart.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Ajax Channels List
$page = new Page("ajaxChannelsList", _T('Channels List', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxChannelsList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Channel creation and modification
$page = new Page("channelEdit", _T('Edit Channel', 'reflex'));
$page->setFile("modules/reflex/reflex/channelEdit.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Delete channel popup.
$page = new Page("ajaxDeleteChannel", _T('Delete Channel', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxDeleteChannel.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Test channel popup: confirming sends a message through the channel.
$page = new Page("ajaxTestChannel", _T('Test Channel', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxTestChannel.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Ajax Notification Rules List
$page = new Page("ajaxRulesList", _T('Notification Rules', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxRulesList.php");
$page->setOptions(array("visible" => False, "noHeader" => True, "AJAX" => True));
$submod->addPage($page);

// Notification rule creation and modification
$page = new Page("ruleEdit", _T('Edit Notification Rule', 'reflex'));
$page->setFile("modules/reflex/reflex/ruleEdit.php");
$page->setOptions(array("visible" => False));
$submod->addPage($page);

// Delete notification rule popup.
$page = new Page("ajaxDeleteRule", _T('Delete Notification Rule', 'reflex'));
$page->setFile("modules/reflex/reflex/ajaxDeleteRule.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

// Settings page
$page = new Page("settings", _T('Settings', 'reflex'));
$page->setFile("modules/reflex/reflex/settings.php");
$submod->addPage($page);

$mod->addSubmod($submod);
$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);
?>
