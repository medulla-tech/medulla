<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMajorDetailsByMachinesLinux.php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 * file: modules/updates/updates/ajaxMajorDetailsByMachinesLinux.php
 */

require_once("modules/updates/includes/xmlrpc.php");


global $conf;
$maxperpage = isset($conf["global"]["maxperpage"]) ? (int)$conf["global"]["maxperpage"] : 50;

$start = (isset($_GET['start']) && is_numeric($_GET['start'])) ? (int)$_GET['start'] : 0;
$filter = isset($_GET['filter']) ? trim((string)$_GET['filter']) : "";

$entityId = isset($_GET['entity_id']) ? (int)$_GET['entity_id'] : (isset($_GET['entity']) ? (int)$_GET['entity'] : 0);
$entityName = !empty($_GET['entity_name']) ? htmlentities($_GET['entity_name']) : (!empty($_GET['name']) ? htmlentities($_GET['name']) : "");
$entityCompleteName = !empty($_GET['complete_name']) ? htmlentities($_GET['complete_name']) : (!empty($_GET['completename']) ? htmlentities($_GET['completename']) : $entityName);
$distribution = !empty($_GET['distributor_id']) ? htmlentities($_GET['distributor_id']) : (!empty($_GET['distribution']) ? htmlentities($_GET['distribution']) : "");
$targetVersion = !empty($_GET['max_version']) ? htmlentities($_GET['max_version']) : "";

if ($entityId < 0 || $distribution === "") {
    new NotifyWidgetFailure(_T("Missing parameters to load Linux major upgrade details.", "updates"));
    // Continue to display page with empty results
}



$candidates = xmlrpc_get_linux_upgrade_candidates($distribution, $entityId, $targetVersion);
if (!is_array($candidates)) {
    $candidates = array();
}

// La cible peut être résolue côté backend (colonne target_version).
$resolvedTargetVersion = $targetVersion;
if ($resolvedTargetVersion === "" && !empty($candidates)) {
    foreach ($candidates as $candidate) {
        if (!empty($candidate['target_version'])) {
            $resolvedTargetVersion = (string)$candidate['target_version'];
            break;
        }
    }
}
if ($resolvedTargetVersion === "") {
    $resolvedTargetVersion = "N/A";
}

$filteredCandidates = array();
foreach ($candidates as $candidate) {
    $hostname = isset($candidate['hostname']) ? (string)$candidate['hostname'] : "";
    if ($filter !== "" && stripos($hostname, $filter) === false) {
        continue;
    }
    $filteredCandidates[] = $candidate;
}

$totalFiltered = count($filteredCandidates);
$pagedCandidates = array_slice($filteredCandidates, $start, $maxperpage);

$n = new ListInfos(array($totalFiltered), _T("Machines to be upgraded", "updates"));
$n->addExtraInfo(array($distribution), _T("Distribution", "updates"));
$n->addExtraInfo(array($resolvedTargetVersion), sprintf(_T("Latest %s version", "updates"), ucfirst($distribution)));
$n->setNavBar("");
$n->start = 0;
$n->end = 1;
$n->disableFirstColumnActionLink();
$n->display(0, 0);

$upgradeAction = new ActionPopupItem(
    _T("Upgrade", "updates"),
    "grpDeployUpdateLinuxMajor",
    "updateone",
    "",
    "updates",
    "updates",
    null,
    320,
    "machine"
);

$emptyUpgradeAction = new EmptyActionItem1(
    _T("Upgrade unavailable", "updates"),
    "grpDeployUpdateLinuxMajor",
    "updateoneg",
    "",
    "updates",
    "updates"
);

$machineNames = array();
$currentVersions = array();
$targetVersions = array();
$upgradeActions = array();
$params = array();

foreach ($pagedCandidates as $candidate) {
    $hostname = isset($candidate['hostname']) ? (string)$candidate['hostname'] : "";
    if ($hostname === "") {
        $hostname = isset($candidate['harduuid']) ? (string)$candidate['harduuid'] : _T("Unknown machine", "updates");
    }

    $releaseVersion = isset($candidate['release_version']) ? (string)$candidate['release_version'] : "";
    $uuidInventory = isset($candidate['uuid_inventorymachine']) ? trim((string)$candidate['uuid_inventorymachine']) : "";
    if ($uuidInventory === "" && !empty($candidate['harduuid'])) {
        $uuidInventory = "UUID" . trim((string)$candidate['harduuid']);
    }

    $machineNames[] = $hostname;
    $currentVersions[] = $releaseVersion;
    $targetVersions[] = $resolvedTargetVersion;

    if ($uuidInventory !== "") {
        $upgradeActions[] = $upgradeAction;
    } else {
        $upgradeActions[] = $emptyUpgradeAction;
    }

    $params[] = array(
        'entity_id' => $entityId,
        'entity_name' => $entityName,
        'complete_name' => $entityCompleteName,
        'distributor_id' => $distribution,
        'distribution' => $distribution,
        'release_version' => $releaseVersion,
        'max_version' => $resolvedTargetVersion,
        'cn' => $hostname,
        'uuid_inventorymachine' => $uuidInventory,
    );
}

$list = new OptimizedListInfos($machineNames, _T("Machine name", "updates"));
$list->disableFirstColumnActionLink();
$list->addExtraInfoCentered($currentVersions, _T("Current version", "updates"));
$list->addExtraInfoCentered($targetVersions, _T("Target version", "updates"));
$list->addActionItemArray($upgradeActions);
$list->setItemCount($totalFiltered);
$list->setNavBar(new AjaxNavBar($totalFiltered, $filter));
$list->setParamInfo($params);
$list->setEmptyState(_T("No machines found", "updates"), _T("No Linux machines match the current filter.", "updates"));
$list->start = $start;
$list->end = $start + count($machineNames);
$list->display();

?>