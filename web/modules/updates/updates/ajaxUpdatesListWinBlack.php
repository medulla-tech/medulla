<?php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: ajaxUpdatesListWinBlack.php
 */
require_once("modules/updates/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$entityid   = (isset($_GET['uuid']) ? $_GET['uuid']  : -1 );

$black_list = xmlrpc_get_black_list( $start, $maxperpage, $filter, $entityid);

// BlackList Actions
$blackUnbanAction = new ActionItem(_T("Unban update", "updates"), "blackUnban", "unlist", "", "updates", "updates");
$blackActions = ["unban" => []];

$params_black = [];
$count_black = $black_list['nb_element_total'];
$kbs_black = [];
$updateids_black = [];
$titles_black = [];
$count = count($black_list['title']);

// ########## Set params ########## //
for($i = 0; $i < $count; $i++) {
    $blackActions["unban"][] = $blackUnbanAction;

    $titles_black[] = $black_list['title'][$i];

    $params_black[] = array(
        'updateid' => $black_list['updateid_or_kb'][$i],
        'title' => $black_list['title'][$i],
        'id' => $black_list['id'][$i],
        "severity" => $black_list['severity'][$i],
        'entityid' => $entityid,
        'name' => $_GET['name'],
        'completename' => $_GET['completename'],
        'comments' => $_GET['comments'],
        'level' => $_GET['level'],
        'altname' => $_GET['altname']
    );

    if(strlen($black_list['updateid_or_kb'][$i]) < 10) {
        $kbs_black[] = 'KB'.strtoupper($black_list['updateid_or_kb'][$i]);
        $updateids_black[] = "";
    } else {
        $kbs_black[] = "";
        $updateids_black[] = "<a href=\"https://www.catalog.update.microsoft.com/Search.aspx?q='" . $black_list['updateid_or_kb'][$i] .'" target="_blank">' . $black_list['updateid_or_kb'][$i] . "</a>";
    }
}
$ids = array(); // Initialize the array
// ########## Display BlackList Table ########## //
// Add css ids to each tr tag in the table
foreach($black_list['updateid_or_kb'] as $updateid) {
    $ids [] = 'b_'.$updateid;
}
$b = new OptimizedListInfos($titles_black, _T("Update name", "updates"));
$b->setCssIds($ids);
$b->addExtraInfo($updateids_black, _T("Update Id", "updates"));
$b->addExtraInfo($black_list['severity'], _T("Severity", "updates"));
$b->disableFirstColumnActionLink();
$b->setItemCount($count_black);
$b->setNavBar(new AjaxNavBar($count_black, $filter, 'updateSearchParamformBlack'));
$b->setItemCount($count_black);
$b->start = 0;
$b->end = $count_black;
$b->setParamInfo($params_black);

// affichage titre tableau
$converter = new ConvertCouleur();

if ($black_list['nb_element_total'] == "0")
{
$titretableau = _T("No updates are currently available in the Black list (banned updates)", 'updates');
}else{
$titretableau = _T("Black list (banned updates)", 'updates');
}

// $completename = $_GET['completename'];
$completename = $_GET['altname'];

$ide = $_GET['uuid'];
$b->setCaptionText(sprintf("%s",
                           $titretableau));

$b->setCssCaption(
    $border = 1,
    $bold = 0,
    $bgColor = "lightgray",
    $textColor = "black",
    $padding = "10px 0",
    $size = "20",
    $emboss = 1,
    $rowColor = $converter->convert("lightgray")
);

$b->addActionItemArray($blackActions["unban"]);
$b->display();
