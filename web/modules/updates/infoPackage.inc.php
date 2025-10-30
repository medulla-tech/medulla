<?php
/**
 * (c) 2022-2025 Siveo, http://siveo.net/
 *
 * $Id$
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

$mod = new Module("updates");
$mod->setVersion("1.0");
$mod->setDescription(_T("Updates", "updates"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("updates");
$submod->setDescription(_T("Updates", "updates"));
$submod->setVisibility(true);
$submod->setImg('modules/updates/graph/navbar/updates');
$submod->setDefaultPage("updates/updates/index");
$submod->setPriority(500);

$page = new Page("index", _T('Entities Compliance', 'updates'));
$submod->addPage($page);

$page = new Page("ajaxEntitiesList", _T("Entities Compliance", "updates"));
$page->setFile("modules/updates/updates/ajaxEntitiesList.php");
$page->setOptions(array("AJAX" => true, "visible" => false, "noHeader" => true));
$submod->addPage($page);


$page = new Page("detailsByMachines", _T('Details by Machines', 'updates'));
$page->setFile("modules/updates/updates/detailsByMachines.php");
$submod->addPage($page);

$page = new Page("ajaxDetailsByMachines", _T("Details by Machines", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsByMachines.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("deployAllUpdates", _T('Deploy all Updates', 'updates'));
$page->setFile("modules/updates/updates/deployAllUpdates.php");
$submod->addPage($page);

$page = new Page("ajaxDeployAllUpdates", _T("Deploy all Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxDeployAllUpdates.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("deployUpdate", _T('Deploy Specific Updates On Entity', 'updates'));
$page->setFile("modules/updates/updates/deployUpdate.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);


$page = new Page("deploySpecificUpdate", _T('Deploy specific update', 'updates'));
$page->setFile("modules/updates/updates/deploySpecificUpdate.php");
$submod->addPage($page);

$page = new Page("detailsByUpdates", _T('List updates', 'updates'));
$page->setFile("modules/updates/updates/detailsByUpdates.php");
$submod->addPage($page);

$page = new Page("hardwareConstraintsForMajorUpdates", _T('do not perform the update for now, as long as certain essential hardware constraints are not met', 'updates'));
$page->setFile("modules/updates/updates/hardwareConstraintsForMajorUpdates.php");
$submod->addPage($page);

$page = new Page("detailsSpecificUpdate", _T('Machine details for specific update', 'updates'));
$page->setFile("modules/updates/updates/detailsSpecificUpdate.php");
$submod->addPage($page);

$page = new Page("ajaxDetailsSpecificUpdate", _T("Manage machine details for specific update", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsSpecificUpdate.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);


$page = new Page("AjaxcreateGrouplistglpiid", 'create Group List');
$page->setFile("modules/updates/updates/AjaxcreateGrouplistglpiid.php");
$page->setOptions(array("AJAX" => True, "visible" => False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxDetailsSpecificUpdateWithout", _T("Manage machine details for specific update", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsSpecificUpdateWithout.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxDeploySpecificUpdate", _T("Manage deploy specific update", "updates"));
$page->setFile("modules/updates/updates/ajaxDeploySpecificUpdate.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxDetailsByUpdates", _T("List Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsByUpdates.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxDetailsByUpdatesGray", _T("Manage Gray List Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsByUpdatesGray.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxDetailsByUpdatesWhite", _T("Manage White List Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsByUpdatesWhite.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("MajorEntitiesList", _T('os updates', 'updates'));
$page->setFile("modules/updates/updates/MajorEntitiesList.php");
$submod->addPage($page);

$page = new Page("updatesListWin", _T('Manage Updates Lists', 'updates'));
$page->setFile("modules/updates/updates/updatesListWin.php");
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWin", _T("Manage Updates Lists for entity", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWin.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxEntityCompliance", _T("Entity Compliance", "updates"));
$page->setFile("modules/updates/updates/ajaxEntityCompliance.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWinWhite", _T("Manage Updates Lists", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWinWhite.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWinGray", _T("Manage Updates Lists", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWinGray.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWinBlack", _T("Manage Updates Lists", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWinBlack.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("enableUpdate", _T('Enable for manual update', 'updates'));
$page->setFile("modules/updates/updates/enableUpdate.php");
$submod->addPage($page);

$page = new Page("disableUpdate", _T('Disable for manual update', 'updates'));
$page->setFile("modules/updates/updates/disableUpdate.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("whitelistUpdate", _T('Approve for automatic update', 'updates'));
$page->setFile("modules/updates/updates/whitelistUpdate.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("blacklistUpdate", _T('Ban update', 'updates'));
$page->setFile("modules/updates/updates/blacklistUpdate.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("greylistUpdate", _T('Unlist update', 'updates'));
$page->setFile("modules/updates/updates/greylistUpdate.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("deleteRule", _T('UnBan update', 'updates'));
$page->setFile("modules/updates/updates/deleteRule.php");
$submod->addPage($page);

$page = new Page("grayEnable", _T('Gray Enable', 'updates'));
$page->setFile("modules/updates/updates/grayEnable.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("grayDisable", _T('Grey Disable', 'updates'));
$page->setFile("modules/updates/updates/grayDisable.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("grayApprove", _T('Grey Approve', 'updates'));
$page->setFile("modules/updates/updates/grayApprove.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

// Also used for whitelist
$page = new Page("banUpdate", _T('Ban update', 'updates'));
$page->setFile("modules/updates/updates/banUpdate.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("whiteUnlist", _T('White Unlist', 'updates'));
$page->setFile("modules/updates/updates/whiteUnlist.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);


$page = new Page("blackUnban", _T('Black Unban', 'updates'));
$page->setFile("modules/updates/updates/blackUnban.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("pendingUpdateByMachine", _T('Pending Updates', 'updates'));
$submod->addPage($page);

$page = new Page("ajaxPendingUpdateByMachine", _T('Pending Updates', 'updates'));
$page->setFile("modules/updates/updates/ajaxPendingUpdateByMachine.php", array("noHeader" => true,"visible" => false, "AJAX" => true));
$submod->addPage($page);

$page = new Page("auditUpdateByMachine", _T('Updates History', 'updates'));
$submod->addPage($page);

$page = new Page("ajaxAuditUpdateByMachine", _T('Updates History', 'updates'));
$page->setFile("modules/updates/updates/ajaxAuditUpdateByMachine.php", array("noHeader" => true,"visible" => false, "AJAX" => true));
$submod->addPage($page);

$page = new Page("cancelUpdate", _T('Cancel Update', 'updates'));
$page->setFile("modules/updates/updates/cancelUpdate.php", array("noHeader" => true,"visible" => false, "AJAX" => true));
$submod->addPage($page);

// Major update
/*
$page = new Page("ajaxMajorEntitiesList", _T("Entities Major Compliance", "updates"));
$page->setFile("modules/updates/updates/ajaxMajorEntitiesList.php");
$page->setOptions(array("AJAX" => true, "visible" => false, "noHeader" => true));
$submod->addPage($page);*/




