<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxDetailsSpecificUpdateWithout.php
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");


global $conf;
$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$kb = (isset($_GET['kb'])) ? $_GET['kb'] : "";
$updateid = (isset($_GET['updateid'])) ? $_GET['updateid'] : "";
$maxperpage = $conf["global"]["maxperpage"];
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";

$without_Upd = xmlrpc_get_machines_needing_update($updateid, $location, $start, $maxperpage, $filter);

$machines = $without_Upd["datas"];
$total = $without_Upd["total"];

echo "<h2>"._T("Machines without update", "updates")."</h2>";
$n = new OptimizedListInfos($machines["name"], _T("Machine name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($machines["platform"], _T("Platform", "updates"));

$n->start=0;
$n->end = $total;
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, $filter, "updateSearchParamformWithout"));
$n->setEmptyState(_T("No machines found", "updates"), _T("No machines are missing this update.", "updates"));
$n->display();
