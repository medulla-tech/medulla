<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2014 Mandriva, http://www.mandriva.com
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

include_once('common.inc.php');


function existGroup($group) {
    return xmlCall("base.existGroup", $group);
}

function get_groups(&$error) {
  $groups = xmlCall("base.getGroupsLdap",null);
  sort($groups);
  reset($groups);
  return $groups;
}

function get_default_group() {
  return xmlCall("base.getDefaultUserGroup",null);
}


function search_groups($filter = null) {
    $filter = cleanSearchFilter($filter);
    $groups = xmlCall("base.getGroupsLdap", $filter);
    sort($groups);
    reset($groups);
    return $groups;
}

function get_members($group) {
    return xmlCall("base.getMembers",$group);
}

function change_group_desc($cn, $desc) {
    return xmlCall("base.changeGroupDescription", array($cn, $desc));
}

function get_detailed_group($group) {
    return xmlCall("base.getDetailedGroup", array($group));
}

function get_user_groups($user) {
    return xmlCall('base.getUserGroups', $user);
}

function add_member($group, $user) {
    $param[]=$group;
    $param[]=$user;
    xmlCall('base.addUserToGroup', $param);
}

function del_member($group, $user) {
    $param[]=$group;
    $param[]=$user;
    xmlCall('base.delUserFromGroup',$param);
}

function create_group(&$error, $group) {
    if ($group == "") {
        $error = "Groupe nul";
        return;
    }

    if (in_array($group, get_groups($error))) {
        $error = sprintf(_("Group %s already exist"),$group);
        return;
    }

    $ret = xmlCall("base.createGroup", $group);

    if (in_array("samba", $_SESSION["supportModList"])) {
        // FIXME: should be a choice made by the user
        // Samba plugin is enabled, so we make this group a Samba group,
        // but only if we are a PDC.
        $pdc = xmlCall("samba.isPdc", null);
        if ($pdc) xmlCall("samba.makeSambaGroup", array($group));
    }
    if (!isXMLRPCError()) {
        return sprintf(_("Group %s created"),$group);
    } else {
        return;
    }
}

function del_group($group) {
    xmlCall("base.delGroup",$group);
}

?>
