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

// ###################################################################################### //
// ########### !!! PENSER A CHANGER I OU J POUR METTRE DE VRAI VARIABLE !!! ############# //
// ###################################################################################### //

// Global configuration of $maxperpage, $filter, $start, $end
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

// Appel de fonction pour recuperer la Liste Grise dans up_gray_list
$grey_list = xmlrpc_get_grey_list($start, $end, $filter);
// Appel de fonction pour recuperer la Liste Grise dans up_gray_list ou valided = 1
$walter_white = xmlrpc_get_white_list($start, $end, $filter);
// Appel de fonction pour recuperer la Liste Grise dans up_black_list
$black_list = xmlrpc_get_black_list($start, $end, $filter);

echo "<pre>";
//print_r($grey_list);
echo "</pre>";

// The action items for moving updates between lists
$greylistUpd = new ActionPopupItem(_T("Unlist Update", "updates"), "greylistUpdate", "unlist", "updates", "updates");
$whitelistUpd = new ActionPopupItem(_T("Approve Update", "updates"), "whitelistUpdate", "approveupdate", "updates", "updates");
$blacklistUpd = new ActionItem(_T("Ban Update", "updates"), "blacklistUpdate", "banupdate", "", "updates", "updates");
$unBan = new ActionPopupItem(_T("Unban Update", "updates"), "deleteRule", "unlist","", "updates", "updates");

// Initialisation of the arrays that will contain the parameters of each table
$params_grey = [];
$params_white = [];
$params_black = [];
$params_unBan = [];

// Initialisation of the arrays that will hold the actions
$actiongreylistUpds = [];
$actionwhitelistUpds = [];
$actionblacklistUpds = [];
$actionunBan = [];

// Counters for each list
$count_grey = $grey_list['nb_element_total'];
$count_white = $walter_white['nb_element_total'];
$count_black = $black_list['nb_element_total'];

// ########## Greylist loop ########## //
for($i=0; $i < $count_grey; $i++){
    $actionwhitelistUpds[] = $whitelistUpd;
    $actionblacklistUpds[] = $blacklistUpd;

    $title_grey[] = $grey_list['title'][$i];

    $params_grey[] = array('updateid' => $grey_list['updateid'][$i]);
}

// ########## whiteList loop ########## //
for($i=0; $i < $count_white; $i++){
    $actiongreylistUpds[] = $greylistUpd;
    $actionblacklistUpds[] = $blacklistUpd;

    $title_white[] = $walter_white['title'][$i];

    $params_white[] = array('updateid' => $walter_white['updateid'][$i]);
}

// ########## blackList loop ########## //
for($i=0; $i < $count_black; $i++){
    // $actiongreylistUpds[] = $greylistUpd;
    // $actionwhitelistUpds[] = $whitelistUpd;
    $actionunBan[] = $unBan;

    $title_black[] = $black_list['title'][$i];

    $params_black[] = array('updateid' => $black_list['updateid'][$i]);
    $params_unBan[] = array('updateid' => $black_list['updateid_or_kb'][$i]);
}

// ########## Greylist table ########## //
$g = new OptimizedListInfos($title_grey, _T("Update name", "updates"));
$g->disableFirstColumnActionLink();
$g->addExtraInfo($id, _T("Updateid", "updates"));
$g->setItemCount($count_grey);
$g->setNavBar(new AjaxNavBar($count_grey, $filter));
$g->setParamInfo($params_grey);
echo '<h2> GreyList</h2>';
$g->addActionItemArray($actionwhitelistUpds);

// ##### C'est ce bouton qui m'interesse ###### //
$g->addActionItemArray($actionblacklistUpds);
$g->display();

// ########## Whitelist table ########## //
$w = new OptimizedListInfos($title_white, _T("Update name", "updates"));
$w->disableFirstColumnActionLink();
$w->setItemCount($count_white);
$w->setNavBar(new AjaxNavBar($count_white, $filter));
$w->setParamInfo($params_white);
echo '</br></br><h2> WhiteList</h2>';
$w->addActionItemArray($actiongreylistUpds);
$w->addActionItemArray($actionblacklistUpds);
$w->display();

// ########## BlackList table ########## //
$b = new OptimizedListInfos($title_black, _T("Update name", "updates"));
$b->disableFirstColumnActionLink();
$b->setItemCount($count_black);
$b->setNavBar(new AjaxNavBar($count_black, $filter));
$b->setParamInfo($params_unBan);
echo '</br></br><h2> BlackList</h2>';
// $b->addActionItemArray($actionwhitelistUpds);
// $b->addActionItemArray($actiongreylistUpds);
$b->addActionItemArray($actionunBan);
$b->display();



// ##################################################### //
// ############ EX MODAL SUPPRESSION ################## //
// $f = new PopupForm(_T("Delete this package"));
// $hidden = new HiddenTpl("packageUuid");
// $f->add($hidden, array("value" =>$uuid, "hide" => True));
// $hidden = new HiddenTpl("p_api");
// $f->add($hidden, array("value" => $p_api, "hide" => True));
// $hidden = new HiddenTpl("pid");
// $f->add($hidden, array("value" => $pid, "hide" => True));
// $f->add(new HiddenTpl("from"), array("value" => $from, "hide" => True));
// $f->addValidateButton("bconfirm");
// $f->addCancelButton("bback");

// ##### Lien genere dans /usr/share/mmc/modules/pkgs/pkgs/ajaxPackageList.php ##### //
// <a title="Supprimer un package" href="main.php?module=pkgs&amp;submod=pkgs&amp;action=delete&amp;pid=YTYxN2IwNGEtdGVzdGpma196Ynk1dm1jOWhtdXl1Zmprb2oz&amp;packageUuid=a617b04a-testjfk_zby5vmc9hmuyufjkoj3&amp;permission=rw&amp;mod=" onclick="PopupWindow(event,'main.php?module=pkgs&amp;submod=pkgs&amp;action=delete&amp;pid=YTYxN2IwNGEtdGVzdGpma196Ynk1dm1jOWhtdXl1Zmprb2oz&amp;packageUuid=a617b04a-testjfk_zby5vmc9hmuyufjkoj3&amp;permission=rw&amp;mod=', 300); return false;">&nbsp;</a>

// ##### CE QUE JE GENERE COMME LIEN ##### //
// <a title="Ban Update" href="main.php?module=updates&amp;submod=updates&amp;action=blacklistUpdate&amp;updateid=01f7dc80-5870-4a79-bb59-fe9071e01405&amp;permission=test&amp;mod=">&nbsp;</a>

?>
