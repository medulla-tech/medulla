<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");
require("localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

global $maxperpage;
if (!isset($maxperpage) || !is_numeric($maxperpage)) {
    $maxperpage = 20;
}

$entityuuid = (isset($_GET['entity'])) ? htmlentities($_GET['entity']) : "UUID0";
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

$selectedLocation = $_POST['selected_location'] ?? $_GET['selected_location'] ?? [];
$rawEntity = $_POST['entityid'] ?? $_GET['entityid'] ?? ($selectedLocation['uuid'] ?? ($selectedLocation['id'] ?? ''));
$entityId = (int) preg_replace('/^UUID/i', '', (string) $rawEntity);

$releases = xmlrpc_get_linux_approved_releases($entityId);
if (!is_array($releases) || !isset($releases['id']) || !is_array($releases['id'])) {
    $releases = [
        'id' => [],
        'distribution' => [],
        'version' => [],
        'name' => [],
        'is_current_stable' => [],
        'is_latest_major_version' => [],
    ];
}
$versions = [];
// $stableCheckboxes = []; // Colonne conservee pour reprise si besoin.
$latestMajorVersionCheckboxes = [];
$params = [];
$cssClasses = [];
$submittedStableValues = $_POST['is_current_stable'] ?? [];
$submittedLatestMajorVersionValues = $_POST['is_latest_major_version'] ?? ($_POST['is_recommended'] ?? []);

$rows = [];
foreach ($releases['id'] as $index => $releaseId) {
    $rows[] = [
        'id' => (int) $releaseId,
        'distribution' => (string) ($releases['distribution'][$index] ?? ''),
        'version' => (string) ($releases['version'][$index] ?? ''),
        'name' => (string) ($releases['name'][$index] ?? ''),
        'is_current_stable' => (int) ($releases['is_current_stable'][$index] ?? 0),
        'is_latest_major_version' => (int) (($releases['is_latest_major_version'][$index] ?? ($releases['is_recommended'][$index] ?? 0))),
    ];
}

usort($rows, static function ($a, $b) {
    $distributionCmp = strcasecmp($a['distribution'], $b['distribution']);
    if ($distributionCmp !== 0) {
        return $distributionCmp;
    }

    // Sort versions in descending natural order within each distribution.
    return strnatcasecmp($b['version'], $a['version']);
});

foreach ($rows as $row) {
    $releaseId = $row['id'];
    $distribution = $row['distribution'];
    $version = $row['version'];
    $isCurrentStable = $row['is_current_stable'];
    $isLatestMajorVersion = $row['is_latest_major_version'];

    $versions[] = $version;

    $params[] = [
        'id' => $releaseId,
        'distribution' => $distribution,
        'version' => $version,
        'is_current_stable' => $isCurrentStable,
        'is_latest_major_version' => $isLatestMajorVersion,
    ];

    $effectiveCurrentStable = array_key_exists($releaseId, $submittedStableValues)
        ? (int) $submittedStableValues[$releaseId]
        : $isCurrentStable;
    $effectiveLatestMajorVersion = array_key_exists($releaseId, $submittedLatestMajorVersionValues)
        ? (int) $submittedLatestMajorVersionValues[$releaseId]
        : $isLatestMajorVersion;

    // $stableCheckboxes[] = sprintf(
    //     '<input type="hidden" name="is_current_stable[%1$d]" value="0"><input type="checkbox" id="stable%1$d" name="is_current_stable[%1$d]" value="1" %2$s>',
    //     (int) $releaseId,
    //     $effectiveCurrentStable === 1 ? 'checked' : ''
    // );

    $latestMajorVersionCheckboxes[] = sprintf(
        '<input type="hidden" name="is_latest_major_version[%1$d]" value="0"><input type="checkbox" id="latestMajorVersion%1$d" name="is_latest_major_version[%1$d]" value="1" %2$s>',
        (int) $releaseId,
        $effectiveLatestMajorVersion === 1 ? 'checked' : ''
    );

    $cssClasses[] = 'family-produit alternate';
}

// Insert distribution section headers, like approve_products does for Windows products.
$groupedVersionColumn = [];
// $groupedStableCheckboxes = []; // Colonne conservee pour reprise si besoin.
$groupedLatestMajorVersionCheckboxes = [];
$groupedParams = [];
$groupedCssClasses = [];

$currentDistribution = null;
foreach ($rows as $index => $row) {
    $distribution = $row['distribution'];
    if ($distribution !== $currentDistribution) {
        $currentDistribution = $distribution;
        $groupedVersionColumn[] = strtoupper($distribution);
        // $groupedStableCheckboxes[] = '&nbsp;';
        $groupedLatestMajorVersionCheckboxes[] = '&nbsp;';
        $groupedParams[] = ['id' => 0, 'distribution' => $distribution, 'is_separator' => 1];
        $groupedCssClasses[] = 'family-separator';
    }

    $groupedVersionColumn[] = $versions[$index];
    // $groupedStableCheckboxes[] = $stableCheckboxes[$index];
    $groupedLatestMajorVersionCheckboxes[] = $latestMajorVersionCheckboxes[$index];
    $groupedParams[] = $params[$index];
    $groupedCssClasses[] = $cssClasses[$index];
}

echo '<style type="text/css">
.linux-approved-releases {
    box-sizing: border-box;
    width: 100%;
    max-width: 100%;
    display: block;
    clear: both;
}
.linux-approved-releases .approval-table-scroll {
    box-sizing: border-box;
    display: block;
    clear: both;
    width: 100%;
    max-width: 100%;
    padding: 0 12px 12px 0;
    overflow-x: auto;
    overflow-y: hidden;
}
.linux-approved-releases table.listinfos {
    width: 100%;
}
.linux-approved-releases .approval-table-clear {
    clear: both;
    display: block;
    height: 0;
    overflow: hidden;
}
.linux-approved-releases .approval-form-actions {
    box-sizing: border-box;
    clear: both;
    display: block;
    float: none;
    width: 100%;
    padding: 12px 12px 0 0;
    text-align: right;
}
.linux-approved-releases .approval-form-actions .btnPrimary {
    float: none;
}
</style>';
echo '<form method="post" action="'.urlStrRedirect("updates/updates/linuxApprovedReleases").'" name="linuxApprovedReleasesForm" class="approval-form linux-approved-releases">';
echo '<div class="approval-table-scroll">';

$n = new ListInfos($groupedVersionColumn, _T("Version", "updates"));
// $n->addExtraInfoCenteredRaw($groupedStableCheckboxes, _T("Updates enabled", "updates"));
$n->addExtraInfoCenteredRaw($groupedLatestMajorVersionCheckboxes, _T("Latest major version", "updates"));
$n->setParamInfo($groupedParams);
$n->start = 0;
$n->end = count($groupedVersionColumn);
$n->setCssClasses($groupedCssClasses);
$n->disableFirstColumnActionLink();
$n->display($navbar = 0, $header = 0);

echo '</div>';
echo '<div class="approval-table-clear"></div>';
echo '<input type="hidden" name="form_name" value="linux_approved_releases">';
echo '<input type="hidden" name="auth_token" value="'.htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8').'">';
echo '<input type="hidden" name="entityid" value="'.$entityId.'">';
echo '<input type="hidden" name="entityname" value="'.($selectedLocation['name'] ?? '').'">';
echo '<div class="approval-form-actions">';
echo '<input class="btnPrimary" type="submit" value="' . _T("Apply", "updates") . '">';
echo '</div>';
echo "\n</form>";
?>
