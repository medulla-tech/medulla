<?php

/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Medulla 2, http://medulla.mandriva.org
 *
 * Medulla 2 is free software; you can redistribute it and/or modify
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
require_once("modules/medulla/includes/utilities.php");

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();

if (!isset($_GET['hostname'])) {
    $_GET['hostname'] = $_GET['cn'];
}
if (!isset($_GET['uuid'])) {
    $_GET['uuid'] = $_GET['objectUUID'];
}
if (!isset($_GET['part'])) {
    $_GET['part'] = 'Summary';
}
if (isset($_GET['groupname'])) {
    $groupname = $_GET['groupname'];
} else {
    $groupname = "";
}
if (isset($_GET['gid'])) {
    $gid = $_GET['gid'];
} else {
    $gid = "";
}

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
if (isset($_SESSION['pull_targets']) && in_array($_GET['uuid'], $_SESSION['pull_targets'])) {
    if (hasCorrectAcl('base', 'computers', 'remove_from_pull')) {
        $remove_pull_id = uniqid();
        $_SESSION['remove_pull_id'] = $remove_pull_id;
        $p->setDescription(
            sprintf(
                '%s <a class="btn btn-primary" href="%s">%s</a>',
                _T('This client has been registered in pull mode', 'inventory'),
                urlStrRedirect('base/computers/remove_from_pull', array('uuid' => $_GET['uuid'], 'remove_pull_id' => $remove_pull_id)),
                _T('Leave pull mode', 'inventory')
            )
        );
    } else {
        $p->setDescription(
            sprintf('%s', _T('This client has been registered in pull mode', 'inventory'))
        );
    }
}
$prefix = '';
if ($_GET['hostname'] != '') {
    $p->addTop(sprintf(_T("%s's inventory", 'inventory'), $_GET['hostname']), "modules/inventory/inventory/header.php");
} else {
    $p->addTop(sprintf(_T("%s's content inventory", 'inventory'), $groupname), "modules/inventory/inventory/header.php");
    $prefix = 'group';
}

// TODO get the list with trads from agent (conf file...)
$tab = 'Summary';
$i = 7;
$p->addTab($prefix . "tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'part' => $tab, 'gid' => $gid, 'groupname' => $groupname));
$tab = 'Hardware';
$i = 0;
$p->addTab($prefix . "tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'part' => $tab, 'gid' => $gid, 'groupname' => $groupname));
$tab = 'Storage';
$i = 8;
$p->addTab($prefix . "tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'part' => $tab, 'gid' => $gid, 'groupname' => $groupname));
/* $tab = 'Bios';
  $i = 5;
  $p->addTab($prefix . "tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'part' => $tab, 'gid' => $gid, 'groupname' => $groupname));
 */

$i = 1;
foreach (array('Network', 'Software', 'Registry') as $tab) { // , 'Administrative'
    $p->addTab($prefix . "tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'part' => $tab, 'gid' => $gid, 'groupname' => $groupname));
    $i++;
}

$tab = 'History';
$i++;
$p->addTab($prefix . "tab$i", _T('History', 'inventory'), "", "modules/inventory/inventory/history.php", array('uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'part' => $tab, 'gid' => $gid, 'groupname' => $groupname));

$p->display();

$uuid = $_GET['uuid'];
if (isset($uuid)) {
    $f = new ValidatingForm();
    print("<br><br>");
    $result['xls_path'] = getReport($uuid, $_SESSION['lang']);
    $link = new SpanElement(sprintf(
        '<br /><a class="btn btn-primary" href="%s">%s</a>&nbsp;&nbsp;',
        urlStrRedirect("base/computers/get_file", array('path' => $result['xls_path'])),
        _T("Get XLS Report", "inventory")
    ));
    $f->add($link);
    $f->pop();
    $f->display();
}
