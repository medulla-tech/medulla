<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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

/* require_once("modules/ppolicy/includes/ppolicy-xmlrpc.php"); */
/* require_once("modules/ppolicy/includes/ppolicy.inc.php"); */

/**
 * ppolicy module declaration
 */

/* require_once("modules/admin/includes/admin.inc.php"); */
require_once("modules/admin/includes/commons.inc.php");

$mod = new Module("admin");
$mod->setVersion("3.1.0");
$mod->setRevision('$Rev$');
$mod->setDescription(_T("Configuration", "admin"));
$mod->setAPIVersion("4.1.3");
$mod->setPriority(600);

/* Add the page to the module */

$submod = new SubModule("configure");
$submod->setVisibility(True);
$submod->setDescription(_T("Administration"));
$submod->setDefaultPage("admin/configure/index");
$submod->setImg('img/navbar/load');
$mod->addSubmod($submod);

/* Add the (yet empty) module to the app */
$MMCApp = MMCApp::getInstance();
$MMCApp->addModule($mod);
unset($MMCApp);

/* Load all configuration page found in the "pages" directory, they will
 be added to the main submodule
*/
loadAllConfigurationPages();


?>
