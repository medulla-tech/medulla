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

require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/includes/html.php");
require_once("modules/base/includes/AjaxFilterLog.inc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");

$params = array("part" => $table, "from" => 'inventory%2Finventory%2F'.strtolower($table));

foreach (array('uuid', 'hostname', 'gid', 'groupname', 'tab') as $get) {
    if (isset($_GET[$get])) {
        $value = $_GET[$get];
    } else {
        $value = '';
    }
    $params[$get] = $value;
}
$titles = array('index' => _T('Bios list', 'inventory'),
                'hardware' => _T('Hardware and OS information list', 'inventory'),
                'software' => _T('Software list', 'inventory'),
                'network' => _T('Network card and configuration list', 'inventory'),
                'controller' => _T('Controller list', 'inventory'),
                'registry' => _T('Registry keys/values list', 'inventory'),
                'drive' => _T('Drive list', 'inventory'),
                'input' => _T('Input device list', 'inventory'),
                'memory' => _T('Memory module list', 'inventory'),
                'monitor' => _T('Monitor list', 'inventory'),
                'port' => _T('Port list', 'inventory'),
                'printer' => _T('Printer list', 'inventory'),
                'sound' => _T('Sound list', 'inventory'),
                'storage' => _T('Storage medium list', 'inventory'),
                'videocard' => _T('Video card list', 'inventory')
);

                

$p = new PageGenerator($titles[$_GET['action']]);
$p->setSideMenu($sidemenu);
$p->setNoFixHeight();
$p->display();

$ajax = new AjaxFilterInventory(urlStrRedirect("inventory/inventory/ajaxViewPart"), "container", $params);
$ajax->display();
$ajax->displayDivToUpdate();

?>
