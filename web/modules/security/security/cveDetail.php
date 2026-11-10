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
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * Security Module - CVE Detail
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

$cve_id = strtoupper(trim($_GET['cve_id'] ?? ''));
$validId = preg_match('/^CVE-\d{4}-\d{4,}$/', $cve_id) === 1;

$p = new PageGenerator(sprintf(_T("CVE Details: %s", 'security'), $validId ? $cve_id : ''));
$p->setSideMenu($sidemenu);
$p->display();

if (!$validId) {
    echo '<p class="error">' . _T("Invalid CVE ID", "security") . '</p>';
    return;
}

$cve = xmlrpc_get_cve_details($cve_id, SecurityFilter::location());

if (!$cve) {
    echo '<p class="error">' . _T("CVE not found", "security") . '</p>';
    return;
}

$severityClass = SecurityBadge::severityClass($cve['severity']);

$sourceNames = array(
    'nvd' => 'NVD',
    'cve' => 'CVE.org',
    'euvd' => 'EUVD (ENISA)',
    'debian' => 'Debian',
    'ubuntu' => 'Ubuntu',
);
$links = array();
foreach ($cve['source_urls'] ?? array() as $src => $url) {
    if (!is_string($url) || !preg_match('#^https?://#i', $url)) {
        continue;
    }
    $name = $sourceNames[$src] ?? strtoupper($src);
    $links[] = '<a href="' . htmlspecialchars($url) . '" target="_blank" rel="noopener noreferrer">' . htmlspecialchars($name) . '</a>';
}
if (empty($links)) {
    $links[] = '<a href="https://nvd.nist.gov/vuln/detail/' . urlencode($cve_id) . '" target="_blank" rel="noopener noreferrer">NVD</a>';
}

// One row per machine, listing its affected software
$machinesByHost = array();
foreach ($cve['machines'] ?? array() as $machine) {
    $id = $machine['id_glpi'];
    if (!isset($machinesByHost[$id])) {
        $machinesByHost[$id] = array(
            'id_glpi' => $id,
            'hostname' => $machine['hostname'],
            'softwares' => array()
        );
    }
    $machinesByHost[$id]['softwares'][] = array(
        'name' => $machine['software_name'],
        'version' => $machine['software_version']
    );
}
?>

<?php SecurityFilter::backLink('allcves', _T("Back to CVE list", "security")); ?>

<div class="cve-header severity-<?php echo $severityClass; ?>">
    <div class="cve-title"><?php echo htmlspecialchars($cve['cve_id']); ?></div>
    <div class="cve-meta">
        <div class="cve-meta-item">
            <strong><?php echo _T("Risk", "security"); ?>:</strong>
            <?php echo SecurityBadge::risk($cve['cvss_score'], $cve['severity']); ?>
        </div>
        <?php if (!empty($cve['exploited_since'])): ?>
        <div class="cve-meta-item">
            <span class="exploited-flag">⚠ <?php echo htmlspecialchars(SecurityBadge::exploitedText($cve['exploited_since'])); ?></span>
        </div>
        <?php endif; ?>
        <?php if (!empty($cve['published_at'])): ?>
        <div class="cve-meta-item">
            <strong><?php echo _T("Published", "security"); ?>:</strong>
            <span><?php echo SecurityFormat::date($cve['published_at']); ?></span>
        </div>
        <?php endif; ?>
        <?php if (!empty($cve['last_modified'])): ?>
        <div class="cve-meta-item">
            <strong><?php echo _T("Last Modified", "security"); ?>:</strong>
            <span><?php echo SecurityFormat::date($cve['last_modified']); ?></span>
        </div>
        <?php endif; ?>
        <?php if (!empty($cve['euvd_id'])): ?>
        <div class="cve-meta-item">
            <strong><?php echo _T("EUVD ID", "security"); ?>:</strong>
            <span><?php echo htmlspecialchars($cve['euvd_id']); ?></span>
        </div>
        <?php endif; ?>
    </div>
    <div class="external-links">
        <strong><?php echo _T("View on", "security"); ?>:</strong>
        <?php echo implode(' | ', $links); ?>
    </div>
</div>

<h3 class="section-title"><?php echo _T("Description", "security"); ?></h3>
<div class="cve-description">
    <?php echo nl2br(htmlspecialchars(($cve['description'] ?? '') ?: _T("No description available", "security"))); ?>
</div>

<?php if (!empty($cve['softwares'])): ?>
<h3 class="section-title"><?php echo _T("Affected Software", "security"); ?></h3>
<ul class="software-list">
    <?php foreach ($cve['softwares'] as $sw): ?>
    <li>
        <strong><?php echo htmlspecialchars($sw['name']); ?></strong>
        <span class="software-version">v<?php echo htmlspecialchars($sw['version']); ?></span>
        <?php echo SecurityBadge::fix($sw['fix_available'] ?? null); ?>
    </li>
    <?php endforeach; ?>
</ul>
<?php endif; ?>

<h3 class="section-title">
    <?php echo _T("Affected Machines", "security"); ?>
    <span class="section-count">(<?php echo count($machinesByHost); ?>)</span>
</h3>

<?php
if (!empty($machinesByHost)) {
    $hostnames = array();
    $softwares = array();
    $params = array();
    foreach ($machinesByHost as $machine) {
        $hostnames[] = htmlspecialchars($machine['hostname']);
        $lines = array();
        foreach ($machine['softwares'] as $sw) {
            $lines[] = htmlspecialchars($sw['name']) . ' <span class="cell-sub">' . htmlspecialchars($sw['version']) . '</span>';
        }
        $softwares[] = implode('<br/>', $lines);
        $params[] = array('id_glpi' => $machine['id_glpi'], 'hostname' => $machine['hostname'], 'back' => SecurityFilter::here());
    }
    $n = new OptimizedListInfos($hostnames, _T("Machine", "security"));
    $n->setTableCssClass("security-table");
    $n->disableFirstColumnActionLink();
    $n->addExtraInfoRaw($softwares, _T("Affected Software", "security"));
    $n->setParamInfo($params);
    $n->addActionItem(new ActionItem(_T("View CVEs", "security"), "machineDetail", "display", "", "security", "security"));
    $n->setItemCount(count($hostnames));
    $n->start = 0;
    $n->end = count($hostnames);
    $n->display(0, 0);
} else {
?>
<div class="empty-message">
    <p><?php echo _T("No machines currently affected by this CVE", "security"); ?></p>
</div>
<?php } ?>
