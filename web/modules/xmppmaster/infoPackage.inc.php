<?php
/**
 * (c) 2015-2017 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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

/**
 * module declaration
 */
require_once("modules/pulse2/version.php");

$mod = new Module("xmppmaster");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("xmppmaster", "xmppmaster"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(800);

$submod = new SubModule("xmppmaster");
$submod->setImg('modules/xmppmaster/img/navbar/xmppmaster');
$submod->setDescription(_T("Audit", "xmppmaster"));

$submod->setDefaultPage("xmppmaster/xmppmaster/index");

$page = new Page("index", _T('xmppmaster status', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("auditdeploy", _T('XMPP All users tasks', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("auditpastdeploys", _T('XMPP All users past task', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("auditmypastdeploys", _T('XMPP My Past tasks', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("consolexmpp", _T('XMPP Console', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("customQA", _T('XMPP Console', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("filesmanagers", _T('XMPP files managers', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("ajaxFiltercustom");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxFiltercustom.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("editqa", _T('Edit Custom Quick Action', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("", _T('delete Custom Quick Action', 'xmppmaster'));
$submod->addPage($page);


$page = new Page("deleteqa",_T("Delete Custom Quick Action", 'pkgs'));
$page->setFile("modules/xmppmaster/xmppmaster/removeqa.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);


$page = new Page("logbymachine", _T('XMPP logs', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("logbygrpmachine", _T('XMPP logs grp', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("consolecomputerxmpp", _T('XMPP Console', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("xmppfilesbrowsing", _T('XMPP browser file', 'xmppmaster'));
$submod->addPage($page);

//ne non expert mode
$page = new Page("xmppfilesbrowsingne", _T('XMPP browser file', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("ActionQuickconsole", _T('XMPP Console', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("wakeonlan", _T('Wake on LAN', 'xmppmaster'));
$submod->addPage($page);
// ajax procedure read and send result from log
$page = new Page("ajaxdeploylog");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxdeploylog.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("xmpprefrechfilesremote");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxxmpprefrechfilesremote.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("xmpprefrechfilesremotene");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxxmpprefrechfilesremotene.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("xmppplugindownload");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxxmppplugindownload.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("xmpprefrechfileslocal");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxxmpprefrechfileslocal.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("xmpprefrechfileslocalne");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxxmpprefrechfileslocalne.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("xmppremotecmd");
$page->setFile("modules/xmppmaster/xmppmaster/xmppremotecmdshell.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

// $tab = new Tab("tablaunch", _T("MSC launch tab for a machine", "msc"));
//     $page->addTab($tab);
// --------------QUICK ACTION--------------------

$page = new Page("deployquick", _T("action deploy quick", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/deployquick.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("deployquickgroup", _T("quick action deploy group", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/deployquickgroup.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);


$page = new Page("actionwakeonlan", _T("quick action Wol", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/actionwakeonlan.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("actioninventory", _T("quick action Inventory", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/actioninventory.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);


$page = new Page("actionrestart", _T("quick action Restart", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/actionrestart.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("actionshutdown", _T("quick action shutdown", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/actionshutdown.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("actionvncchangeperms", _T("quick action change vnc settings", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/actionvncchangeperms.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("actionrestart", _T("quick action Install key", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/actionkeyinstall.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);
// --------------END QUICK ACTION--------------------

// ajax procedure to start a reversessh on client machine for guacamole
$page = new Page("actionreversessh", _T("quick action reversessh for guacamole", "xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/actionreversesshguacamole.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

// ajax procedure read and send result from log
$page = new Page("viewlogs",_T('Audit deployment', 'xmppmaster'));
$page->setFile("modules/xmppmaster/xmppmaster/logs/viewlogs.php");
$page->setOptions(array("visible" => True, "noHeader" => False));
$submod->addPage($page);

$page = new Page("logbymachine", _T('XMPP log', 'xmppmaster'));
$page->setFile("modules/xmppmaster/xmppmaster/logs/logbymachine.php");
$page->setOptions(array("visible" => True, "noHeader" => True));
$submod->addPage($page);

$page = new Page("logbygrpmachine", _T('XMPP log', 'xmppmaster'));
$page->setFile("modules/xmppmaster/xmppmaster/logs/logbygrpmachine");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("ajaxstatusxmpp",_T("List all groups of computers","xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/ajaxstatusxmpp.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxviewgrpdeploy",_T("ajax view grp deploy","xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/logs/ajaxviewgrpdeploy.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxlogsxmpp",_T("List computers deploy","xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/ajaxlogsxmpp.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxlogsgrpxmpp",_T("List computers deploy by group","xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/ajaxlogsgrpxmpp.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxstatusxmppscheduler",_T("List computer deploy","xmppmaster"));
$page->setFile("modules/xmppmaster/xmppmaster/ajaxstatusxmppscheduler.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);
?>
