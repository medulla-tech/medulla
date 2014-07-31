<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

/**
 * dashboard module declaration
 */
require_once("modules/pulse2/version.php");

$mod = new Module("support");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Support", "support"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(500);

$submod = new SubModule("support", _T("Remote support", "support"));
$submod->setDefaultPage("support/support/index");
$submod->setVisibility(false);
$submod->setPriority(110);

$page = new Page("collect", _T("Collect", "support"));
$submod->addPage($page);
$page = new Page("connect", _T("Connect", "support"));
$submod->addPage($page);
$page = new Page("disconnect", _T("Disconnect", "support"));
$submod->addPage($page);
$page = new Page("get_file", _T("Download an archive including logs and config files", "support"));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp = & MMCApp::getInstance();
$MMCApp->addModule($mod);


?>
