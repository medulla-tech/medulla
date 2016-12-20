<?php
/**
 * (c) 2015-2016 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
require_once("modules/pulse2/version.php");

$mod = new Module("xmppmaster");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("xmppmaster", "xmppmaster"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(800);

$submod = new SubModule("xmppmaster");
$submod->setDescription(_T("XMPP Master", "xmppmaster"));

$submod->setVisibility(False);

$page = new Page("consolexmpp", _T('XMPP Console', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("deployxmpp", _T('XMPP Deploy', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("wakeonlan", _T('Wake on LAN', 'xmppmaster'));
$submod->addPage($page);

$page = new Page("ajaxdeploylog");
$page->setFile("modules/xmppmaster/xmppmaster/ajaxdeploylog.php");
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