$page = new Page("ajaxMajorEntitiesList", _T('Entities Major Compliance', 'updates'));
$page->setFile("modules/updates/updates/ajaxMajorEntitiesList.php");
$submod->addPage($page);


/*

$page = new Page("ajaxMajorEntitiesList", _T("Entities Major Compliance", "updates"));
$page->setFile("modules/updates/updates/ajaxMajorEntitiesList.php");
$submod->addPage($page);*/
/*
$page = new Page("ajaxMajorListEntity", _T('Major Compliance entity', 'updates'));
$page->setFile("modules/updates/updates/ajaxMajorListEntity.php");
$submod->addPage($page);*/

$page = new Page("updatesListMajorWin", _T('Manage Major Updates Lists', 'updates'));
$page->setFile("modules/updates/updates/updatesListMajorWin.php");
$submod->addPage($page);

$page = new Page("deployUpdatemajor", _T('Deploy Major Updates On Machine', 'updates'));
$page->setFile("modules/updates/updates/deployUpdatemajor.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("grpDeployUpdatemajor", _T('Deploy Major Updates On entity', 'updates'));
$page->setFile("modules/updates/updates/grpDeployUpdatemajor.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);


$page = new Page("ajaxMajorDetailsByMachines", _T("Details by Machines for major update", "updates"));
$page->setFile("modules/updates/updates/ajaxMajorDetailsByMachines.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("majorDetailsByMachines", _T('Machines major update', 'updates'));
$page->setFile("modules/updates/updates/majorDetailsByMachines.php");
$submod->addPage($page);

$page = new Page("ajaxgroupUpdateMajorEntity", _T("Deployment details on group entity", "updates"));
$page->setFile("modules/updates/updates/ajaxgroupUpdateMajorEntity.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);


$page = new Page("groupUpdateMajorEntity", _T('Machines major update', 'updates'));
$page->setFile("modules/updates/updates/groupUpdateMajorEntity.php");
$submod->addPage($page);

$page = new Page("auditByEntity", _T('History by Entity', 'updates'));
$page->setFile("modules/updates/updates/auditByEntity.php");
$submod->addPage($page);
$mod->addSubmod($submod);

$page = new Page("ajaxAuditByEntity", _T("History by Entity", "updates"));
$page->setFile("modules/updates/updates/ajaxAuditByEntity.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("auditByUpdate", _T('History by Update', 'updates'));
$page->setFile("modules/updates/updates/auditByUpdate.php");
$submod->addPage($page);
$mod->addSubmod($submod);

$page = new Page("ajaxAuditByUpdate", _T("History by Update", "updates"));
$page->setFile("modules/updates/updates/ajaxAuditByUpdate.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

// choose rule upa products
$page = new Page("approve_rules", _T('Automatic approval rules', 'updates'));
$page->setFile("modules/updates/updates/approve_rules.php");
$submod->addPage($page);

$page = new Page("ajaxApproveRules", _T("Choose update event for entity", "updates"));
$page->setFile("modules/updates/updates/ajaxApproveRules.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

/// choose produit
$page = new Page("approve_products", _T('Approve Microsoft products updates', 'updates'));
$page->setFile("modules/updates/updates/approve_products.php");
$submod->addPage($page);

$page = new Page("ajaxApproveProduct", _T("Choose product for entity", "updates"));
$page->setFile("modules/updates/updates/ajaxApproveProduct.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);


$mod->addSubmod($submod);

$MMCApp = &MMCApp::getInstance();
$MMCApp->addModule($mod);


