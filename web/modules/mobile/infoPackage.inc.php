<?php
require_once("modules/medulla_server/version.php");

$mod = new Module("mobile");
$mod->setVersion("1.0");
$mod->setDescription(_T("Mobiles", "mobile"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(10);
$submod = new SubModule("mobile");
$submod->setDescription(_T("Mobiles", "mobile"));
$submod->setVisibility(true);
$submod->setImg('img/other/mobile_down');
$submod->setDefaultPage("mobile/mobile/index");
$submod->setPriority(10);
$page = new Page("index", _T('Page de tests', 'mobile'));
$page->setFile("modules/mobile/mobile/index.php");
$submod->addPage($page);
$mod->addSubmod($submod);
$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);
//$submod->setImg("modules/imaging/img/imaging");

################################
# add enrole page 
################################

$pageEnrol = new Page("enrolMobile", _T('Enrôler un téléphone', 'mobile'));
$pageEnrol->setFile("modules/mobile/mobile/enrolMobile.php");
$submod->addPage($pageEnrol);

################################
# add configuration page  
################################

$pageConfig = new Page("addConfiguration", _T('Ajouter une configuration', 'mobile'));
$pageConfig->setFile("modules/mobile/mobile/addConfiguration.php");
$submod->addPage($pageConfig);


################################
# ListMobile - ajax
################################
$pageAjaxMobileList = new Page("ajaxMobileList", _T('Liste des mobiles', 'mobile'));
$pageAjaxMobileList->setFile("modules/mobile/mobile/ajaxMobileList.php");
$pageAjaxMobileList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxMobileList);

$pageAjaxMobileList = new Page("ajaxEnrolMobile", _T('Enrole mobiles', 'mobile'));
$pageAjaxMobileList->setFile("modules/mobile/mobile/ajaxenroMobile.php");
$pageAjaxMobileList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxMobileList);



?>