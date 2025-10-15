<?php
/**
 * (c) 2022-2023 Siveo, http://siveo.net/
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
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$entityid   = (isset($_GET['uuid']) ? $_GET['uuid']  : -1 );

$white_list = xmlrpc_get_white_list($start, $maxperpage, $filter, $entityid);
// WhiteList Actions
$whiteUnlistAction = new ActionPopupItem(_T("Unlist update", "updates"), "whiteUnlist", "unlist", "updates", "updates");
$banAction = new ActionPopupItem(_T("Ban update", "updates"), "banUpdate", "banupdate", "updates", "updates");
$whiteActions = [
    "unlist" => [],
    "ban" => []
];
$params_white = [];
$count_white = $white_list['nb_element_total'];
$kbs_white = [];
$updateids_white = [];
$titles_white = [];
for($i = 0; $i < $count_white; $i++) {
    $tmp = [];
    $whiteActions["unlist"][] = $whiteUnlistAction;
    $whiteActions["ban"][] = $banAction;

    $titles_white[] = $white_list['title'][$i];

    $tmp = array(
        'updateid' => $white_list['updateid'][$i],
        'title' => $white_list['title'][$i],
        'severity' => $white_list['severity'][$i],
        'entityid' => $entityid,
        'name' => $_GET['name'],
        'completename' => $_GET['completename'],
        'comments' => $_GET['comments'],
        'level' => $_GET['level'],
        'altname' => $_GET['altname']
    );

    if(strlen($white_list['updateid'][$i]) < 10) {
        $kbs_white[] = 'KB'.strtoupper($white_list['updateid'][$i]);
        $updateids_white[] = "";
        $tmp['kb'] = $white_list['updateid'][$i];
        $tmp['uid'] = "";
    } else {
        $kbs_white[] = "";
        $updateids_white[] = "<a href=\"https://www.catalog.update.microsoft.com/Search.aspx?q='" . $white_list['updateid'][$i] .'" target="_blank">' . $white_list['updateid'][$i] . "</a>";
        $tmp['kb'] = "";
        $tmp['uid'] = $white_list['updateid'][$i];
    }
    $params_white[] = $tmp;
}
$ids = array(); // Initialize the array
// Add css ids to each tr tag in the table
foreach($white_list['updateid'] as $updateid) {
    $ids [] = 'w_'.$updateid;
}

$w = new OptimizedListInfos($titles_white, _T("Update name", "updates"));
$w->setCssIds($ids);
$w->disableFirstColumnActionLink();
$w->addExtraInfo($updateids_white, _T("Update Id", "updates"));
$w->addExtraInfo($white_list['severity'], _T("Severity", "updates"));
// $w->addExtraInfo($kbs_white, _T("KB", "updates"));
$w->setItemCount($count_white);
$w->setNavBar(new AjaxNavBar($count_white, $filter, 'updateSearchParamformWhite'));
$w->start = 0;
$w->end = $count_white;
$w->setParamInfo($params_white);
// affichage titre tableau
$converter = new ConvertCouleur();

if ($count_white == 0)
{
    $titretableau = _T("No updates are currently available in the White list (automatic updates)", 'updates');
}else{
    $titretableau = _T("White list (automatic updates)", 'updates');
}

// $completename = $_GET['completename'];
$completename = $_GET['altname'];

// Remplace les "+" par un espace
$completename_cleaned = str_replace('+', ' ', $completename);
// Remplace ">" par " → "
$completename_cleaned = str_replace('>', ' → ', $completename_cleaned);
// Remplace les "&nbsp;" par un espace
$completename_cleaned = str_replace('&nbsp;', ' ', $completename_cleaned);
// Supprime les espaces multiples
$completename_cleaned = preg_replace('/\s+/', ' ', $completename_cleaned);
// Supprime les espaces en début et fin de chaîne
$completename_cleaned = trim($completename_cleaned);
$ide = $_GET['uuid'];
$w->setCaptionText(sprintf("%s [%s] (%s)",
                           $titretableau ,
                           $completename_cleaned,
                           $ide));
$w->setCssCaption(
    $border = 1,
    $bold = 0,
    $bgColor = "lightgray",
    $textColor = "black",
    $padding = "10px 0",
    $size = "20",
    $emboss = 1,
    $rowColor = $converter->convert("lightgray")
);
$w->addActionItemArray($whiteActions["unlist"]);
$w->addActionItemArray($whiteActions["ban"]);
$w->display();
