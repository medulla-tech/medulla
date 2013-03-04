<?
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

require("modules/glpi/includes/xmlrpc.php");
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/pulse2/includes/utilities.php");

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }
if (!isset($_GET['part'])) { $_GET['part'] = 'Summary'; }

$uuid = '';
$hostname = '';
if (isset($_GET['uuid'])) { $uuid = $_GET['uuid']; }
if (isset($_GET['hostname'])) { $hostname = $_GET['hostname']; }

$uri = getGlpiMachineUri();
if ($uri) {
    $glpi_link = sprintf('<a href="%s" target="new">GLPI</a>', $uri.str_replace('UUID', '', $uuid));
}
else {
    $glpi_link = 'GLPI';
}

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("%s's inventory (%s)", "glpi"), $hostname, $glpi_link), "modules/glpi/glpi/header.php");

$i = 0;
// TODO get the list with trads from agent (conf file...)

$tabList = array(
    'Summary' => _T('Summary', "glpi"),
    'Hardware' => _T('Hardware', "glpi"),
    'Storage' => _T('Storage', "glpi"),
    'Network' => _T('Network', "glpi"),
    'Softwares' => _T('Softwares', "glpi"),
    'Administrative' => _T('Administrative', "glpi"),
    'History' => _T('History', "glpi"),
);

foreach ($tabList as $tab => $str) {
    $p->addTab("tab$i", $str, "", "modules/glpi/glpi/view_part.php", array('hostname'=>$hostname, 'uuid'=>$uuid, 'part' => $tab));
    $i++;
}

$p->display();

?>
