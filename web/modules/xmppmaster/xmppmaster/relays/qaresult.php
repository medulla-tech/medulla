<?php
/*
 * (c) 2020 Siveo, http://www.siveo.net
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
 *
 */

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
$p = new PageGenerator(_T("Relay Quick Result Action", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();

$qa_relay_id = (isset($_GET['qa_relay_id'])) ? htmlentities($_GET['qa_relay_id']) : "";
$launched_id = (isset($_GET['launched_id'])) ? htmlentities($_GET['launched_id']) : "";
$execution_date = (isset($_GET['execution_date'])) ? htmlentities($_GET['execution_date']) : "";
$name = (isset($_GET['name'])) ? htmlentities($_GET['name']) : "";
$description = (isset($_GET['description'])) ? htmlentities($_GET['description']) : "";
$result_id = (isset($_GET['result_id'])) ? htmlentities($_GET['result_id']) : "";

$result = xmlrpc_get_qa_relay_result($result_id);

$jid = (isset($result['relay'])) ? htmlentities($result['relay']) : "";
$command_result = (isset($result['command_result'])) ? json_decode($result['command_result'], true) : "";
$cmd_result = ($command_result != "") ? $command_result['result'] : [];

$result_str = implode("\n", $cmd_result);


$list = new ListInfos([$jid], 'Relay');
$list->addExtraInfo([$execution_date], 'Execution Date');
$list->addExtraInfo([$name], 'Relay QA Name');
$list->addExtraInfo([$description], 'Relay QA Description');
$list->display();
echo '<textarea ';
echo 'spellcheck="false" style="';
echo 'height:400px; width:50%; margin-left:25%; background-color:black; color:rgb(230,230,230);font-size:1.2em;';
echo 'border-radius:15px; box-shadow: 0.5em 3px #0420263a, -0.75em 0 1em #00688054;';
echo '">';
echo $result_str.'</textarea>';

?>
