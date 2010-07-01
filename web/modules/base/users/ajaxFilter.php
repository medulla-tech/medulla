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

require("modules/base/includes/users.inc.php");
require_once("modules/base/includes/logging-xmlrpc.inc.php");

global $conf;
if(isset($_REQUEST['maxperpage'])) {
    $maxperpage = $_REQUEST['maxperpage'];
} else {
    $maxperpage = $conf["global"]["maxperpage"];
}

$filter = $_GET["filter"];
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

list($usercount, $users) = get_users_detailed($error, $filter, $start, $start + $maxperpage);

$arrUser = array();
$arrSnUser = array();
$homeDirArr = array();
$mails = array();
$phones = array();
$css = array();

for ($idx = 0; $idx < count($users); $idx++) {
    if ($users[$idx]["enabled"]) {
        $css[$idx] = "userName";
    } else $css[$idx] = "userNameDisabled";
    $arrUser[]=$users[$idx]['uid'];

    $arrSnUser[]=$users[$idx]['givenName'].' '.$users[$idx]['sn'];;

    if (strlen($users[$idx]["mail"]) > 0) {
        $mails[] = '<a href="mailto:' . $users[$idx]["mail"] . '">' . $users[$idx]["mail"] . "</a>";
    } else {
        $mails[] = $users[$idx]["mail"];
    }
    /* We display the smallest telephone number, hopefully it is the user phone extension */
    $num = null;
    foreach($users[$idx]["telephoneNumber"] as $number) {
        if ($num == null) $num = $number;
        else if (strlen($number) < strlen($num)) $num = $number;
    }
    $phones[] = $num;
}

// $arrUser is the list of all Users
$n = new UserInfos($arrUser, _("Login"));
$n->setItemCount($usercount);
$n->setNavBar(new AjaxPaginator($usercount, $filter, "updateSearchParam",  $maxperpage));

$n->start = 0;
$n->end = $usercount - 1;

$n->setCssClass("userName");

$n->css = $css;

$n->addExtraInfo($arrSnUser,_("Name"));
$n->addExtraInfo($mails,_("Mail"));
$n->addExtraInfo($phones,_("Telephone"));

$n->addActionItem(new ActionItem(_("Edit"),"edit","edit","user"));
$n->addActionItem(new ActionItem(_("MMC rights"),"editacl","editacl","user") );
$n->addActionItem(new ActionPopupItem(_("Delete"),"delete","delete","user") );
$n->addActionItem(new ActionPopupItem(_("Backup"),"backup","backup","user") );
if (has_audit_working()) {
    $n->addActionItem(new ActionItem(_("Logged Actions"),"loguser","audit","user") );
}
$n->setName(_("Users"));
$n->display();

?>
