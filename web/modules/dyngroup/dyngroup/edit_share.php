<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: add_groups.php 106 2008-06-30 13:30:54Z oroussy $
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

require("modules/base/computers/localSidebar.php");
require("modules/base/graph/computers/index.css");
require("modules/base/includes/users.inc.php");
require("modules/base/includes/groups.inc.php");
require("graph/navbar.inc.php");

require("modules/dyngroup/includes/groups.inc.php");

$name = quickGet('name');
$gid = quickGet('gid');
$group = new Group($gid, true);
if (!$name) { $name = $group->getName(); }

$p = new PageGenerator(sprintf(_T("Share groupe '%s' with", "dyngroup"), $name));
$sidemenu->forceActiveItem($item->action);
$p->setSideMenu($sidemenu);
$p->display();

$members = unserialize(base64_decode($_POST["lmembers"]));
$nonmemb = unserialize(base64_decode($_POST["lnonmemb"]));
$listOfMembers = unserialize(base64_decode($_POST["lsmembers"]));

if (isset($_POST["bdeluser_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            $ma = preg_split("/##/", $member);
            unset($members[$member]);
            unset($listOfMembers[$ma[1]]);
        }
    }
/*} elseif (isset($_POST['bfiltmachine_x'])) {
    $truncate_limit = 2000;
    $listOfMachines = getRestrictedComputersList(0, $truncate_limit, array('get'=>array('cn', 'objectUUID'), 'filter'=>$_POST['filter']), False);
    $count = getRestrictedComputersListLen();
    if ($truncate_limit < $count) {
        new NotifyWidgetWarning(sprintf(_T("Machine list has been truncated at %d machines", "dyngroup"), $truncate_limit));
    }
    $machines = array();
    foreach ($listOfMachines as $machine) {
        $machines[$machine['cn']."##".$machine['objectUUID']] = $machine['cn'];
    }
*/
} elseif (isset($_POST["badduser_x"])) {
    if (isset($_POST["nonmemb"])) {
        foreach ($_POST["nonmemb"] as $user) {
            $ma = preg_split("/##/", $user);
            $members[$user] = $ma[1];
            $listOfMembers[$ma[1]] = array('user'=>array('login'=>$ma[1], 'type'=>$ma[0]));
        }
    }
} elseif (isset($_POST["bconfirm"])) {
    $listOfCurMembers = $group->shareWith();
    if (!$listOfCurMembers) { $listOfCurMembers = array(); }

    $listN = array();
    $listC = array();
    foreach ($listOfMembers as $login => $member) { $listN[$member['user']['login']] = $member; }
    foreach ($listOfCurMembers as $member) { $listC[$member['user']['login']] = $member; }
    
    $newmem = array_diff_assoc($listN, $listC);
    $delmem = array_diff_assoc($listC, $listN);

    $res = $group->addShares($newmem) && $group->delShares($delmem);

    if ($res) {
        new NotifyWidgetSuccess(_T("Group successfully shared", "dyngroup"));
        $list = $group->shareWith();
        $members = array();
        foreach ($list as $member) {
            $listOfMembers[$member['user']['login']] = $member;
            $members[$member['user']['type']."##".$member['user']['login']] = $member['user']['login'];
        }
    } else {
        new NotifyWidgetFailure(_T("Group failed to share", "dyngroup"));
    }
} else {
    $list = $group->shareWith();
    $members = array();
    foreach ($list as $member) {
        $members[$member['user']['type']."##".$member['user']['login']] = $member['user']['login'];
        $listOfMembers[$member['user']['login']] = $member;
    }
    
    if (!$members) { $members = array(); }
    if (!$listOfMembers) { $listOfMembers = array(); }


    list($count, $users) = get_users_detailed($error, '', 0, 10000);
    $listOfUsers = array();
    foreach ($users as $u) {
        $listOfUsers[$u['uid']] = array('user'=>array('login'=>$u['uid'], 'type'=>0));
    }
    $groups = search_groups('');
    foreach ($groups as $u) {
        $listOfUsers[$u[0]] = array('user'=>array('login'=>$u[0], 'type'=>1));
    }
    $nonmemb = array();
    foreach ($listOfUsers as $user) {
        $nonmemb[$user['user']['type']."##".$user['user']['login']] = $user['user']['login'];
    }
}
ksort($members);
reset($members);
ksort($nonmemb);

$diff = array_diff_assoc($nonmemb, $members);
natcasesort($diff);

drawGroupShare($nonmemb, $members, $listOfMembers, $diff, $group->id, $name);

?>

