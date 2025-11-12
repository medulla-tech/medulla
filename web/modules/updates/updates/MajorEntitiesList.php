<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

// require_once("modules/updates/includes/xmlrpc.php");
// require_once("modules/admin/includes/xmlrpc.php");
// require_once("modules/xmppmaster/includes/xmlrpc.php");
// require_once("modules/updates/includes/updates.inc.php");

global $maxperpage;


$p = new PageGenerator(_T("Entity Compliance", "updates"));
$p->setSideMenu($sidemenu);
$p->display();

$refresh = new RefreshButton();
print "<br/>";
$refresh->display();

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMajorEntitiesList"), "container", array('source' => 'xmppmaster'), 'formRunning');

$ajax->setRefresh($refresh->refreshtime());
$ajax->display();
$ajax->displayDivToUpdate();

$p = new TabbedPageGenerator();
//$p->setSideMenu($sidemenu);
$p->addTab("tabwin", _T("Os Windows", "updates"), "",
           "modules/updates/updates/major/osWindows.php", array());

$p->addTab("tabwinserv", _T("OS Windows Server", "dyngroup"), "",
           "modules/updates/updates/major/osWindowsserveur.php", array());
/*
$p->addTab("tabrhel", _T("OS Rhel", "dyngroup"), "",
           "modules/updates/updates/major/Redhat.php", array());

$p->addTab("tabalma", _T("OS Alma", "dyngroup"), "",
           "modules/updates/updates/major/Alma.php", array());

$p->addTab("tabcentosos", _T("OS CentOS", "dyngroup"), "",
           "modules/updates/updates/major/Centos.php", array());

$p->addTab("tabdebian", _T("OS Debian", "dyngroup"), "",
           "modules/updates/updates/major/Debian.php", array());

$p->addTab("tabsuse", _T("OS Suse", "dyngroup"), "",
           "modules/updates/updates/major/Suse.php", array());

$p->addTab("tabubuntu", _T("OS Ubuntu", "dyngroup"), "",
           "modules/updates/updates/major/Ubuntu.php", array());

$p->addTab("tabfedora", _T("OS Fedora", "dyngroup"), "",
           "modules/updates/updates/major/Fedora.php", array());*/
$p->display();
?>
