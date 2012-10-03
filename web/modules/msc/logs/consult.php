<?

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

require("modules/msc/logs/localSidebar.php");
require("graph/navbar.inc.php");

require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/command_history.php');
require_once('modules/msc/includes/functions.php');
require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

$p = new PageGenerator(_T("Consolidated view", 'msc'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilterCommands(urlStrRedirect("msc/logs/ajaxConsultLogsFilter"));
$ajax->setRefresh(web_def_refresh_time());
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();


?>

