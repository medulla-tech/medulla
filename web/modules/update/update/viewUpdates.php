<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2013 Mandriva, http://www.mandriva.com
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
?>
<?php

require("graph/navbar.inc.php");
require_once("modules/update/includes/xmlrpc.inc.php");
require_once("modules/update/includes/html.inc.php");

$MMCApp = & MMCApp::getInstance();

$os_classes = get_os_classes();

$sidemenu = new SideMenu();
$sidemenu->setClass("update");

$sidemenu->addSideMenuItem(new SideMenuItem(_T('All updates', 'update'), "update", "update", "index"));

foreach ($os_classes['data'] as $os) {
    $item = new SideMenuItem($os['name'], "update", "update", "viewUpdates&os_class_id=" . $os['id']);
    $item->setCssId("osClass" . $os['id']);
    $sidemenu->addSideMenuItem($item);
}

if (isset($_GET['os_class_id'])) {
    $sidemenu->forceActiveItem("viewUpdates&os_class_id=" . $_GET['os_class_id']);
}

$p = new PageGenerator(_T("Update manager", 'update'));
$p->setSideMenu($sidemenu);
$p->display();
$params = array();

if (isset($_GET["os_class_id"]))
    $params['os_class_id'] = $_GET["os_class_id"];

$ajax = new AjaxFilterLocation(urlStrRedirect("update/update/ajaxUpdates"), "container", "status", $params);

$ajax->setElements(array(
                         _T('Available', 'update'),
                         _T('Enabled', 'update'),
                         _T('Disabled', 'update')
));

$ajax->setElementsVal(array('0', '1', '2'));
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();
?>