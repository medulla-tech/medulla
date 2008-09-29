<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

global $table, $label, $filter;

require_once("modules/inventory/includes/xmlrpc.php");

require("localSidebar.php");
require("graph/navbar.inc.php");

$url = 'modules/inventory/inventory/ajaxViewPart.php?part='.$table.'&from=inventory%2Finventory%2F'.strtolower($table);
foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab') as $get) {
    $url .= "&$get=".$_GET[$get];
}
$ajax = new AjaxFilter($url);

$ajax->display();
$p = new PageGenerator(sprintf(_T("%s list", "inventory"), $label));
$p->setSideMenu($sidemenu);
$p->setNoFixHeight();
$p->display();

$ajax->displayDivToUpdate();

?>
