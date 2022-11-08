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

$page = new Page("updatesListWin", _T('Manage Windows Updates', 'updates'));
$page->setFile("modules/updates/updates/updatesListWin.php");
$submod->addPage($page);

$page = new Page("ajaxUpdatesGreyListWin", _T("Manage Greylist", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesGreyListWin.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxUpdatesWhiteListWin", _T("Manage Whitelist", "updates"));
$page->setFile("modules/updates/updates/ajaxUpdatesWhiteListWin.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True, "noHeader"=>True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>

