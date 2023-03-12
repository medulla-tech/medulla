<?php
/*
 * (c) 2015-2020 Siveo, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/monitoring/monconfig.php
 */


require("graph/navbar.inc.php");
require("modules/base/computers/localSidebar.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once("modules/pulse2/includes/utilities.php");

$p = new PageGenerator(_T("Monitoring Configurator", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();

$file = "/var/lib/pulse2/xmpp_monitoring/confagent/monitoring_config.ini";
$name = "mon_conf";


$editor = new Editor($file, $name, $name, $css=[], $scripts=[], $mode='out', $language='ini');
$ajax = urlStrRedirect("xmppmaster/xmppmaster/ajaxmonconfig");
$editor->setAjax($ajax);

//If the path and file doesn't exist, both are created
if(!$editor->dir_exists()){
  $editor->create_dir();
}

if(!$editor->file_exists()){
  $editor->create_file();
}

$content = $editor->get_content();
//$editor->setFontSize(8);
$editor->display();
?>
