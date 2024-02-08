<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
 * (c) 2017 Siveo, http://http://www.siveo.net
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


global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if ($_GET['module'] == 'base' && $_GET['submod'] == 'computers') {
    require("modules/base/computers/localSidebar.php");
} else {
    require("modules/imaging/manage/localSidebar.php");
}
require_once('graph/navbar.inc.php');
require_once("modules/medulla_server/includes/utilities.php");

$_GET['hostname'] = isset($_GET['hostname'] ) ? $_GET['hostname'] : (isset($_GET['cn'])?$_GET['cn'] : "" );
$_GET['uuid'] = isset($_GET['uuid'] ) ? $_GET['uuid'] : (isset($_GET['objectUUID']) ? $_GET['objectUUID'] : null );
/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();
if ($_GET['uuid']) {
    $machine = getMachine(array('uuid' => $_GET['uuid']));
    if ($machine->uuid != $_GET['uuid']) {
        $p = new PageGenerator(sprintf(_T("%s's computer secure control", 'msc'), $_GET['hostname']));
        $p->setSideMenu($sidemenu);
        $p->display();
        include('modules/msc/msc/header.php');
    } else {
        if (empty($_GET['hostname']))
            $_GET['hostname'] = $machine->hostname;
        $p = new TabbedPageGenerator();
        $p->setSideMenu($sidemenu);
        $p->addTop(sprintf(_T("%s's computer secure control", 'msc'), $machine->hostname), "modules/msc/msc/header.php");
        //show list packages
        $p->addTab("tablaunch", _T("Launch Actions", 'msc'), "", "modules/msc/msc/launch.php", array('uuid' => $machine->uuid, 'hostname' => $machine->hostname));
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
        if (!$group->all_params['ro'] || strtolower($group->all_params['ro']) === "false") {
                $p->addTab("grouptablaunch", _T("Launch Actions", 'msc'), "", "modules/msc/msc/launch.php", array('gid' => $_GET['gid']));
//             if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
//                 $p->addTab("grouptabbundle", _T("Launch Bundle", 'msc'), "", "modules/msc/msc/launch_bundle.php", array('gid' => $_GET['gid']));
//             }
        }
    }
    $p->display();
} else {
    $p = new PageGenerator();
    $p->setSideMenu($sidemenu);
    $p->display();
    print _T("Not enough information", "msc");
}
?>
<script type="text/javascript" src="jsframework/lib/raphael/raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.pie-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/utilities.js"></script>
