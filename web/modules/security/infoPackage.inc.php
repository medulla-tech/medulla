<?php
/**
 * Module Security
 */

require_once("modules/medulla_server/version.php");

$mod = new Module("security");
$mod->setVersion("1.0");
$mod->setRevision('');
$mod->setDescription(_T("Security", "security"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(1000);

$submod = new SubModule("security");
$submod->setDescription(_T("Security", "security"));
$submod->setVisibility(true);
$submod->setImg('modules/security/graph/navbar/security');
$submod->setDefaultPage("security/security/index");
$submod->setPriority(0);

// page principale
$page = new Page("index", _T('Synthèse CVE', 'security'));
$page->setFile("modules/security/security/index.php");
$submod->addPage($page);

// page ajax
$page = new Page("ajaxSecurityList");
$page->setFile("modules/security/security/ajaxSecurityList.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp = &MMCApp::getInstance();
$MMCApp->addModule($mod);
