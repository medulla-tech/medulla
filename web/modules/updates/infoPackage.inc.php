<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/infoPackage.inc.php

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

$page = new Page("index", _T('Update status', 'updates'));
$submod->addPage($page);

$page = new Page("deployWinGroup", _T('Deploy an update on a group', 'updates'));
$page->setFile("modules/updates/updates/deployWinGroup.php");
$page->setOptions(array("visible" => false));
$submod->addPage($page);

$page = new Page("ajaxDeployWinGroup", _T('Deploy an update on a group', 'updates'));
$page->setFile("modules/updates/updates/ajaxDeployWinGroup.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

// Guarded by the deployWinGroup ACL in the page itself.
$page = new Page("deployWinGroupUpdate", _T('Deploy', 'updates'));
$page->setFile("modules/updates/updates/deployWinGroupUpdate.php");
$page->setOptions(array("visible" => false, "noHeader" => true, "noACL" => true));
$submod->addPage($page);

$page = new Page("upgradeWinGroup", _T('Upgrade this group', 'updates'));
$page->setFile("modules/updates/updates/upgradeWinGroup.php");
$page->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($page);

$page = new Page("settingsWin", _T('Settings', 'updates'));
$page->setFile("modules/updates/updates/settingsWin.php");
$submod->addPage($page);

$page = new Page("MajorEntitiesList", _T('Upgrades', 'updates'));
$page->setFile("modules/updates/updates/MajorEntitiesList.php");

$tab = new Tab("tabwin", _T("Windows", "updates"));
$page->addTab($tab);

$tab = new Tab("tablinux", _T("Linux", "updates"));
$page->addTab($tab);

$submod->addPage($page);

$page = new Page("updatesListWin", _T('Approval', 'updates'));
$page->setFile("modules/updates/updates/updatesListWin.php");

// System tabs share the page ACL.
foreach (array("tabwin" => _T("Windows", "updates"),
               "tablinux" => _T("Linux", "updates")) as $tabId => $tabLabel) {
    $tab = new Tab($tabId, $tabLabel);
    $tab->setOptions(array("noACL" => true));
    $page->addTab($tab);
}

$submod->addPage($page);

$page = new Page("ajaxApprovalsListWin", _T("Approval", "updates"));
$page->setFile("modules/updates/updates/ajaxApprovalsListWin.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxMachinesListWin", _T("Update status", "updates"));
$page->setFile("modules/updates/updates/ajaxMachinesListWin.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("ajaxMachineUpdatesListWin", _T("Machine details", "updates"));
$page->setFile("modules/updates/updates/ajaxMachineUpdatesListWin.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("detailsMachineWin", _T("Machine details", "updates"));
$page->setFile("modules/updates/updates/detailsMachineWin.php");
$page->setOptions(array("visible" => false));
$submod->addPage($page);

$page = new Page("EntityComplianceos", _T("Update status", "updates"));
$page->setFile("modules/updates/updates/EntityComplianceos.php");

$tab = new Tab("tabwin", _T("Windows", "updates"));
$page->addTab($tab);

$tab = new Tab("tablinux", _T("Linux", "updates"));
$page->addTab($tab);

$submod->addPage($page);

$page = new Page("grayApprove", _T('Approve', 'updates'));
$page->setFile("modules/updates/updates/grayApprove.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

// Guarded by the grayApprove ACL in the page itself.
$page = new Page("deployWinUpdate", _T('Deploy', 'updates'));
$page->setFile("modules/updates/updates/deployWinUpdate.php");
$page->setOptions(array("visible" => false, "noHeader" => true, "noACL" => true));
$submod->addPage($page);

$page = new Page("uninstallWinUpdate", _T('Uninstall', 'updates'));
$page->setFile("modules/updates/updates/uninstallWinUpdate.php");
$page->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($page);

$page = new Page("banUpdate", _T('Decline', 'updates'));
$page->setFile("modules/updates/updates/banUpdate.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("whiteUnlist", _T('Back to pending', 'updates'));
$page->setFile("modules/updates/updates/whiteUnlist.php", array("noHeader" => true,"visible" => false));
$submod->addPage($page);

$page = new Page("ajaxMajorTabMachines", _T("Upgrades", "updates"));
$page->setFile("modules/updates/updates/ajaxMajorTabMachines.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$page = new Page("products", _T('Tracked products', 'updates'));
$page->setFile("modules/updates/updates/products.php");

$tab = new Tab("tabwin", _T("Windows", "updates"));
$page->addTab($tab);

$tab = new Tab("tablinux", _T("Linux", "updates"));
$page->addTab($tab);

$submod->addPage($page);

$page = new Page("automation", _T('Automatic approval', 'updates'));
$page->setFile("modules/updates/updates/automation.php");

$tab = new Tab("tabwin", _T("Windows", "updates"));
$page->addTab($tab);

$tab = new Tab("tablinux", _T("Linux", "updates"));
$page->addTab($tab);

$submod->addPage($page);

// Guarded by the ACL of the page whose setting is reset, in the page itself.
$page = new Page("resetWinSetting", _T('Use the setting of the parent entity', 'updates'));
$page->setFile("modules/updates/updates/resetWinSetting.php");
$page->setOptions(array("visible" => false, "noHeader" => true, "noACL" => true));
$submod->addPage($page);

// Guarded by the grayApprove ACL and the MajorEntitiesList tab ACL of the system in the page itself.
$page = new Page("launchUpgrade", _T('Upgrade machine', 'updates'));
$page->setFile("modules/updates/updates/launchUpgrade.php");
$page->setOptions(array("visible" => false, "noHeader" => true, "noACL" => true));
$submod->addPage($page);

// Guarded by the grayApprove ACL and the MajorEntitiesList tab ACL of the system in the page itself.
$page = new Page("cancelUpgrade", _T('Abandon', 'updates'));
$page->setFile("modules/updates/updates/cancelUpgrade.php");
$page->setOptions(array("visible" => false, "noHeader" => true, "noACL" => true));
$submod->addPage($page);

// Guarded by the grayApprove ACL and the entity of the machine in the page itself.
$page = new Page("restartMachine", _T('Restart', 'updates'));
$page->setFile("modules/updates/updates/restartMachine.php");
$page->setOptions(array("visible" => false, "noHeader" => true, "noACL" => true));
$submod->addPage($page);

$page = new Page("ajaxUpdateCreateGroup", _T("Create GRP update", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdateCreateGroup.php");
$page->setOptions(array("visible" => false, "AJAX" => true, "noHeader" => true));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp = &MMCApp::getInstance();
$MMCApp->addModule($mod);

