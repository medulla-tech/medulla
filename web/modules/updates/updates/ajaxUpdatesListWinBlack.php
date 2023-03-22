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

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);
$black_list = xmlrpc_get_black_list($start, $maxperpage, $filter);

// BlackList Actions
$blackUnbanAction = new ActionItem(_T("unban Update", "updates"),"blackUnban","unlist","", "updates", "updates");
$blackActions = ["unban" =>[]];

$params_black = [];
$count_black = $black_list['nb_element_total'];
$kbs_black = [];
$updateids_black = [];
$titles_black = [];

// ########## Set params ########## //
for($i=0; $i < $count_black; $i++){
    $blackActions["unban"][] = $blackUnbanAction;

    $titles_black[] = $black_list['title'][$i];

    $params_black[] = array(
        'updateid' => $black_list['updateid_or_kb'][$i],
        'title' => $black_list['title'][$i],
        'id'=>$black_list['id'][$i]
    );

    if(strlen($black_list['updateid_or_kb'][$i]) < 10){
        $kbs_black[] = 'KB'.strtoupper($black_list['updateid_or_kb'][$i]);
        $updateids_black[] = "";
    }
    else{
        $kbs_black[] = "";
        $updateids_black[] = $black_list['updateid_or_kb'][$i];
    }
}

// ########## Display BlackList Table ########## //

$b = new OptimizedListInfos($titles_black, _T("Update name", "updates"));
$b->addExtraInfo($updateids_black, _T("Update Id", "updates"));
$b->addExtraInfo($kbs_black, _T("KB", "updates"));
$b->disableFirstColumnActionLink();
$b->setItemCount($count_black);
$b->setNavBar(new AjaxNavBar($count_black, $filter, 'updateSearchParamformBlack'));
$b->setItemCount($count_black);
$b->start = 0;
$b->end = $count_black;
$b->setParamInfo($params_black);
echo '</br></br><h2> Blacklisted updates</h2>';
$b->addActionItemArray($blackActions["unban"]);
$b->display();

?>
