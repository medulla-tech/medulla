<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
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
 */
require_once("modules/updates/includes/xmlrpc.php");

// Configuration global de $maxperpage, $filter, $start, $end
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

echo '<pre>';
// print_r($_GET);
echo '</pre>';
$white_list = xmlrpc_get_white_list($start, $end, $filter);
// WhiteList Actions
$whiteUnlistAction = new ActionPopupItem(_T("Unlist Update", "updates"), "whiteUnlist", "display", "updates", "updates");
$banAction = new ActionPopupItem(_T("Ban Update", "updates"), "banUpdate", "delete", "updates", "updates");
$whiteActions = [
    "unlist"=>[],
    "ban"=>[]
];
$params_white = [];
$count_white = $white_list['nb_element_total'];
$kbs_white = [];
$updateids_white = [];
$titles_white = [];
for($i=0; $i < $count_white; $i++){
    $tmp = [];
    $whiteActions["unlist"][] = $whiteUnlistAction;
    $whiteActions["ban"][] = $banAction;

    // $actiongreylistUpds[] = $greylistUpd;
    // $actionblacklistUpds[] = $blacklistUpd;

    $titles_white[] = $white_list['title'][$i];

    $tmp = array(
        'updateid' => $white_list['updateid'][$i],
        'title' => $white_list['title'][$i]
    );

    if(strlen($white_list['updateid'][$i]) < 10){
        $kbs_white[] = 'KB'.strtoupper($white_list['updateid'][$i]);
        $updateids_white[] = "";
        $tmp['kb'] = $white_list['updateid'][$i];
        $tmp['uid'] = "";
    }
    else{
        $kbs_white[] = "";
        $updateids_white[] = $white_list['updateid'][$i];
        $tmp['kb'] = "";
        $tmp['uid'] = $white_list['updateid'][$i];
    }
    $params_white[] = $tmp;
}

$w = new OptimizedListInfos($titles_white, _T("Update name", "updates"));
$w->disableFirstColumnActionLink();
$w->addExtraInfo($updateids_white, _T("Update Id", "updates"));
$w->addExtraInfo($kbs_white, _T("KB", "updates"));
$w->setItemCount($count_white);
$w->setNavBar(new AjaxNavBar($count_white, $filter, 'updateSearchParamformWhite'));
$w->setParamInfo($params_white);
echo '</br></br><h2> WhiteList</h2>';
$w->addActionItemArray($whiteActions["unlist"]);
$w->addActionItemArray($whiteActions["ban"]);
$w->display();