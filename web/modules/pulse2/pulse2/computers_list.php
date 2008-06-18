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

if (displayLocalisationBar()) {
    $ajax = new AjaxFilterLocation("modules/pulse2/pulse2/ajaxComputersList.php", "container", 'location', $param);

    $list = array();
    foreach (getUserLocations() as $name) {
        $list[$name] = $name;
    }
    $ajax->setElements($list);
    $ajax->setElementsVal($list);
} else {
    $ajax = new AjaxFilter("modules/pulse2/pulse2/ajaxComputersList.php", "container", $param);
}

$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

?>
