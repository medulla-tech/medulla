<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);

global $type;
if ($_GET['action'] == 'computersprofilecreator') { $type = 1; } else { $type = 0; }

if ($type == 0) {
    $p->addTop(sprintf(_T("Group creation", "dyngroup"), $_GET['name']), "modules/dyngroup/dyngroup/header.php");
    $p->addTab("tabdyn", _T("Dynamic group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/creator.php", array('type'=>$type));
    $p->addTab("tabsta", _T("Static group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/add_groups.php", array('type'=>$type));
    $p->addTab("tabfromfile", _T("Static group creation from import", "dyngroup"), "", "modules/dyngroup/dyngroup/import_from_file.php", array('type'=>$type));
} else {
    $p->addTop(sprintf(_T("Profile creation", "dyngroup"), $_GET['name']), "modules/dyngroup/dyngroup/header.php");
    $p->addTab("tabdyn", _T("Result profile creation", "dyngroup"), "", "modules/dyngroup/dyngroup/creator.php", array('type'=>$type));
    $p->addTab("tabsta", _T("Static profile creation", "dyngroup"), "", "modules/dyngroup/dyngroup/add_groups.php", array('type'=>$type));
    $p->addTab("tabfromfile", _T("Static profile creation from import", "dyngroup"), "", "modules/dyngroup/dyngroup/import_from_file.php", array('type'=>$type));
}
$p->display();

?>

