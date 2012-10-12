<?php
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

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/includes/html.php");

$type = $_GET['type'];
$field = $_GET['field'];
$filter = $_GET['filter'];
$from = $_GET['from'];

$p = new PageGenerator(_T("Chart", 'inventory'));
$p->setSideMenu($sidemenu);
$p->display();

$img = new RenderedImage(urlStr("inventory/inventory/graph", array("gid"=>$_GET['gid'], 'uuid'=>$_GET['uuid'], "type"=>$type, "field"=>$field, "filter"=>$filter)), 'graph', 'center');
$img->display();

$params = array();
foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
    $params[$get] = $_GET[$get];
}

$lnk = new RenderedLink(urlStr($from, $params), _T('back', 'inventory')); //array('tab'=>$_GET['tab'], 'filter'=>$filter));
$lnk->display();

?>

