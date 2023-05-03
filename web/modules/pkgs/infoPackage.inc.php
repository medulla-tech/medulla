<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://siveo.net
 *
 * $Id$
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

/**
 * module declaration
 */
require_once("modules/medulla_server/version.php");

// hide msc module for the moment
$mod = new Module("pkgs");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Packages", "pkgs"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(800);


$submod = new SubModule("pkgs");
$submod->setDescription(_T("Packages", "pkgs"));
$submod->setImg('modules/pkgs/img/navbar/pkgs');
$submod->setDefaultPage("pkgs/pkgs/index");

//------ Rules ------
$page = new Page("rulesList" ,_T("Rules list", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/rulesList.php");
$submod->addPage($page);

$page = new Page("addRule" ,_T("Add a rule", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/addRule.php");
$submod->addPage($page);

$page = new Page("editRule" ,_T("Edit a rule", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/editRule.php");
$submod->addPage($page);

$page = new Page("deleteRule",_T("Delete a rule", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/deleteRule.php", array("AJAX" => True,"noHeader"=>True,"visible"=>False));
$submod->addPage($page);

//------ Packages ------
$page = new Page("index", _T('Show all packages', 'pkgs'));
$submod->addPage($page);

// $page = new Page("bundleList", _T('Show all bundles', 'pkgs'));
// $submod->addPage($page);

$page = new Page("add", _T('Add a package', 'pkgs'));
$submod->addPage($page);

$page = new Page("edit", _T('Edit a package', 'pkgs'));
$submod->addPage($page);

$page = new Page("detail", _T('Package detail', 'pkgs'));
$submod->addPage($page);

$page = new Page("preview", _T('Package File Preview', 'pkgs'));
$page->setOptions(array("AJAX" => True, "visible" => False, "noHeader"=>False));
$submod->addPage($page);

// $page = new Page("addBundle", _T('Add a bundle', 'pkgs'));
// $submod->addPage($page);
//
// $page = new Page("editBundle", _T('Edit a bundle', 'pkgs'));
// $submod->addPage($page);

$page = new Page("addXMPP", 'Add XMPP package');
$page->setOptions(array("AJAX" => True, "visible" => False, "noHeader"=>False));
$submod->addPage($page);

$page = new Page("createGroupLicence", _T("Create licence static group", "glpi"));
$page->setFile("modules/pkgs/pkgs/createGroupLicence.php");
$page->setOptions(array("visible"=>False, "noHeader"=>True));
$submod->addPage($page);

$submod->addPage($page);
$page = new Page("pending", _T('See pending packages', 'pkgs'));
$submod->addPage($page);
$page = new Page("appstreamSettings", _T('Appstream settings', 'pkgs'));
$submod->addPage($page);

$page = new Page("ajaxRefreshPackageTempDir", 'Display Package API Temporary Dir');
$page->setOptions(array("AJAX" => True, "visible" => False, "noHeader"=>True));
$submod->addPage($page);

// $page = new Page("ajaxGetSuggestedCommand", 'Get suggested command');
// $page->setOptions(array("AJAX" => True, "visible" => False, "noHeader"=>True));
// $submod->addPage($page);

$page = new Page("ajaxGetSuggestedCommand1", 'Get suggested command');
$page->setOptions(array("AJAX" => True, "visible" => False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("ajaxDisplayUploadForm", 'Display upload form');
$page->setOptions(array("AJAX" => True, "visible" => False, "noHeader"=>True));
$submod->addPage($page);

$page = new Page("rsync",_T("Show mirror status", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/rsync.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("desynchronization",_T("Pending Package synchronization", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/desynchronization.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("delete",_T("Delete a package", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/remove.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("deleteBundle",_T("Delete a bundle", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/removeBundle.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("activateAppstreamFlow" ,_T("Activate Appstream Stream", 'pkgs'));
$page->setFile("modules/pkgs/pkgs/activateAppstreamFlow.php", array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxXMLRPCCall");
$page->setFile("modules/pkgs/pkgs/ajaxXMLRPCCall.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxPendingPackageList");
$page->setFile("modules/pkgs/pkgs/ajaxPendingPackageList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxAppstreamActivatedPackageList");
$page->setFile("modules/pkgs/pkgs/ajaxAppstreamActivatedPackageList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxAppstreamAvailablePackageList");
$page->setFile("modules/pkgs/pkgs/ajaxAppstreamAvailablePackageList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxPackageList");
$page->setFile("modules/pkgs/pkgs/ajaxPackageList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxBundleList");
$page->setFile("modules/pkgs/pkgs/ajaxBundleList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("ajaxAutocompleteSearch");
$page->setFile("modules/pkgs/pkgs/ajaxAutocompleteSearch.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$page = new Page("viewAppstreamUpdates", _T("Appstream Updates list", "pkgs"));
$page->setFile("modules/pkgs/pkgs/viewAppstreamUpdates.php");
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);


?>
