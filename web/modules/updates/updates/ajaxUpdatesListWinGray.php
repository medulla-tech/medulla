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

// Get Datas
$grey_list = xmlrpc_get_grey_list($start, $maxperpage, $filter);

// GrayList Actions
$grayEnableAction = new ActionItem(_T("Enable for manual update", "updates"), "grayEnable", "enableupdate", "", "updates", "updates");
$grayEnableEmptyAction = new EmptyActionItem1(_("Enable for manual update"), "grayEnable", "enableupdateg", "", "updates", "updates");
$grayDisableAction = new ActionPopupItem(_T("Disable for manual update", "updates"), "grayDisable", "disableupdate", "updates", "updates");
$grayDisableEmptyAction = new EmptyActionItem1(_T("Disable for manual update", "updates"), "grayDisable", "disableupdateg", "", "updates", "updates");
$grayApproveAction = new ActionPopupItem(_T("Approve for automatic update", "updates"), "grayApprove", "approveupdate", "updates", "updates");
$banAction = new ActionPopupItem(_T("Ban update", "updates"), "banUpdate", "banupdate", "updates", "updates");
$grayActions = [
    "enable" => [],
    "disable" => [],
    "approve" => [],
    "ban" => []
];
$params_grey = [];
$count_grey = $grey_list['nb_element_total'];
$count_partial = safeCount($grey_list['title']);

$kbs_gray = [];
$updateids_gray = [];
$titles_grey = [];

// ########## Boucle greyList ########## //
for($i = 0; $i < $count_partial; $i++) {
    $grayActions["enable"][] = ($grey_list['valided'][$i] == 0) ? $grayEnableAction : $grayEnableEmptyAction;
    $grayActions["disable"][] = ($grey_list['valided'][$i] == 1) ? $grayDisableAction : $grayDisableEmptyAction;
    $grayActions["approve"][] = $grayApproveAction;
    $grayActions["ban"][] = $banAction;

    $icon = ($grey_list['valided'][$i] == 1) ? '<img style="position:relative; top : 5px;" src="img/other/updateenabled.svg" width="25" height="25">' : '<img style="position:relative; top : 5px;" src="img/other/updatedisabled.svg" width="25" height="25">';
    $titles_grey[] = $icon.$grey_list['title'][$i];

    $params_grey[] = array(
        'updateid' => $grey_list['updateid'][$i],
        'title' => $grey_list['title'][$i],
        'severity' => $grey_list['severity'][$i]
    );
    if(strlen($grey_list['updateid'][$i]) < 10) {
        $kbs_gray[] = 'KB'.strtoupper($grey_list['updateid'][$i]);
        $updateids_gray[] = "";
    } else {
        $kbs_gray[] = "";
        $updateids_gray[] = "<a href=\"https://www.catalog.update.microsoft.com/Search.aspx?q='" . $grey_list['updateid'][$i] . "'\">" . $grey_list['updateid'][$i] . "</a>";
    }
}

// Add css ids to each tr tag in the table
foreach($grey_list['updateid'] as $updateid) {
    $ids [] = 'u_'.$updateid;
}
// ########## Affichage Tableau GreyList ########## //
$g = new OptimizedListInfos($titles_grey, _T("Update name", "updates"));

$g-> setCssIds($ids);
$g->disableFirstColumnActionLink();
$g->addExtraInfo($updateids_gray, _T("Update Id", "updates"));
$g->addExtraInfo($grey_list['severity'], _T("Severity", "updates"));
$g->setItemCount($count_grey);
$g->setNavBar(new AjaxNavBar($count_grey, $filter, 'updateSearchParamformGray'));
$g->setParamInfo($params_grey);
echo '<h2>'._T("Grey list (manual updates)", "updates").'</h2>';
$g->addActionItemArray($grayActions['enable']);
$g->addActionItemArray($grayActions['disable']);
$g->addActionItemArray($grayActions['approve']);
$g->addActionItemArray($grayActions['ban']);
$g->start = 0;
$g->end = $count_grey;
$g->display();
