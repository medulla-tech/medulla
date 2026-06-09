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

$releases = xmlrpc_get_linux_approved_releases();
if (!is_array($releases) || !isset($releases['id']) || !is_array($releases['id'])) {
    $releases = [
        'id' => [],
        'distribution' => [],
        'version' => [],
        'name' => [],
        'is_current_stable' => [],
        'is_recommended' => [],
    ];
}

$distributions = [];
$versions = [];
$names = [];
$stableCheckboxes = [];
$recommendedCheckboxes = [];
$params = [];

foreach ($releases['id'] as $index => $releaseId) {
    $distribution = $releases['distribution'][$index] ?? '';
    $version = $releases['version'][$index] ?? '';
    $name = $releases['name'][$index] ?? '';
    $isCurrentStable = (int) ($releases['is_current_stable'][$index] ?? 0);
    $isRecommended = (int) ($releases['is_recommended'][$index] ?? 0);

    $distributions[] = $distribution;
    $versions[] = $version;
    $names[] = $name;

    $params[] = [
        'id' => $releaseId,
        'distribution' => $distribution,
        'version' => $version,
        'name' => $name,
        'is_current_stable' => $isCurrentStable,
        'is_recommended' => $isRecommended,
    ];

    $stableCheckboxes[] = sprintf(
        '<input type="hidden" name="is_current_stable[%1$d]" value="0"><input type="checkbox" id="stable%1$d" name="is_current_stable[%1$d]" value="1" %2$s>',
        (int) $releaseId,
        $isCurrentStable === 1 ? 'checked' : ''
    );

    $recommendedCheckboxes[] = sprintf(
        '<input type="hidden" name="is_recommended[%1$d]" value="0"><input type="checkbox" id="recommended%1$d" name="is_recommended[%1$d]" value="1" %2$s>',
        (int) $releaseId,
        $isRecommended === 1 ? 'checked' : ''
    );
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
echo '<form method="post" action="" name="linuxApprovedReleasesForm" class="approval-form linux-approved-releases">';
echo '<div class="approval-table-scroll">';

$n = new ListInfos($distributions, _T("Distribution", "updates"));
$n->addExtraInfo($versions, _T("Version", "updates"));
$n->addExtraInfo($names, _T("Name", "updates"));
$n->addExtraInfoCenteredRaw($stableCheckboxes, _T("Current stable", "updates"));
$n->addExtraInfoCenteredRaw($recommendedCheckboxes, _T("Recommended", "updates"));
$n->setParamInfo($params);
$n->start = 0;
$n->end = count($distributions);
$n->disableFirstColumnActionLink();
$n->display($navbar = 0, $header = 0);

echo '</div>';
echo '<div class="approval-table-clear"></div>';
echo '<input type="hidden" name="form_name" value="linux_approved_releases">';
echo '<div class="approval-form-actions">';
echo '<input class="btnPrimary" type="submit" value="' . _T("Apply", "updates") . '">';
echo '</div>';
echo "\n</form>";
?>