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

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

include('modules/pulse2/includes/menu_action.php');

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }
if (!isset($_GET['part'])) { $_GET['part'] = 'Hardware'; }
if (isset($_GET['groupname'])) { $groupname = $_GET['groupname']; } else { $groupname = ""; }
if (isset($_GET['gid'])) { $gid = $_GET['gid']; } else { $gid = ""; }

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$prefix = '';
if ($_GET['hostname'] != '') {
    $p->addTop(sprintf(_T("%s's inventory", 'inventory'), $_GET['hostname']), "modules/inventory/inventory/header.php");
} else {
    $p->addTop(sprintf(_T("%s's content inventory", 'inventory'), $groupname), "modules/inventory/inventory/header.php");
    $prefix = 'group';
}

// TODO get the list with trads from agent (conf file...)
$tab = 'Hardware';
$i = 0;
$p->addTab($prefix."tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part' => $tab, 'gid'=>$gid, 'groupname'=>$groupname));
$tab = 'Bios';
$i = 5;
$p->addTab($prefix."tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part' => $tab, 'gid'=>$gid, 'groupname'=>$groupname));

$i = 1;
foreach (array('Software', 'Network', 'Controller', 'Registry') as $tab) {
    $p->addTab($prefix."tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part' => $tab, 'gid'=>$gid, 'groupname'=>$groupname));
    $i++;
}

$tab = 'History';
$i++;
$p->addTab($prefix."tab$i", _T('History', 'inventory'), "", "modules/inventory/inventory/history.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part'=>$tab, 'gid'=>$gid, 'groupname'=>$groupname));

$p->display();

?>
