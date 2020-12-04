<?php
/**
 * (c) 2020 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
require_once("modules/pulse2/version.php");

$mod = new Module("admin");
$mod->setVersion("4.6.5");
//$mod->setRevision('');
$mod->setDescription(_T("Admin", "admin"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(2000);

$submod = new SubModule("admin");
$submod->setDescription(_T("Admin", "admin"));
$submod->setVisibility(True);
$submod->setImg('modules/admin/graph/navbar/admin');
$submod->setDefaultPage("admin/admin/index");
$submod->setPriority(1001);

$page = new Page("index", _T('Clusters List', 'admin'));
$page->setFile("modules/admin/admin/index.php");
$submod->addPage($page);

$page = new Page("ajaxClustersList", _T("Clusters List", "admin"));
$page->setFile("modules/admin/admin/ajaxClustersList.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("relaysList", _T("Get the xmpp relays list", "glpi"));
$page->setFile("modules/admin/admin/relaysList.php");
$submod->addPage($page);

$page = new Page("ajaxRelaysList", _T("Relays List", "glpi"));
$page->setFile("modules/admin/admin/ajaxRelaysList.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);


$page = new Page("switchrelay",_T("Switch Relay","xmppmaster"));
$page->setFile("modules/admin/admin/switchrelay.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("reconfiguremachines",_T("Reconfigure Machines","xmppmaster"));
$page->setFile("modules/admin/admin/reconfiguremachines.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("detailactions", _T("Relays Detail Actions", "xmppmaster"));
$page->setFile("modules/admin/admin/detailactions.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("qalaunched", _T("Qa launched on Relays", "xmppmaster"));
$page->setFile("modules/admin/admin/qalaunched.php");
//$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("ajaxqalaunched", _T("Qa launched on Relays", "xmppmaster"));
$page->setFile("modules/admin/admin/ajaxqalaunched.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("qaresult", _T("Qa result on Relays", "xmppmaster"));
$page->setFile("modules/admin/admin/qaresult.php");
//$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("packageslist", _T("Packages List", "xmppmaster"));
$page->setFile("modules/admin/admin/packageslist.php");
//$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);

$page = new Page("ajaxpackageslist", _T("Packages List", "xmppmaster"));
$page->setFile("modules/admin/admin/ajaxpackageslist.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);


$page = new Page("consolexmpp", _T('XMPP Console', 'xmppmaster'));
$page->setFile("modules/xmppmaster/xmppmaster/consolexmpp.php");
$submod->addPage($page);


$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
