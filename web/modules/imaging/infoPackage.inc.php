<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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


/**
 * module declaration
 */

$mod = new Module("imaging");
$mod->setVersion("1.0.0");
$mod->setRevision("$Rev$");
$mod->setDescription(_T("Imaging service","imaging"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(600);

$submod = new SubModule("publicimages");
$submod->setDescription(_T("Public Images", "publicimages"));
$submod->setImg("modules/imaging/graph/img/imaging");
$submod->setDefaultPage("imaging/publicimages/index");

$page = new Page("index",_T("List public images","imaging"));
$submod->addPage($page);

$page = new Page("ajaxImages");
$page->setFile("modules/imaging/publicimages/ajaxImages.php", array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("delete");
$page->setFile("modules/imaging/publicimages/delete.php", array( "visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("copy");
$page->setFile("modules/imaging/publicimages/copy.php", array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("edit");
$page->setFile("modules/imaging/publicimages/edit.php", array("visible" => False));
$submod->addPage($page);

$page = new Page("view");
$page->setFile("modules/imaging/publicimages/view.php", array("visible" => False));
$submod->addPage($page);

$page = new Page("mkiso");
$page->setFile("modules/imaging/publicimages/mkiso.php", array( "visible" => False, "noHeader" => True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
