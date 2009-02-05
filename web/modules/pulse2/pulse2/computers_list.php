<?
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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

require("modules/pulse2/includes/xmlrpc.inc.php");
require("modules/pulse2/includes/locations_xmlrpc.inc.php");

$param = array();
if (isset($_GET['gid'])) { $param['gid'] = $_GET['gid']; }
if (isset($_GET['request'])) { $param['request'] = $_GET['request']; }
if (isset($_GET['equ_bool'])) { $param['equ_bool'] = $_GET['equ_bool']; }

if (displayLocalisationBar()) {
    $ajax = new AjaxFilterLocation("modules/base/computers/ajaxComputersList.php", "container", 'location', $param);

    $list = array();
    $values = array();
    foreach (getUserLocations() as $loc) {
        $values[$loc['uuid']] = $loc['name'];
        if (isset($loc['altname'])) {
            $list[$loc['uuid']] = $loc['altname'];
        } else {
            $list[$loc['uuid']] = $loc['name'];
        }
    }
    $ajax->setElements($list);
    $ajax->setElementsVal($values);
    if (!empty($_SESSION["computers.selected_location"])) {
        $ajax->setSelected($_SESSION["computers.selected_location"]);
    }
} else {
    $ajax = new AjaxFilter("modules/base/computers/ajaxComputersList.php", "container", $param);
}

$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

if (in_array("dyngroup", $_SESSION["modulesList"]) and isset($_GET['gid'])) {
    ?><a href='<?= urlStr("base/computers/csv", array('groupname'=>$_GET['groupname'], 'gid'=>$_GET['gid'])) ?>'><img src='modules/pulse2/graph/csv.png' alt='export csv'/></a><?php
}

?>
