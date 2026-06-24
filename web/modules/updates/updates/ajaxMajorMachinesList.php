<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMajorMachinesList.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");


global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// ------------------------------------------------------------------
// Paramètres d'entrée
// ------------------------------------------------------------------
$distribution = isset($_GET['distribution']) ? strtolower(trim($_GET['distribution'])) : "debian";
$entityuuid   = isset($_GET['entity'])       ? $_GET['entity']                          : "UUID0";
$filter       = isset($_GET['filter'])       ? $_GET['filter']                          : "";
$start        = isset($_GET['start'])        ? (int) $_GET['start']                     : 0;
$end          = isset($_GET['end'])          ? (int) $_GET['end']                       : $start + $maxperpage - 1;
$limit        = $start === -1 ? -1 : ($end - $start + 1);

// Extrait l'id numérique de l'entité (ex: "UUID42" → 42)
$entity_id = (int) preg_replace('/^UUID/i', '', $entityuuid);

// ------------------------------------------------------------------
// Appel XMLRPC
// ------------------------------------------------------------------
$result = xmlrpc_get_major_machines_by_entity(
    $distribution,
    $entity_id,
    $filter,
    $start,
    $limit
);

$machines    = $result['machines']    ?? [];
$total       = (int)($result['total']       ?? 0);
$max_version = $result['max_version'] ?? "";
$name_version = $result['name_version'] ?? "";

// ------------------------------------------------------------------
// Titre de la page
// ------------------------------------------------------------------
$versionup = ucwords(strtolower(sprintf("%s %s %s", $distribution, $max_version, $name_version)));
$strTitle  = sprintf(_T("Machines — OS Upgrade to %s", "updates"), $versionup);

$p = new PageGenerator($strTitle);
$p->display();

// ------------------------------------------------------------------
// Tableau vide
// ------------------------------------------------------------------
if (empty($machines)) {
    echo '<div class="alert alert-info">' . _T("No machines found for this entity and distribution.", "updates") . '</div>';
    return;
}

// ------------------------------------------------------------------
// Construction des colonnes
// ------------------------------------------------------------------
$col_hostname        = [];
$col_version         = [];
$col_status          = [];
$params              = [];

// Labels des statuts
$status_labels = [
    'outdated'   => '<span class="badge badge-danger">'  . _T("Outdated",  "updates") . '</span>',
    'up_to_date' => '<span class="badge badge-success">' . _T("Up to date","updates") . '</span>',
    'pending'    => '<span class="badge badge-warning">' . _T("Pending",   "updates") . '</span>',
    'unknown'    => '<span class="badge badge-secondary">' . _T("Unknown", "updates") . '</span>',
];

foreach ($machines as $machine) {
    $hostname = htmlspecialchars($machine['hostname'] ?? '', ENT_QUOTES, 'UTF-8');
    $version  = htmlspecialchars($machine['release_version'] ?? '', ENT_QUOTES, 'UTF-8');
    $status   = $machine['status'] ?? 'unknown';

    $col_hostname[] = $hostname;
    $col_version[]  = $version;
    $col_status[]   = $status_labels[$status] ?? $status_labels['unknown'];
    $params[]       = $machine;
}

// ------------------------------------------------------------------
// Affichage OptimizedListInfos
// ------------------------------------------------------------------
$n = new OptimizedListInfos($col_hostname, _T("Hostname", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo(
    $col_version,
    _T("Current version", "updates")
);
$n->addExtraInfoCenteredRaw(
    $col_status,
    _T("Status", "updates")
);
$n->setItemCount($total);
$n->start  = ($start === -1) ? 0 : $start;
$n->end    = ($start === -1) ? max(0, count($col_hostname) - 1) : $end;
if ($start !== -1) {
    $n->setNavBar(new AjaxNavBar($total, $filter));
}
$n->setParamInfo($params);
$n->display($start === -1 ? 0 : 1);
?>
