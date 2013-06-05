<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/ppolicy/includes/ppolicy-xmlrpc.php");
require_once("modules/ppolicy/includes/ppolicy.inc.php");

/**
 * ppolicy module declaration
 */


$mod = new Module("ppolicy");
$mod->setVersion("3.1.0");
$mod->setRevision('$Rev$');
$mod->setDescription(_T("Password Policy", "ppolicy"));
$mod->setAPIVersion("0:1:0");
$mod->setPriority(600);

/* Get the base module instance reference */
$base = &$MMCApp->getModule('base');
/* Get the users sub-module instance reference */
$users = &$base->getSubmod('users');

/* Add the page to the module */
$page = new Page("indexppolicy",_T("Password policies", "ppolicy"));
$page->setFile("modules/ppolicy/default/index.php");
$users->addPage($page);

$page = new Page("addppolicy",_T("Add a password policy", "ppolicy"));
$page->setFile("modules/ppolicy/default/add.php");
$users->addPage($page);

$page = new Page("editppolicy",_T("Edit a password policy", "ppolicy"));
$page->setFile("modules/ppolicy/default/edit.php");
$page->setOptions(array("visible" => False));
$users->addPage($page);

$page = new Page("deleteppolicy",_T("Delete a password policy", "ppolicy"));
$page->setFile("modules/ppolicy/default/delete.php",
    array("noHeader" => True, "visible" => False)
);
$users->addPage($page);

$page = new Page("ajaxPPoliciesFilter");
$page->setFile("modules/ppolicy/default/ajaxPPoliciesFilter.php",
    array("AJAX" => True, "visible" => False)
);
$users->addPage($page);

/* Declare variable to will can set hiden it */
$ppolicyattr = getPPolicyAttributesKeys();

foreach ($ppolicyattr as $key=>$info) {    // separate right between Global Password Policies Attributes from User PPolicy Attributes
    $mod->addACL('g'.$key, _T("Default ".$info[0],"ppolicy"));
}

$mod->addACL("ppolicyactivated", _T("Enable user specific password policy","ppolicy"));
foreach ($ppolicyattr as $key=>$info) {    // foreach the list of Supported Attributes
    $mod->addACL($key, _T($info[0],"ppolicy"));
}


$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

/* You should unset the references when you finished using them */
unset($base);
unset($users);
?>
