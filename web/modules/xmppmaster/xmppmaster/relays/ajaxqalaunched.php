<?php
/*
 * (c) 2015-2020 siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

require_once("modules/xmppmaster/includes/xmlrpc.php");
global $config;

$jid = (isset($_GET['jid'])) ? $_GET['jid'] : '';
$start = (isset($_GET['start'])) ? $_GET['start'] : -1;
$maxperpage = (isset($_GET['maxperpage'])) ? $_GET['maxperpage'] : -1;

$list = xmlrpc_get_relay_qa_launched($jid, $_SESSION['login'], $start, $maxperpage);

$params = [];
$qaresultaction = new ActionItem(_("Show Result"), "qaresult", 'inventory', "", "xmppmaster", "xmppmaster");
$qaresultActions = [];

for($i=0;$i< count($list['datas']['id']); $i++){
  $params[] = [
    'command_cluster'=>$list['datas']['command_cluster'][$i],
    'execution_date'=>$list['datas']['command_start'][$i],
    'user_command'=>$list['datas']['user_command'][$i],
    'name'=>$list['datas']['name'][$i],
    'qa_relay_id'=>$list['datas']['id_command'][$i],
    'description'=>$list['datas']['description'][$i],
    'result_id'=>$list['datas']['result_id'][$i],
    'launched_id'=>$list['datas']['id'][$i],
    'command_relay'=>$list['datas']['command_relay'][$i]
  ];
  $qaresultActions[] = $qaresultaction;
}

$n = new OptimizedListInfos($list['datas']['name'], _T("Quick Action", "xmppmaster"));
$n->addExtraInfo($list['datas']['command_start'], _T("Description", "glpi"));
$n->addExtraInfo($list['datas']['description'], _T("Description", "glpi"));
$n->addActionItemArray($qaresultActions);
$n->setParamInfo($params);
$n->setNavBar(new AjaxNavBar($list['total'], $filter));
$n->start = 0;
$n->end = $list['total'];
$n->display();
?>
