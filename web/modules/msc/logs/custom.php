<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("modules/msc/logs/localSidebar.php");
require("graph/navbar.inc.php");

require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/command_history.php');
require_once('modules/msc/includes/functions.php');
require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

$p = new PageGenerator(_T("Show custom status task's logs", 'msc'));
$p->setSideMenu($sidemenu);
$p->display();

$params = array("type"=>-1, "from"=>"custom");

$ajax = new AjaxFilterCommandsStates(urlStrRedirect("msc/logs/ajaxLogsFilter"), "container", "commands", "currentstate", $params);

$res = get_all_commandsonhost_currentstate(); 
$list = array();
$labels = array();
foreach ($res as $name) {
    $labels[$name] = _T(preg_replace("[_]", ' ', ucfirst($name)), 'msc');
    $list[$name] = $name;
}
$ajax->setElements($labels);
$ajax->setElementsVal($list);

$ajax->setRefresh(web_def_refresh_time());
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();



?>

