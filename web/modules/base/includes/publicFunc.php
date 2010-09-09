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

function _base_infoUser($userObjClass) {
    if (array_search("posixAccount", $userObjClass)!==false) {
        print "posix ";
    }
}

function _base_enableUser($uid) {
    xmlCall("base.enableUser", array($uid));
}

function _base_disableUser($uid) {
    xmlCall("base.disableUser", array($uid));
}

function _base_changeUserPasswd($paramsArr) {
    return xmlCall("base.changeUserPasswd", $paramsArr);
} 

function _base_changeUserPrimaryGroup($uid, $group) {
    return xmlCall("base.changeUserPrimaryGroup", array($uid, $group));
}

function _base_delGroup($group) {
    $ret = xmlCall("base.delGroup", $group);
    if($ret == 2) {
        $msg = sprintf(_("Group %s can't be deleted.<br/>%s is the primary group of some users."), $group, $group);
    }
    else {
        $msg = sprintf(_("Group %s successfully deleted."), $group);
    }
    return array("code" => $ret, "info" => $msg);    
}

function _base_completeUserEntry(&$entry) {
    $attrs = array("title", "mail", "mobile", "facsimileTelephoneNumber", "homePhone");
    foreach($attrs as $attr) {
        if (!isset($entry[$attr])) {
            $entry[$attr] = array(null);
        }
    }
}

?>
