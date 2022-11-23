<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2017 Siveo, http://http://www.siveo.net
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

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

// get entities
require("modules/pulse2/includes/xmlrpc.inc.php");
require_once("modules/pulse2/includes/utilities.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

if(!isset($params))
    $params = array();

$p = new PageGenerator();
$p->setSideMenu($sidemenu);
$p->display();

# synchronization of locations
global $SYNCHROSTATE_UNKNOWN;
global $SYNCHROSTATE_TODO;
global $SYNCHROSTATE_SYNCHRO;
global $SYNCHROSTATE_RUNNING;
global $SYNCHROSTATE_INIT_ERROR;

$location = getCurrentLocation();

if (isset($_POST['bsync'])) {
    $params['bsync'] = '1';
    $ret = xmlrpc_synchroLocation($_POST['location_uuid']);
    // goto images list
    if ((is_array($ret) and $ret[0] or !is_array($ret) and $ret) and !isXMLRPCError()) {
        //$str = sprintf(_T("Boot menu generation Success for package server on location %s ", "imaging"),$_POST['location_uuid']);
        /* insert notification code here if needed */
    } elseif (!$ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Boot menu generation failed for package server: %s<br /><br />Check /var/log/mmc/pulse2-package-server.log", "imaging"), implode(', ', $ret[1]));
        new NotifyWidgetFailure($str);
    }
    elseif (isXMLRPCError()) {
        $str = sprintf(_T("Boot menu generation failed for package server: %s<br /><br />Check /var/log/mmc/pulse2-package-server.log", "imaging"), implode(', ', $ret[1]));
        new NotifyWidgetFailure($str);
    }
}

# needed in the case we have to go back to the good list.
$params['from'] = $_GET['action'];
$params['module'] = $_GET['module'];
$params['submod'] = $_GET['submod'];
$params['action'] = $_GET['action'];

if (displayLocalisationBar()) {
    $location = getCurrentLocation();

    $ajax = new AjaxLocation("modules/imaging/manage/$page.php", "container_$page", "location", $params);
    list($list, $values) = getEntitiesSelectableElements();
    $ajax->setElements($list);
    $ajax->setElementsVal($values);
    if($location)
        $ajax->setSelected($location);
    $ajax->display();
    $ajax->displayDivToUpdate();
}

?>
