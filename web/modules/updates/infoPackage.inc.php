<?php
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

$page = new Page("ajaxMachineListOnEntities", _T("Details by Machines", "updates"));
$page->setFile("modules/updates/updates/ajaxMachineListOnEntities.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("deployAllUpdates", _T('Deploy all Updates', 'updates'));
$page->setFile("modules/updates/updates/deployAllUpdates.php");
$submod->addPage($page);

$page = new Page("ajaxPreDeployAll", _T("Deploy all Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxPreDeployAll.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("deploySpecificUpdate", _T('Deploy specific update', 'updates'));
$page->setFile("modules/updates/updates/deploySpecificUpdate.php");
$submod->addPage($page);

$page = new Page("ajaxUpdateToDeploy", _T("Deploy specific update", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdateToDeploy.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("updatesListWin", _T('Manage Windows Updates', 'updates'));
$page->setFile("modules/updates/updates/updatesListWin.php");
$submod->addPage($page);

$page = new Page("ajaxUpdatesListWin", _T("Manage Windows Updates", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesListWin.php");
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

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>
