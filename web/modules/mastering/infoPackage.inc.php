<?php
require_once("modules/medulla_server/version.php");

$mod = new Module("mastering");
$mod->setVersion("1.0");
//$mod->setRevision('');
$mod->setDescription(_T("Mastering", "mastering"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("mastering");
$submod->setDescription(_T("Mastering", "mastering"));
$submod->setVisibility(True);
$submod->setImg("modules/mastering/img/mastering");

$submod->setDefaultPage("mastering/mastering/index");
$submod->setPriority(500);

$page = new Page("index", _T('Create Action', 'mastering'));
$page->setFile("modules/mastering/mastering/index.php");
$submod->addPage($page);

$page = new Page("addAction", _T('Add Action', 'mastering'));
$page->setFile("modules/mastering/mastering/addAction.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxActionMachine", _T("Create Action on machine", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxActionMachine.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


$page = new Page("actionList", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/actionList.php");
$submod->addPage($page);


$page = new Page("ajaxActionList", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxActionList.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("results", _T("Results for action", "mastering"));
$page->setFile("modules/mastering/mastering/results.php");
$submod->addPage($page);

$page = new Page("ajaxResults", _T("Results for action", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxResults.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("masters", _T('Masters List', 'mastering'));
$page->setFile("modules/mastering/mastering/masters.php");
$submod->addPage($page);

$page = new Page("ajaxMasters", _T("Masters List", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxMasters.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxServerSize", _T("Server Size", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxServerSize.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


$page = new Page("createMaster", _T('Create Master', 'mastering'));
$page->setFile("modules/mastering/mastering/createMaster.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("register", _T('Register', 'mastering'));
$page->setFile("modules/mastering/mastering/register.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("deployMaster", _T('Deploy Master', 'mastering'));
$page->setFile("modules/mastering/mastering/deployMaster.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>

