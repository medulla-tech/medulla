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

// Global config for $maxperpage
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);


// == Get gray, white and black lists ==
$grey_list = xmlrpc_get_grey_list($start, $end, $filter);
$white_list = xmlrpc_get_white_list($start, $end, $filter);
$black_list = xmlrpc_get_black_list($start, $end, $filter);

// == Declare actions for the lists ==
// GrayList Actions
$grayEnableAction = new ActionItem(_T("Enable Update", "updates"),"grayEnable","quick","", "updates", "updates");
$grayDisableAction = new ActionPopupItem(_T("Disable Update", "updates"), "grayDisable", "display", "updates", "updates");
$grayApproveAction = new ActionPopupItem(_T("Approve Update", "updates"), "grayApprove", "edit", "updates", "updates");

// WhiteList Actions
$whiteUnlistAction = new ActionPopupItem(_T("Unlist Update", "updates"), "whiteUnlist", "display", "updates", "updates");
$banAction = new ActionPopupItem(_T("Ban Update", "updates"), "banUpdate", "delete", "updates", "updates");

// BlackList Actions
$blackUnbanAction = new ActionItem(_T("unban Update", "updates"),"blackUnban","quick","", "updates", "updates");

// Actions wrapper
$whiteActions = [
    "unlist"=>[],
    "ban"=>[]
];
$grayActions = [
    "enable"=>[],
    "disable"=>[],
    "approve"=>[],
    "ban"=>[]
];
$blackActions = ["unban" =>[]];

// Declare Params wrappers for the 3 tables
$params_grey = [];
$params_white = [];
$params_black = [];


// get updates counts
$count_grey = $grey_list['nb_element_total'];
$count_white = $white_list['nb_element_total'];
$count_black = $black_list['nb_element_total'];

// Declare some additionnals columns
$kbs_white = [];
$kbs_gray = [];
$kbs_black = [];

$updateids_white = [];
$updateids_gray = [];
$updateids_black = [];

$titles_white = [];
$titles_grey = [];
$titles_black = [];

// ########## greyList ########## //
for($i=0; $i < $count_grey; $i++){
    $grayActions["enable"][] = $grayEnableAction;
    $grayActions["disable"][] = $grayDisableAction;
    $grayActions["approve"][] = $grayApproveAction;
    $grayActions["ban"][] = $banAction;

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

// ########## whiteList ########## //
for($i=0; $i < $count_white; $i++){
    $tmp = [];
    $whiteActions["unlist"][] = $whiteUnlistAction;
    $whiteActions["ban"][] = $banAction;

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

// ########## blackList ########## //
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

// ########## GreyList Table ########## //
$g = new OptimizedListInfos($titles_grey, _T("Update name", "updates"));
$g->disableFirstColumnActionLink();
$g->addExtraInfo($updateids_gray, _T("Update Id", "updates"));
$g->addExtraInfo($kbs_gray, _T("KB", "updates"));
$g->setItemCount($count_grey);
$g->setNavBar(new AjaxNavBar($count_grey, $filter));
$g->setParamInfo($params_grey);
echo '<h2> GreyList</h2>';
$g->addActionItemArray($grayActions['enable']);
$g->addActionItemArray($grayActions['disable']);
$g->addActionItemArray($grayActions['approve']);
$g->addActionItemArray($grayActions['ban']);

$g->display();


// ########## WhiteList Table ########## //
$w = new OptimizedListInfos($titles_white, _T("Update name", "updates"));
$w->disableFirstColumnActionLink();
$w->addExtraInfo($updateids_white, _T("Update Id", "updates"));
$w->addExtraInfo($kbs_white, _T("KB", "updates"));
$w->setItemCount($count_white);
$w->setNavBar(new AjaxNavBar($count_white, $filter));
$w->setParamInfo($params_white);
echo '</br></br><h2> WhiteList</h2>';
$w->addActionItemArray($whiteActions["unlist"]);
$w->addActionItemArray($whiteActions["ban"]);
$w->display();

// ########## BlackList Table ########## //

$b = new OptimizedListInfos($titles_black, _T("Update name", "updates"));
$b->addExtraInfo($updateids_black, _T("Update Id", "updates"));
$b->addExtraInfo($kbs_black, _T("KB", "updates"));
$b->disableFirstColumnActionLink();
$b->setItemCount($count_black);
$b->setNavBar(new AjaxNavBar($count_black, $filter));
$b->setParamInfo($params_black);
echo '</br></br><h2> BlackList</h2>';
$b->addActionItemArray($blackActions["unban"]);
$b->display();


?>
