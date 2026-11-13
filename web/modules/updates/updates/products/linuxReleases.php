<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/products/linuxReleases.php

require_once("modules/medulla_server/includes/utilities.php");
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

$entity = updatesWinProductsEntity();
if (!$entity) {
    EmptyStateBox::show(_T("No entity available for this user.", "updates"));
    return;
}
$entityId = updatesEntityId($entity);
$pageUrl = urlStrRedirect("updates/updates/products", array('tab' => 'tablinux', 'location' => $entity['uuid']));

$result = xmlrpc_get_linux_releases($entityId);
$releases = null;
if (!updatesReadFailed($result) && is_array($result['rows'] ?? null)) {
    $releases = array();
    foreach ($result['rows'] as $row) {
        $distribution = is_array($row) && is_scalar($row['distribution'] ?? null) ? trim((string) $row['distribution']) : '';
        $release = is_array($row) && is_scalar($row['release'] ?? null) ? trim((string) $row['release']) : '';
        if ($distribution !== '' && $release !== '') {
            $releases[] = array(
                'distribution' => $distribution,
                'release' => $release,
                'codename' => is_scalar($row['codename'] ?? null) ? trim((string) $row['codename']) : '',
                'tracked' => !empty($row['tracked']),
            );
        }
    }
}
$inherited = is_array($result) ? updatesWinInheritedEntity($result['inherited_from'] ?? null) : null;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['bsavereleases'])) {
    verifyCSRFToken($_POST);
    $saved = false;
    $unchanged = false;
    if ($releases !== null) {
        $posted = array();
        foreach ((array) ($_POST['tracked'] ?? array()) as $distribution => $postedReleases) {
            foreach ((array) $postedReleases as $release) {
                if (is_scalar($release)) {
                    $posted[$distribution][(string) $release] = true;
                }
            }
        }
        // Only the versions offered to the entity are kept.
        $selections = array();
        $tracked = array();
        foreach ($releases as $row) {
            $pair = array('distribution' => $row['distribution'], 'release' => $row['release']);
            if ($row['tracked']) {
                $tracked[] = $pair;
            }
            if (isset($posted[$row['distribution']][$row['release']])) {
                $selections[] = $pair;
            }
        }
        // Inherited and left as it is: it stays inherited, nothing is written.
        $unchanged = $inherited !== null && $selections === $tracked;
        $saved = !$unchanged && xmlrpc_set_linux_releases($entityId, $selections) === true;
    }
    if ($unchanged) {
        new NotifyWidgetSuccess(_T("No change: the setting stays inherited.", "updates"));
    } elseif ($saved) {
        new NotifyWidgetSuccess(_T("Saved. The entity's machines are being re-evaluated.", "updates"));
    } else {
        new NotifyWidgetFailure(_T("Save failed.", "updates"));
    }
    header("Location: " . $pageUrl);
    exit;
}

echo '<div class="updates-entity-section">';
updatesEntitySelect($entity, false, updatesWinInheritanceLine($entity, 'linuxreleases', $result));
echo '</div>';

if ($releases === null) {
    updatesReadFailedBox();
    return;
}
if (empty($releases)) {
    EmptyStateBox::show(_T("No Linux version reported by the machines", "updates"));
    return;
}

$groups = array();
foreach ($releases as $row) {
    $groups[$row['distribution']][] = $row;
}

$names = array();
$checks = array();
$cssClasses = array();
$familyIndex = 0;
foreach ($groups as $distribution => $rows) {
    $familyIndex++;
    $distributionName = updatesLinuxDistributionName($distribution);
    $names[] = htmlspecialchars($distributionName, ENT_QUOTES, 'UTF-8');
    $checks[] = sprintf(
        '<input type="checkbox" class="family-check-all" data-family="%d" title="%s">',
        $familyIndex,
        htmlspecialchars(_T("Track every version of this distribution", "updates"), ENT_QUOTES, 'UTF-8')
    );
    $cssClasses[] = "family-separator";

    foreach ($rows as $row) {
        $label = $distributionName . ' ' . $row['release'];
        if ($row['codename'] !== '') {
            $label .= ' (' . $row['codename'] . ')';
        }
        $names[] = htmlspecialchars($label, ENT_QUOTES, 'UTF-8');
        $checks[] = sprintf(
            '<input type="checkbox" class="product-check" name="tracked[%s][]" value="%s" data-family="%d"%s>',
            htmlspecialchars($row['distribution'], ENT_QUOTES, 'UTF-8'),
            htmlspecialchars($row['release'], ENT_QUOTES, 'UTF-8'),
            $familyIndex,
            $row['tracked'] ? ' checked' : ''
        );
        $cssClasses[] = "family-produit alternate";
    }
}

echo '<form method="post" action="' . htmlspecialchars($pageUrl, ENT_QUOTES, 'UTF-8') . '" class="approval-form">';
$n = new ListInfos($names, _T("Version", "updates"));
$n->addExtraInfoCenteredRaw($checks, _T("Tracked", "updates"));
$n->setNavBar = "";
$n->start = 0;
$n->end = count($names) - 1;
$n->setCssCaptionClass("table-rounded caption-style");
$n->setCssClasses($cssClasses);
$n->disableFirstColumnActionLink();
$n->display(0, 0);
updatesTrackedFormEnd('bsavereleases');
?>
