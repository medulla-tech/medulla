<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com/
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

require_once('modules/base/computers/localSidebar.php');
require_once('graph/navbar.inc.php');
require_once('modules/imaging/includes/includes.php');

$params = getParams();
$hostname = $params['hostname'];

if (isset($params['uuid'])) {
    $_GET['type'] = '';
    $_GET['target_uuid'] = $params['uuid'];
    $_GET['target_name'] = $params['hostname'];
    $params['type'] = '';
    $params['target_uuid'] = $params['uuid'];
    $params['target_name'] = $params['hostname'];
    if (!isset($_GET['uuid']) || $_GET['uuid'] == '') {
        $_GET['uuid'] = $params['uuid'];
    }

    $p = new TabbedPageGenerator();
    $sidemenu->forceActiveItem("index");
    $p->setSideMenu($sidemenu);    

    $params['hostname'] = $hostname;
    $p->addTop(sprintf(_T("%s's computer imaging", 'imaging'), $hostname), 
        "modules/imaging/imaging/header.php");
    $p->addTab("tabbootmenu", _T("Boot menu", 'imaging'), _T("Current boot menu", "imaging"), 
        "modules/imaging/imaging/bootmenu.php", $params);
    $p->addTab("tabimages", _T("Images and Masters", 'imaging'), "", 
        "modules/imaging/imaging/images.php", $params);
    $p->addTab("tabservices", _T("Boot services", 'imaging'), _T("Available boot menu services", "imaging"), 
        "modules/imaging/imaging/services.php", $params);
    $p->addTab("tablogs", _T("Imaging log", 'imaging'), "", 
        "modules/imaging/imaging/logs.php", $params);
    $p->addTab("tabconfigure", _T("Menu configuration", 'imaging'), "", 
        "modules/imaging/imaging/configure.php", $params);
    $p->display();
    
} elseif (isset($params['gid'])) {
    $_GET['type'] = 'group';
    $_GET['target_uuid'] = $params['gid'];
    $_GET['target_name'] = $params['hostname'];
    $params['type'] = 'group';
    $params['target_uuid'] = $params['gid'];
    $params['target_name'] = $params['hostname'];

    $p = new TabbedPageGenerator();
    $sidemenu->forceActiveItem("list_profiles");
    $p->setSideMenu($sidemenu);
    require("modules/dyngroup/includes/includes.php");
    $group = new Group($_GET['gid'], true);
    if ($group->exists == False) {
        $msc_host = new RenderedMSCGroupDontExists($_GET['gid']);
        $msc_host->headerDisplay();
    } else {
        $params['groupname'] = $group->getName();
        $p->addTop(sprintf(_T("%s's profile imaging", 'imaging'), $group->getName()), 
            "modules/imaging/imaging/header.php");
        $p->addTab("grouptabbootmenu", _T("Boot menu", 'imaging'), _T("Current boot menu", "imaging"), 
            "modules/imaging/imaging/bootmenu.php", $params);
        $p->addTab("grouptabimages", _T("Masters", 'imaging'), "", 
            "modules/imaging/imaging/images.php", $params);
        $p->addTab("grouptabservices", _T("Boot services", 'imaging'), _T("Available boot menu services", "imaging"), 
            "modules/imaging/imaging/services.php", $params);
        $p->addTab("grouptablogs", _T("Imaging log", 'imaging'), "", 
            "modules/imaging/imaging/logs.php", $params);
        $p->addTab("grouptabconfigure", _T("Menu configuration", 'imaging'), "", 
            "modules/imaging/imaging/configure.php", $params);
    }
    $p->display();
    
} else {

    $p = new PageGenerator();
    $p->setSideMenu($sidemenu);
    $p->display();
    print _T("Not enough informations", "imaging");
    
}

?>
