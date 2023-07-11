<?php
/**
 * (c) 2022-2023 Siveo, http://siveo.net/
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

require_once("modules/pulse2/version.php");

$mod = new Module("updates");
$mod->setVersion("1.0");
$mod->setDescription(_T("Updates", "updates"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("updates");
$submod->setDescription(_T("Updates", "updates"));
$submod->setVisibility(True);
$submod->setImg('modules/updates/graph/navbar/updates');
$submod->setDefaultPage("updates/updates/index");
$submod->setPriority(500);

$page = new Page("index", _T('Update Deployments', 'updates'));
$submod->addPage($page);

$page = new Page("ajaxEntitiesList", _T("Update Deployments", "updates"));
$page->setFile("modules/updates/updates/ajaxEntitiesList.php");
$page->setOptions(array("AJAX"=>True, "visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("detailsByMachines", _T('Details by Machines', 'updates'));
$page->setFile("modules/updates/updates/detailsByMachines.php");
$submod->addPage($page);

$page = new Page("ajaxDetailsByMachines", _T("Details by Machines", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsByMachines.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("deployAllUpdates", _T('Deploy all Updates', 'updates'));
$page->setFile("modules/updates/updates/deployAllUpdates.php");
$submod->addPage($page);

$page = new Page("ajaxDeployAllUpdates", _T("Deploy all Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxDeployAllUpdates.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("deployUpdate", _T('Deploy Specific Updates On Entity', 'updates'));
$page->setFile("modules/updates/updates/deployUpdate.php");
$submod->addPage($page);

$page = new Page("deploySpecificUpdate", _T('Deploy specific update', 'updates'));
$page->setFile("modules/updates/updates/deploySpecificUpdate.php");
$submod->addPage($page);

$page = new Page("detailsByUpdates", _T('List updates', 'updates'));
$page->setFile("modules/updates/updates/detailsByUpdates.php");
$submod->addPage($page);

$page = new Page("detailsSpecificUpdate", _T('Machine details for specific update', 'updates'));
$page->setFile("modules/updates/updates/detailsSpecificUpdate.php");
$submod->addPage($page);

$page = new Page("ajaxListMachineDetailSpecificUpdate", _T("Manage machine details for specific update", "updates"));
$page->setFile("modules/updates/updates/ajaxListMachineDetailSpecificUpdate.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxDeploySpecificUpdate", _T("Manage deploy specific update", "updates"));
$page->setFile("modules/updates/updates/ajaxDeploySpecificUpdate.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxDetailsByUpdates", _T("Manage List Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxDetailsByUpdates.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("updatesListWin", _T('Manage Windows Updates', 'updates'));
$page->setFile("modules/updates/updates/updatesListWin.php");
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWinWhite", _T("Manage Windows Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWinWhite.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWinGray", _T("Manage Windows Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWinGray.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWinBlack", _T("Manage Windows Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWinBlack.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("enableUpdate", _T('Enable Update', 'updates'));
$page->setFile("modules/updates/updates/enableUpdate.php");
$submod->addPage($page);

$page = new Page("disableUpdate", _T('Disable Update', 'updates'));
$page->setFile("modules/updates/updates/disableUpdate.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("whitelistUpdate", _T('Approve Update', 'updates'));
$page->setFile("modules/updates/updates/whitelistUpdate.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("blacklistUpdate", _T('Ban Update', 'updates'));
$page->setFile("modules/updates/updates/blacklistUpdate.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("greylistUpdate", _T('Unlist Update', 'updates'));
$page->setFile("modules/updates/updates/greylistUpdate.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("deleteRule", _T('UnBan Update', 'updates'));
$page->setFile("modules/updates/updates/deleteRule.php");
$submod->addPage($page);

$page = new Page("grayEnable", _T('Gray Enable', 'updates'));
$page->setFile("modules/updates/updates/grayEnable.php", array("noHeader"=>true,"visible"=>false));
$submod->addPage($page);

$page = new Page("grayDisable", _T('Grey Disable', 'updates'));
$page->setFile("modules/updates/updates/grayDisable.php", array("noHeader"=>true,"visible"=>false));
$submod->addPage($page);

$page = new Page("grayApprove", _T('Grey Approve', 'updates'));
$page->setFile("modules/updates/updates/grayApprove.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

// Also used for whitelist
$page = new Page("banUpdate", _T('Ban Update', 'updates'));
$page->setFile("modules/updates/updates/banUpdate.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("whiteUnlist", _T('White Unlist', 'updates'));
$page->setFile("modules/updates/updates/whiteUnlist.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);


$page = new Page("blackUnban", _T('Black Unban', 'updates'));
$page->setFile("modules/updates/updates/blackUnban.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("pendingUpdateByMachine", _T('Pending Updates', 'updates'));
$submod->addPage($page);

$page = new Page("ajaxPendingUpdateByMachine", _T('Pending Updates', 'updates'));
$page->setFile("modules/updates/updates/ajaxPendingUpdateByMachine.php", array("noHeader"=>True,"visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("auditUpdateByMachine", _T('Updates Done', 'updates'));
$submod->addPage($page);

$page = new Page("ajaxAuditUpdateByMachine", _T('Updates Done', 'updates'));
$page->setFile("modules/updates/updates/ajaxAuditUpdateByMachine.php", array("noHeader"=>True,"visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>
