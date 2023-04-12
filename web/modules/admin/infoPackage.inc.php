<?php
/**
 * (c) 2020-2021 Siveo, http://siveo.net
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
require_once("modules/pulse2/version.php");

$mod = new Module("admin");
$mod->setVersion("5.0.0");
//$mod->setRevision('');
$mod->setDescription(_T("Admin", "admin"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("admin");
$submod->setDescription(_T("Admin", "admin"));
$submod->setVisibility(True);
$submod->setImg('modules/admin/graph/navbar/admin');
$submod->setDefaultPage("admin/admin/relaysList");
$submod->setPriority(1001);

$page = new Page("relaysList", _T("Relays List", "glpi"));
$page->setFile("modules/admin/admin/relaysList.php");
$submod->addPage($page);

$page = new Page("ajaxRelaysList", _T("Relays List", "glpi"));
$page->setFile("modules/admin/admin/ajaxRelaysList.php");
$page->setOptions(array("AJAX"=>true, "visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("packageslist", _T("Packages List", "xmppmaster"));
$page->setFile("modules/admin/admin/packageslist.php");
$submod->addPage($page);

$page = new Page("ajaxpackageslist", _T("Packages List", "xmppmaster"));
$page->setFile("modules/admin/admin/ajaxpackageslist.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("reconfiguremachines",_T("Reconfigure Machines","xmppmaster"));
$page->setFile("modules/admin/admin/reconfiguremachines.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("switchrelay",_T("Switch Relay","xmppmaster"));
$page->setFile("modules/admin/admin/switchrelay.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("conffile", _("Edit config files"));
$page->setFile("modules/admin/admin/configfile.php");
$submod->addPage($page);

// Popup qa on relays list
$page = new Page("detailactions", _T("Launch Quick Action on Relays", "admin"));
$page->setFile("modules/admin/admin/detailactions.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("qalaunched", _T("Qa launched on Relays", "xmppmaster"));
$page->setFile("modules/admin/admin/qalaunched.php");
$submod->addPage($page);

// List of qa launched on relay
$page = new Page("ajaxqalaunched", _T("Qa launched on Relays", "xmppmaster"));
$page->setFile("modules/admin/admin/ajaxqalaunched.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

// Result of the qa launched on relay
$page = new Page("qaresult", _T("Qa result on Relays", "xmppmaster"));
$page->setFile("modules/admin/admin/qaresult.php");
$submod->addPage($page);


//Tab pages
$page = new Page("rules_tabs", _T("Relay Rules", "admin"));
$page->setFile("modules/admin/admin/rules_tabs.php");
$page->setOptions(array("visible" => true));

//Tab1
$tab = new Tab("relayRules", _T("Relay Rules", "admin"));
$page->addTab($tab);

//Tab2
$tab = new Tab("newRelayRule", _T("New Relay Rule", "admin"));
$page->addTab($tab);
$submod->addPage($page);

$page = new Page("newRelayRule", _T("New Relay Rule", "admin"));
$page->setFile("modules/admin/admin/ajaxRelayRules.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("ajaxRelayRules", _T("Relay Rules", "admin"));
$page->setFile("modules/admin/admin/ajaxRelayRules.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("rules", _T("Rules List", "admin"));
$page->setFile("modules/admin/admin/rules.php");
$submod->addPage($page);

$page = new Page("ajaxRules", _T("Rules", "admin"));
$page->setFile("modules/admin/admin/ajaxRules.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("rulesDetail", _T("Rules Detail", "admin"));
$page->setFile("modules/admin/admin/rulesDetail.php");
$submod->addPage($page);

$page = new Page("ajaxRulesDetail", _T("Rules Detail", "admin"));
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("moveRule", _T("Move Rule", "admin"));
$page->setFile("modules/admin/admin/moveRule.php");
$submod->addPage($page);

$page = new Page("clustersList", _T('Clusters List', 'admin'));
$page->setFile("modules/admin/admin/clustersList.php");
$submod->addPage($page);

$page = new Page("ajaxClustersList", _T("Clusters List", "admin"));
$page->setFile("modules/admin/admin/ajaxClustersList.php");
$page->setOptions(array("visible"=>False, "AJAX"=>True));
$submod->addPage($page);

$page = new Page("editCluster", _T("Edit Cluster", "admin"));
$page->setFile("modules/admin/admin/editCluster.php");
$submod->addPage($page);

$page = new Page("newCluster", _T("New Cluster", "admin"));
$page->setFile("modules/admin/admin/newCluster.php");
$submod->addPage($page);

$page = new Page("deleteRelayRule", _T("Delete Relay Rules", "admin"));
$page->setFile("modules/admin/admin/deleteRelayRule.php");
$submod->addPage($page);

$page = new Page("editRelayRule", _T("Edit Relay Rule", "admin"));
$page->setFile("modules/admin/admin/editRelayRule.php");
$submod->addPage($page);

$page = new Page("moveRelayRule", _T("Move Relay Rule", "admin"));
$page->setFile("modules/admin/admin/moveRelayRule.php");
$submod->addPage($page);

$page = new Page("ban", _T("Ban Machines", "admin"));
$page->setFile("modules/admin/admin/ban.php");
$page->setOptions(array("AJAX" => false, "noHeader"=>true));
$submod->addPage($page);

$page = new Page("ajaxban", _T("Ban Machines", "admin"));
$page->setFile("modules/admin/admin/ajaxban.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("unban", _T("Unban Machines", "admin"));
$page->setFile("modules/admin/admin/unban.php");
$page->setOptions(array("AJAX" => false, "noHeader" => True));
$submod->addPage($page);

$page = new Page("ajaxunban", _T("Unban Machines", "admin"));
$page->setFile("modules/admin/admin/ajaxunban.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);


$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
