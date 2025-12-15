<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");

global $conf;
$glpidisplayname = (!empty($conf['global']['glpidisplayname'])) ? $conf['global']['glpidisplayname'] : 'glpi';
$p = new PageGenerator(sprintf(_T("All devices %s", 'glpi'), $glpidisplayname));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxGlpiDevicesList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
