<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

function quickGet($name, $p_first = false, $urldecode = True) {
    if ($p_first) {
        if (strlen($_POST[$name])) {
            $res = stripslashes($_POST[$name]);
        } elseif (strlen($_GET[$name])) {
            $res = $_GET[$name];
        } else {
            $res = null;
        }
    } else {
        if (isset($_GET[$name])) {
            $res = $_GET[$name];
        } elseif (isset($_POST[$name])) {
            $res = stripslashes($_POST[$name]);
        } else {
            $res = null;
        }
    }
    if ($urldecode) {
        return urldecode($res);
    } else {
        return $res;
    }
}

function quickSet($name, $value) { $_GET[$name] = $value; }

function idGet() { return quickGet('id'); }

function right_top_shortcuts_display() {
    if (
        (isset($_GET['cn']) and isset($_GET['objectUUID']))
        or (isset($_GET['uuid']) and $_GET['uuid'] != "")
        or (isset($_GET['action']) and in_array($_GET['action'], array('BrowseFiles', 'BrowseShareNames', 'hostStatus')))
    ) { // Computers
        include('modules/pulse2/includes/menu_action.php');
    }
    elseif(isset($_GET['gid'])) { // Groups
        include('modules/pulse2/includes/menu_group_action.php');
    }
}

?>
