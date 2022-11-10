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

//////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////// Tableau Grey List //////////////////////////////////////////
$grey_list = xmlrpc_get_grey_list($start, $end, $filter);

echo "<pre>";
//print_r($grey_list);
echo "</pre>";

$greylistUpd = new ActionItem(_T("Unlist Update", "updates"), "greylistUpdate", "unlist", "", "updates", "updates");
$whitelistUpd = new ActionItem(_T("Approve Update", "updates"), "whitelistUpdate", "approveupdate", "", "updates", "updates");
$blacklistUpd = new ActionItem(_T("Ban Update", "updates"), "blacklistUpdate" ,"banupdate", "", "updates", "updates");

$params_grey = [];
$params_white = [];
$params_black = [];
$actiongreylistUpds = [];
$actionblacklistUpds = [];
$actionwhitelistUpds = [];
$actionunlistUpds= [];
$names = [];
$count = $grey_list['nb_element_total'];

foreach ($grey_list['title'] as $list) {
    $actionwhitelistUpds[] = $whitelistUpd;
    $actionblacklistUpds[] = $blacklistUpd;
    
    $names_grey[] = $list;
}

for($i=0; $i< count($grey_list['updateid']); $i++){
    $title[] = $grey_list['title'][$i];
    $params_grey[] = array('updateid' => $grey_list['updateid'][$i]);
}


$g = new OptimizedListInfos($names_grey, _T("Update name", "updates"));
$g->disableFirstColumnActionLink();
$g->addExtraInfo($id, _T("Updateid", "updates"));

$g->setItemCount($count);
$g->setNavBar(new AjaxNavBar($count, $filter));
$g->setParamInfo($params_grey);

echo '<h2> GreyList</h2>';

$g->addActionItemArray($actionwhitelistUpds);
$g->addActionItemArray($actionblacklistUpds);

$g->display();


//////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////// Tableau White List //////////////////////////////////////////
$walter_white = xmlrpc_get_white_list($start, $end, $filter);
// echo "<pre>";
// print_r($walter_white);
// echo "</pre>";

$count_white = $white_list['nb_element_total'];

foreach ($walter_white['title'] as $list) {
    $actiongreylistUpds[] = $greylistUpd;
    $actionblacklistUpds[] = $blacklistUpd;
    
    $names_white[] = $list;
}

for($i=0; $i< count($walter_white['updateid']); $i++){
    $title[] = $grey_list['title'][$i];
    $params_white[] = array('updateid' => $walter_white['updateid'][$i]);
}

// Création et affichage du tableau White List avec pour le moment les donnée de la table up_grey_list
$w = new OptimizedListInfos($names_white, _T("Update name", "updates"));
$w->disableFirstColumnActionLink();
$w->setItemCount($count_white);
$w->setNavBar(new AjaxNavBar($count_white, $filter));
$w->setParamInfo($params_white);

echo '</br></br><h2> WhiteList</h2>';

$w->addActionItemArray($actiongreylistUpds);
$w->addActionItemArray($actionblacklistUpds);

$w->display();


//////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////// Tableau Black List //////////////////////////////////////////
$black_list = xmlrpc_get_black_list($start, $end, $filter);
echo "<pre>";
// print_r($black_list);
echo "</pre>";

$count_black = $black_list['nb_element_total'];

foreach ($black_list['title'] as $list) {
    $actiongreylistUpds[] = $greylistUpd;
    $actionwhitelistUpds[] = $whitelistUpd;
    
    $names_black[] = $list;
}

for($i=0; $i< count($black_list['updateid']); $i++){
    $title[] = $grey_list['title'][$i];
    $params_black[] = array('updateid' => $black_list['updateid'][$i]);
}

// Création et affichage du tableau Black List avec pour le moment les donnée de la table up_grey_list
$b = new OptimizedListInfos($names_black, _T("Update name", "updates"));
$b->disableFirstColumnActionLink();
$b->setItemCount($count_black);
$b->setNavBar(new AjaxNavBar($count_black, $filter));
$b->setParamInfo($params_black);

echo '</br></br><h2> BlackList</h2>';

$b->addActionItemArray($actionwhitelistUpds);
$b->addActionItemArray($actiongreylistUpds);

$b->display();
?>
