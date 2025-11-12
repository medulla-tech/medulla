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

$page = new Page("index", _T('Page de tests', 'mastering'));
$page->setFile("modules/mastering/mastering/index.php");
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod); ?>

