<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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


require_once('modules/glpi/includes/xmlrpc.php');

$params = array("from" => 'base%2computers%2Finvtabs');

/*
 * simpleTableParts are parts who are *not* displayed
 * in a multi-line table
 */

$simpleTableParts = array('Summary');

// Simple table
if (in_array($_GET['part'], $simpleTableParts)) {
    include('modules/glpi/glpi/ajaxViewPart.php');
}
// Multi-lines table
else {
    foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
        if (isset($_GET[$get])) {
            $value = $_GET[$get];
            $params[$get] = $value;
        }
    }
    $ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxViewPart"), "container", $params);

    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}
?>
