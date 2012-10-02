<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

require_once('modules/msc/includes/machines.inc.php');
require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/base/computers/localSidebar.php');
require_once('graph/navbar.inc.php');

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }

include('modules/base/includes/menu_action.php');

if ($_GET['uuid']) {
    $machine = getMachine(array('uuid'=>$_GET['uuid']));
    if ($machine->uuid != $_GET['uuid']) {
        $p = new PageGenerator(sprintf(_T("%s's computer secure control", 'msc'), $_GET['hostname']));
        $p->setSideMenu($sidemenu);
        $p->display();
        include('modules/msc/msc/header.php');
    } else {
        if (empty($_GET['hostname'])) $_GET['hostname'] = $machine->hostname;
        $p = new TabbedPageGenerator();
        $p->setSideMenu($sidemenu);
        $p->addTop(sprintf(_T("%s's computer secure control", 'msc'), $machine->hostname), "modules/msc/msc/header.php");
        $p->addTab("tablaunch", _T("Launch Actions", 'msc'), "", "modules/msc/msc/launch.php", array('uuid'=>$machine->uuid, 'hostname'=>$machine->hostname));
        $p->addTab("tabbundle", _T("Launch Bundle", 'msc'), "", "modules/msc/msc/launch_bundle.php", array('uuid'=>$machine->uuid, 'hostname'=>$machine->hostname));
        $p->addTab("tablogs", _T("Logs", 'msc'), "", "modules/msc/msc/logs.php", array('uuid'=>$machine->uuid, 'hostname'=>$machine->hostname));
        $p->addTab("tabhistory", _T("History", 'msc'), "", "modules/msc/msc/history.php", array('uuid'=>$machine->uuid, 'hostname'=>$machine->hostname));
        $p->display();
    }
} elseif ($_GET['gid']) {
    $p = new TabbedPageGenerator();
    $p->setSideMenu($sidemenu);
    require("modules/dyngroup/includes/includes.php");
    $group = new Group($_GET['gid'], true, true);
    if ($group->exists == False) {
        $msc_host = new RenderedMSCGroupDontExists($_GET['gid']);
        $msc_host->headerDisplay();
    } else {
        $p->addTop(sprintf(_T("%s's group secure control", 'msc'), $group->getName()), "modules/msc/msc/header.php");
        if (!$group->all_params['ro']) {
            $p->addTab("grouptablaunch", _T("Launch Actions", 'msc'), "", "modules/msc/msc/launch.php", array('gid'=>$_GET['gid']));
            $p->addTab("grouptabbundle", _T("Launch Bundle", 'msc'), "", "modules/msc/msc/launch_bundle.php", array('gid'=>$_GET['gid']));
        }
        $p->addTab("grouptablogs", _T("Logs", 'msc'), "", "modules/msc/msc/logs.php", array('gid'=>$_GET['gid']));
        $p->addTab("grouptabhistory", _T("History", 'msc'), "", "modules/msc/msc/history.php", array('gid'=>$_GET['gid']));
    }
    $p->display();
} else {
    $p = new PageGenerator();
    $p->setSideMenu($sidemenu);
    $p->display();
    print _T("Not enough informations", "msc");
}

?>
