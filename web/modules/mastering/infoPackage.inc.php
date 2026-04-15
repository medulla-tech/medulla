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

// Default page
$submod->setDefaultPage("mastering/mastering/index");
$submod->setPriority(500);

// List the machines
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


// List of configured actions for entity
$page = new Page("actionList", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/actionList.php");
$submod->addPage($page);

$page = new Page("ajaxActionList", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxActionList.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


// List of configured actions for machines
$page = new Page("actionListMachine", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/actionListMachine.php");
$submod->addPage($page);

$page = new Page("ajaxActionListMachine", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxActionListMachine.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


// List of configured action for groups
$page = new Page("actionListGroup", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/actionListGroup.php");
$submod->addPage($page);

$page = new Page("ajaxActionListGroup", _T("List of Actions", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxActionListGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


// Result for a secific action
$page = new Page("results", _T("Results for action", "mastering"));
$page->setFile("modules/mastering/mastering/results.php");
$submod->addPage($page);

$page = new Page("ajaxResults", _T("Results for action", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxResults.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


// On groups list the machines with results on specified action
$page = new Page("resultsGroup", _T("Results for action", "mastering"));
$page->setFile("modules/mastering/mastering/resultsGroup.php");
$submod->addPage($page);

$page = new Page("ajaxResultsGroup", _T("Results for action", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxResultsGroup.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

// List masters
$page = new Page("masters", _T('Masters List', 'mastering'));
$page->setFile("modules/mastering/mastering/masters.php");
$submod->addPage($page);

$page = new Page("ajaxMasters", _T("Masters List", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxMasters.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

// Edit master
$page = new Page("editMaster", _T("Edit Master", "mastering"));
$page->setFile("modules/mastering/mastering/editMaster.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

// Delete master
$page = new Page("deleteMaster", _T("Delete Master", "mastering"));
$page->setFile("modules/mastering/mastering/deleteMaster.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


// Get the size on the server
// On distinct page to reduce the synchrone time needed to get the result
$page = new Page("ajaxServerSize", _T("Server Size", "mastering"));
$page->setFile("modules/mastering/mastering/ajaxServerSize.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


// Create master action
$page = new Page("createMaster", _T('Create Master', 'mastering'));
$page->setFile("modules/mastering/mastering/createMaster.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

// Register action
$page = new Page("register", _T('Register', 'mastering'));
$page->setFile("modules/mastering/mastering/register.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

// Deploy master action
$page = new Page("deployMaster", _T('Deploy Master', 'mastering'));
$page->setFile("modules/mastering/mastering/deployMaster.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

// Delete action
$page = new Page("deleteAction", _T('Delete Action', 'mastering'));
$page->setFile("modules/mastering/mastering/deleteAction.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>

