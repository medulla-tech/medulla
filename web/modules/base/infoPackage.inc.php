<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/base/includes/computers.inc.php");
require_once("modules/base/includes/logging-xmlrpc.inc.php");
require_once("modules/base/includes/users-xmlrpc.inc.php");

/**
 * module declaration
 */
$mod = new Module("base");
$mod->setVersion("3.1.0");
$mod->setRevision('$Rev$');
$mod->setAPIVersion("9:0:5");
$mod->setDescription(_("User, group and computer management"));
$mod->setPriority(0);

/**
 * define main submod
 */

$submod = new SubModule("main", _("Home"));
$submod->setVisibility(False);
$submod->setDefaultPage("base/main/default");
$submod->setPriority(0);

$page = new Page("default", _("Shortcuts"));
$page->setOptions(array("visible" => False));
$submod->addPage($page);

$page = new Page("favorites",_("Favorites page"));
$page->setOptions(array("visible" => False, "AJAX" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

/* Audit module */
if (has_audit_working()) {
    $submod = new SubModule("audit", _("MMC Logs"));
    $submod->setImg('modules/base/graph/navbar/logview');
    $submod->setDefaultPage("base/audit/indexall");
    $submod->setPriority(1000);

    $page = new Page("indexall",_T("All modules", "base"));
    $page->setFile("modules/base/audit/indexall.php", array("AJAX" =>False,"visible"=>True));
    $submod->addPage($page);

    $page = new Page("indexbase",_T("Users and Groups", "base"));
    $page->setFile("modules/base/audit/indexbase.php", array("AJAX" =>False,"visible"=>True));
    $submod->addPage($page);

    if(in_array("samba", $_SESSION["modulesList"])) {
        $page = new Page("indexsamba",_T("Samba", "base"));
        $page->setFile("modules/base/audit/indexsamba.php", array("AJAX" =>False,"visible"=>True));
        $submod->addPage($page);
    }

    if(in_array("mail", $_SESSION["modulesList"])) {
        $page = new Page("indexmail",_T("Mail", "base"));
        $page->setFile("modules/base/audit/indexmail.php", array("AJAX" =>False,"visible"=>True));
        $submod->addPage($page);
    }

    if(in_array("network", $_SESSION["modulesList"])) {
        $page = new Page("indexnetwork",_T("Network", "base"));
        $page->setFile("modules/base/audit/indexnetwork.php", array("AJAX" =>False,"visible"=>True));
        $submod->addPage($page);
    }

    if(in_array("sshlpk", $_SESSION["modulesList"])) {
        $page = new Page("indexsshlpk",_T("SSH public keys", "base"));
        $page->setFile("modules/base/audit/indexsshlpk.php", array("AJAX" =>False,"visible"=>True));
        $submod->addPage($page);
    }

    if(in_array("proxy", $_SESSION["modulesList"])) {
        $page = new Page("indexproxy",_T("Proxy", "base"));
        $page->setFile("modules/base/audit/indexproxy.php", array("AJAX" =>False,"visible"=>True));
        $submod->addPage($page);
    }

    $page = new Page("searchbar");
    $page->setFile("modules/base/includes/searchbar.php", array("AJAX" =>True,"visible"=>False));
    $submod->addPage($page);

    $page = new Page("ajaxLogFilter");
    $page->setFile("modules/base/audit/ajaxLogFilter.php", array("AJAX" =>True,"visible"=>False));
    $submod->addPage($page);

    $page = new Page("logview",_("View details of an action"));
    $page->setFile("modules/base/audit/logview.php", array("AJAX" =>False,"visible"=>False));
    $submod->addPage($page);

    $mod->addSubmod($submod);
}

// Deprecated module
if (isLogViewEnabled()) {
    $submod = new ExpertSubModule("logview", _("Log view"));
    $submod->setVisibility(True);
    $submod->setImg('modules/base/graph/navbar/logview');
    $submod->setDefaultPage("base/logview/index");
    $submod->setPriority(1001);

    $page = new Page("index",_("LDAP log"));
    $page->setFile("modules/base/logview/index.php", array("expert" => True));

    $submod->addPage($page);

    $page = new Page("show");
    $page->setFile("modules/base/logview/ajax_showlog.php",
                   array("AJAX" =>True,"visible"=>False));
    $submod->addPage($page);

    $page = new Page("setsearch");
    $page->setFile("modules/base/logview/ajax_setSearch.php",
                   array("AJAX" =>True,"visible"=>False));
    $submod->addPage($page);

    $mod->addSubmod($submod);
}

$submod = new SubModule("status", _("Status"));
$submod->setVisibility(True);
$submod->setImg('modules/base/graph/navbar/load');
$submod->setDefaultPage("base/status/index");
$submod->setPriority(10012);

$page = new Page("index",_("Default status page"));
$page->setFile("modules/base/status/index.php");
$submod->addPage($page);

if (! isCommunityVersion(true)) {
    $page = new Page("support",_("Support page"));
    $page->setFile("modules/base/status/support.php");
    $submod->addPage($page);
}

$mod->addSubmod($submod);

/**
 * user submod definition
 */

$submod = new SubModule("users", _("Users"));
$submod->setImg('modules/base/graph/navbar/user');
$submod->setDefaultPage("base/users/index");
$submod->setPriority(0);

$page = new Page("index",_("User list"));
$submod->addPage($page);

$page = new Page("ajaxAutocompleteGroup");
$page->setFile("modules/base/users/ajaxAutocompleteGroup.php",
               array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxFilter");
$page->setFile("modules/base/users/ajaxFilter.php",
               array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("add",_("Add a user"));
$submod->addPage($page);

$page = new Page("edit",_("Edit a user"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("editacl",_("Edit ACL permissions on a user"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("loguser",_("Logged user actions"));
$page->setFile("modules/base/users/loguser.php",
	               array("AJAX" =>False,"visible"=>False));
$submod->addPage($page);

$page = new Page("logview",_("Action details"));
$page->setFile("modules/base/users/logview.php",
                   array("AJAX" =>False,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxLogFilter");
$page->setFile("modules/base/audit/ajaxLogFilter.php",
	               array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("delete",_("Delete a user"));
$page->setFile("modules/base/users/delete.php",
               array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("backup",_("Backup user files"));
$page->setFile("modules/base/users/backup.php",
               array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("resetpasswd",_("Reset user password"));
if ($_SESSION["login"] == 'root' || $_SESSION['AUTH_METHOD'] == "login")
    $page->setOptions(array("visible" => False));
$submod->addPage($page);

$page = new Page("passwd",_("Change user password"));
if ($_SESSION["login"] == 'root' || $_SESSION['AUTH_METHOD'] == "token")
    $page->setOptions(array("visible" => False));
$submod->addPage($page);

$page = new Page("getPhoto", _("Get user photo"));
$page->setOptions(array("visible"=>False, "noHeader" =>True));
$submod->addPage($page);

$mod->addSubmod($submod);

/**
 * groups submod definition
 */

$submod = new SubModule("groups", _("Groups"));
$submod->setImg('modules/base/graph/navbar/group');
$submod->setDefaultPage("base/groups/index");
$submod->setPriority(1);

$page = new Page("index",_("Group list"));
$submod->addPage($page);

$page = new Page("add",_("Add a group"));
$submod->addPage($page);

$page = new Page("delete",_("Delete a group"));
$page->setFile("modules/base/groups/delete.php",
               array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxFilter");
$page->setFile("modules/base/groups/ajaxFilter.php",
               array("AJAX"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("members",_("Group members"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("edit",_("Edit a group"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$mod->addSubmod($submod);

/* Computer management module */

if (hasComputerManagerWorking()) {
    $submod = new SubModule("computers", _("Computers"));
    $submod->setImg('modules/base/graph/navbar/computer');
    $submod->setDefaultPage("base/computers/index");
    $submod->setPriority(3);

    $page = new Page("index", _("Computer list"));
    $submod->addPage($page);

    $page = new Page("add", _("Add computer"));
    if (!canAddComputer()) {
        $page->setOptions(array("visible"=>False));
    }
    $submod->addPage($page);

    $page = new Page("edit", _("Edit computer"));
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);

    $page = new Page("delete",_("Delete a computer"));
    $page->setFile("modules/base/computers/delete.php",
                   array("noHeader"=>True,"visible"=>False));
    $submod->addPage($page);

    $page = new Page("ajaxComputersList", _("Ajax part of computers list"));
    $page->setFile("modules/base/computers/ajaxComputersList.php");
    $page->setOptions(array("visible"=>False, "AJAX" =>True));
    $submod->addPage($page);

    $mod->addSubmod($submod);
}


/**
 * ACL properties
 */

$mod->addACL("jpegPhoto",_("User photo"));
$mod->addACL("uid",_("User login"));
$mod->addACL("sn", _("User name"));
$mod->addACL("givenName",_("User firstname"));
$mod->addACL("homeDir",_("User home directory"));
$mod->addACL("loginShell",_("Login shell"));
$mod->addACL("title",_("User title"));
$mod->addACL("mail",_("Mail address"));
$mod->addACL("telephoneNumber",_("Telephone number"));
$mod->addACL("mobile",_("Mobile phone number"));
$mod->addACL("facsimileTelephoneNumber",_("Fax number"));
$mod->addACL("homePhone",_("Home phone number"));
$mod->addACL("primary",_("Primary group"));
$mod->addACL("secondary",_("Secondary groups"));
$mod->addACL("cn",_("Common name"));
$mod->addACL("displayName",_("Preferred name to be used"));
$mod->addACL("pass",_("Password"));
$mod->addACL("confpass",_("Confirm your password"));
$mod->addACL("isBaseDesactive",_("Enable/Disable user account"));

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
