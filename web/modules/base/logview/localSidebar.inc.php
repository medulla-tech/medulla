<?php
/**
 *
 * (c) 2015-2022 Siveo, http://http://www.siveo.net
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
 * File : index.php
 */

/* Build log sidebar that aggregates all log viewers from all available modules */

$sidemenu= new SideMenu();
$sidemenu->setClass("logview");

$MMCApp =& MMCApp::getInstance();

$mod = $MMCApp->getModule("base");
$submod = $mod->getSubmod("logview");
 foreach ($submod->getPages() as $page) {
    if ($page->isVisible()){
       $sidemenu->addSideMenuItem(new SideMenuItem($page->getDescription(),      "base", "logview", $page->getAction()));
    }
}
    $p = new PageGenerator();
    $p->setSideMenu($sidemenu);
?>
