<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require("modules/medulla_server/includes/xmlrpc.inc.php");
require_once("modules/medulla_server/includes/utilities.php");

$param = array();
if (isset($_SESSION['computerpresence'])  && $_SESSION['computerpresence'] != "all_computer")
    $param['computerpresence'] = $_SESSION['computerpresence'];

if (isset($_GET['gid'])) {
    $param['gid'] = urlencode($_GET['gid']);
}
if (isset($_GET['groupname'])) {
    $param['groupname'] = urlencode($_GET['groupname']);
}
//if (isset($_GET['request'])) { $param['request'] = $_SESSION['request'];}
/* if (isset($_GET['request'])) {
  $_SESSION['request'] = $_GET['request'];
  } */
if (isset($_GET['equ_bool'])) {
    $param['equ_bool'] = urlencode($_GET['equ_bool']);
}
if (isset($_GET['imaging_server'])) {
    $param['imaging_server'] = urlencode($_GET['imaging_server']);
}

if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    if (isset($_GET['cmd_id'])) {
        $param['cmd_id'] = urlencode($_GET['cmd_id']);
    }
    if (isset($_GET['login'])) {
        $param['login'] = urlencode($_GET['login']);
    }

    if (isset($_GET['id'])) {
        $param['id'] = urlencode($_GET['id']);
    }

    if (isset($_GET['ses'])) {
        $param['ses'] = urlencode($_GET['ses']);
    }

    if (isset($_GET['hos'])) {
        $param['hos'] = urlencode($_GET['hos']);
    }

    if (isset($_GET['sta'])) {
        $param['sta'] = urlencode($_GET['sta']);
    }

    if (isset($_GET['action'])) {
        $param['logview'] = urlencode($_GET['action']);
    }
}


if (displayLocalisationBar() && (isset($_GET['imaging_server']) && $_GET['imaging_server'] == '' || !isset($_GET['imaging_server']))) {
    $ajax = new AjaxFilterLocation(urlStrRedirect("base/computers/ajaxComputersList"), "container", 'location', $param);

    list($list, $values) = getEntitiesSelectableElements(True);
    $ajax->setElements($list);
    $ajax->setElementsVal($values);
    if (!empty($param['gid'])) {
        if (!empty($_SESSION["computers.selected_location." . $param['gid']])) {
            $ajax->setSelected($_SESSION["computers.selected_location." . $param['gid']]);
        }
    } else if (!empty($_SESSION["computers.selected_location"])) {
        $ajax->setSelected($_SESSION["computers.selected_location"]);
    }
} else {
    $ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxComputersList"), "container", $param);
}

$ajax->display();
echo "<br /><br /><br /><br />";
$ajax->displayDivToUpdate();
?>