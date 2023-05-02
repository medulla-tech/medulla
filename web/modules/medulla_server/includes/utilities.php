<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
require_once("modules/medulla_server/includes/locations_xmlrpc.inc.php");

function quickGet($name, $p_first = false, $urldecode = True) {
    if ($p_first) {
        if (isset($_POST[$name]) && strlen($_POST[$name])) {
            $res = stripslashes($_POST[$name]);
        } elseif (isset($_GET[$name]) && strlen($_GET[$name])) {
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

function quickSet($name, $value) {
    $_GET[$name] = $value;
}

function idGet() {
    return quickGet('id');
}

function right_top_shortcuts_display() {
    if (
        (isset($_GET['cn']) and isset($_GET['objectUUID'])) or
        (isset($_GET['uuid']) and $_GET['uuid'] != "") or
        (isset($_GET['action']) and in_array($_GET['action'], array('BrowseFiles', 'BrowseShareNames', 'hostStatus')))
    ) { // Computers
        include_once('modules/medulla_server/includes/menu_action.php');
    } elseif (isset($_GET['gid'])) { // Groups
        include_once('modules/medulla_server/includes/menu_group_action.php');
    }
}

/*
 * Used to get $list and $values variables to
 * build an ajaxFilter or SelectItem element
 *
 * @param bool AllEntitiesValue: If True, include 'All my entities' value in element list
 * @return array list and values params
 */

function getEntitiesSelectableElements($AllEntitiesValue = False) {
    $list = array();
    $values = array();
    $locations = getUserLocations();

    if ($AllEntitiesValue) {
        if (count($locations) > 1) {
            $list['Pulse2ALL'] = _T('All my entities', 'medulla_server');
            $values['Pulse2ALL'] = '';
        }
    }
    foreach ($locations as $loc) {
        $values[$loc['uuid']] = $loc['uuid'];
        if (isset($loc['completename'])) {
            $list[$loc['uuid']] = $loc['completename'];
        } else {
            $list[$loc['uuid']] = $loc['name'];
        }
    }


    return array($list, $values);
}

/*
 *  Convert timestamp to date
 */

function timestamp_to_date($timestamp) {
        return date('Y/m/d', $timestamp);
}

/*
 *  Convert timestamp to datetime
 */
function timestamp_to_datetime($timestamp) {
        return gmdate('Y-m-d H:i:s', $timestamp);
}
/*
 * get UUID list of machines registered as Pull Machines
 */

function get_pull_targets() {
    if (!isset($_SESSION['pull_targets'])) {
        $_SESSION['pull_targets'] = array();
        if (in_array("msc", $_SESSION["modulesList"])) {
            $_SESSION['pull_targets'] = xmlcall('msc.get_pull_targets');
        }
    }
    return $_SESSION['pull_targets'];
}

function clean_xss($value){
  /*
   * Remove hex codes from string (i.e. %3B%2F ...), html <tags>
   * and closing tags like "> or '> to force script execution
   *
   */
  $binaryPattern = '#(%[0-9a-z]{2})#i';
  $tagsPattern = '#<[^>]*>#i';
  $closurePattern = '#([\' ?"]>)#i';

  if(is_array($value)){
    foreach($value as $_value){
      $_value = preg_replace($binaryPattern, "", $_value);
      $_value = preg_replace($tagsPattern, "", $_value);
      $_value = preg_replace($closurePattern, "", $_value);
      $_value = htmlentities($_value);
    }
  }
  else{
    $value = preg_replace($binaryPattern, "", $value);
    $value = preg_replace($tagsPattern, "", $value);
    $value = preg_replace($closurePattern, "", $value);
    $value = htmlentities($value);
  }
  return $value;
}
?>
