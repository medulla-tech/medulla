<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

// require_once("modules/updates/includes/xmlrpc.php");
// require_once("modules/admin/includes/xmlrpc.php");
// require_once("modules/xmppmaster/includes/xmlrpc.php");
// require_once("modules/updates/includes/updates.inc.php");

global $maxperpage;

$p = new PageGenerator(_T("Entities Compliance", "updates"));
$p->setSideMenu($sidemenu);
$p->display();
/*
$refresh = new RefreshButton();
print "<br/>";
$refresh->display();

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMajorEntitiesList"), "container", array('source' => 'xmppmaster'), 'formRunning');

$ajax->setRefresh($refresh->refreshtime());
$ajax->display();
$ajax->displayDivToUpdate();*/

$p = new TabbedPageGenerator();
//$p->setSideMenu($sidemenu);
$p->addTab("tabwin", _T("Windows", "updates"), "",
           "modules/updates/updates/major/osWindows.php", array());

$p->addTab("tabwinserv", _T("Windows Server", "updates"), "",
           "modules/updates/updates/major/osWindowsserveur.php", array());

$p->addTab("tabalma", _T("AlmaLinux", "updates"), "",
           "modules/updates/updates/major/Alma.php", array());

$p->addTab("tabcentosos", _T("CentOS", "updates"), "",
           "modules/updates/updates/major/Centos.php", array());

$p->addTab("tabdebian", _T("Debian", "updates"), "",
           "modules/updates/updates/major/Debian.php", array());

$p->addTab("tabfedora", _T("Fedora", "updates"), "",
           "modules/updates/updates/major/Fedora.php", array());

$p->addTab("tabmint", _T("Mint", "updates"), "",
           "modules/updates/updates/major/Mint.php", array());

$p->addTab("tabrhel", _T("Redhat", "updates"), "",
           "modules/updates/updates/major/Redhat.php", array());

$p->addTab("tabsuse", _T("Suse", "updates"), "",
           "modules/updates/updates/major/Suse.php", array());

$p->addTab("tabubuntu", _T("Ubuntu", "updates"), "",
           "modules/updates/updates/major/Ubuntu.php", array());

$p->addTab("tabzorin", _T("Zorin", "updates"), "",
           "modules/updates/updates/major/Zorin.php", array());


$p->display();
?>
