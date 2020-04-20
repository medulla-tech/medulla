<?php
require("graph/navbar.inc.php");
require("modules/base/computers/localSidebar.php");

require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("XMPP Relays list", 'glpi'));
$p->setSideMenu($sidemenu);
$p->display();

print "<br/><br/><br/>";
$ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxXmppRelaysList"), "container", array('login' => $_SESSION['login']), 'formRunning');
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();
 ?>
