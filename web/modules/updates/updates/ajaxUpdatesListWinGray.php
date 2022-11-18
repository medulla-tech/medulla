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
// Appel de fonction pour récupérer la Liste Grise dans up_gray_list
$grey_list = xmlrpc_get_grey_list($start, $end, $filter);
// GrayList Actions
$grayEnableAction = new ActionItem(_T("Enable Update", "updates"),"grayEnable","quick","", "updates", "updates");
$grayDisableAction = new ActionPopupItem(_T("Disable Update", "updates"), "grayDisable", "display", "updates", "updates");
$grayApproveAction = new ActionPopupItem(_T("Approve Update", "updates"), "grayApprove", "edit", "updates", "updates");
$banAction = new ActionPopupItem(_T("Ban Update", "updates"), "banUpdate", "delete", "updates", "updates");
$grayActions = [
    "enable"=>[],
    "disable"=>[],
    "approve"=>[],
    "ban"=>[]
];
$params_grey = [];
$count_grey = $grey_list['nb_element_total'];

$kbs_gray = [];
$updateids_gray = [];
$titles_grey = [];
// ########## Boucle greyList ########## //
for($i=0; $i < $count_grey; $i++){
    $grayActions["enable"][] = $grayEnableAction;
    $grayActions["disable"][] = $grayDisableAction;
    $grayActions["approve"][] = $grayApproveAction;
    $grayActions["ban"][] = $banAction;


    // $actionwhitelistUpds[] = $whitelistUpd;

    // $actionblacklistUpds[] = $blacklistUpd;

    $titles_grey[] = $grey_list['title'][$i];

    $params_grey[] = array(
        'updateid' => $grey_list['updateid'][$i],
        'title' => $grey_list['title'][$i]
    );
    if(strlen($grey_list['updateid'][$i]) < 10){
        $kbs_gray[] = 'KB'.strtoupper($grey_list['updateid'][$i]);
        $updateids_gray[] = "";
    }
    else{
        $kbs_gray[] = "";
        $updateids_gray[] = $grey_list['updateid'][$i];
    }
}

// ########## Affichage Tableau GreyList ########## //
$g = new OptimizedListInfos($titles_grey, _T("Update name", "updates"));
$g->disableFirstColumnActionLink();
$g->addExtraInfo($updateids_gray, _T("Update Id", "updates"));
$g->addExtraInfo($kbs_gray, _T("KB", "updates"));
$g->setItemCount($count_grey);
$g->setNavBar(new AjaxNavBar($count_grey, $filter, 'updateSearchParamformGray'));
$g->setParamInfo($params_grey);
echo '<h2> GreyList</h2>';
$g->addActionItemArray($grayActions['enable']);
$g->addActionItemArray($grayActions['disable']);
$g->addActionItemArray($grayActions['approve']);
$g->addActionItemArray($grayActions['ban']);

$g->display();
?>