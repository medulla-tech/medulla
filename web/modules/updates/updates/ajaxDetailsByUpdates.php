<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxDetailsByUpdates.php
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");


global $conf;
// $p = new PageGenerator(_T("Details by Updates", 'updates'));
// $p->setSideMenu($sidemenu);
// $p->display();

$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$maxperpage = $conf["global"]["maxperpage"];
$gid = (isset($_GET['gid'])) ? $_GET['gid'] : "";
$contains = (isset($_GET['contains'])) ? $_GET['contains'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$filterCTX = "Microsoft";
$field = "platform";

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filterCTX;
$ctx['field'] = $field;
$ctx['contains'] = $contains;

$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

$uuid = htmlspecialchars($_GET['entity']);

$ctx['uuid'] = $uuid;

//$uuidCut = substr($uuid, -1);


$titles = [];
$complRates = [];
$machineWithUpd = [];
$machineWithoutUpd = [];
$count_enabled_updates = 0;
$params = [];

$enabled_updates_list = xmlrpc_get_enabled_updates_list($uuid, 'gray|white', $start, $maxperpage, $filter);

echo '<br>';
echo '<br>';
$count_enabled_updates = $enabled_updates_list['nb_element_total'];


if ($uuid == '') {
    $typeOfDetail = "group";
} else {
    $typeOfDetail = "entitie";
}

$detailsUpd = new ActionItem(_T("Details", "updates"), "detailsSpecificUpdate", "auditbymachine", "", "updates", "updates");
$actionHistory = new ActionItem(_T("History by Update", "updates"), "auditByUpdate", "history", "", "updates", "updates");

$kbs_gray = [];
$updateids_gray = [];
$titles = [];
$complRates = [];
$machineWithUpd = [];
$machineWithoutUpd = [];
$actionDetails = [];
$actionHistories = [];

$total = [];
$machineWithoutUpd = $enabled_updates_list['missing'];
$i = 0;
foreach($enabled_updates_list['kb'] as $kb) {
    $in_unique_with_Upd = "False";
    $in_unique_without_Upd = "False";

    $params[] = array('kb' => $kb, 'updateid' => $enabled_updates_list['updateid'][$i], 'location'=>$uuid);
    $with_Upd = xmlrpc_get_count_machine_with_update($kb, $uuid, $enabled_updates_list['history_list'][$i]);

    $total[] = $enabled_updates_list["total"];
    $titles[] = $enabled_updates_list['title'][$i];
    $actionDetails[] = $detailsUpd;
    $actionHistories[] = $actionHistory;
    $machineWithUpd[] = $with_Upd['nb_machines'] + $enabled_updates_list['installed'][$i];
    $totalMachines = $enabled_updates_list["total"];
    $compliance_rate = ($totalMachines > 0) ? round((($totalMachines-$machineWithoutUpd[$i]) / $totalMachines) * 100) : 100;

    $complRates[] = (string) new medulla_progressbar_static($compliance_rate, "", "");
    $i++;
}

$n = new OptimizedListInfos($titles, _T("Name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->addExtraInfoCentered($machineWithUpd, _T("Installed", "updates"));
$n->addExtraInfoCentered($machineWithoutUpd, _T("Requested", "updates"));
$n->addExtraInfoCentered($total, _T("Total machines", "updates"));

$n->setItemCount($count_enabled_updates);
$n->setNavBar(new AjaxNavBar($count_enabled_updates, $filter, 'updateSearchParamform'));
$n->setParamInfo($params);
$n->start = 0;
$n->end = $count_enabled_updates;
$n->addActionItemArray($actionHistories);
$n->addActionItemArray($actionDetails);
$n->setEmptyState(_T("No updates found", "updates"), _T("No updates match the current filter.", "updates"));
echo '<div class="details-by-updates">';
$n->display();
echo '</div>';
