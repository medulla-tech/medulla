<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
// require_once("modules/pulse2/version.php");
// $mod = new Module("guacamole");
// $mod->setVersion(VERSION);
// $mod->setRevision(REVISION);
// $mod->setDescription(_T("guacamole", "guacamole"));
// $mod->setAPIVersion("0:0:0");
// // Create a glpi submodule only for guacamole Dashboard ACL
// $submod = new SubModule("guacamole");
// $submod->setDescription(_T("guacamole", "guacamole"));
// // hide this submodule from Web UI
// $submod->setVisibility(False);
// $page = new Page('guacamole_dashboard', _T('guacamole Dashboard', 'guacamole'));
// $submod->addPage($page);
// $mod->addSubmod($submod);
// $MMCApp =& MMCApp::getInstance();
// $MMCApp->addModule($mod);

require_once("modules/pulse2/version.php");

$mod = new Module("guacamole");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("guacamole", "guacamole"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(800);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
