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

$cve_id = isset($_GET['cve_id']) ? htmlspecialchars($_GET['cve_id']) : '';

$p = new PageGenerator(sprintf(_T("CVE Details: %s", 'security'), $cve_id));
$p->setSideMenu($sidemenu);
$p->display();

if (empty($cve_id)) {
    echo '<p class="error">' . _T("Invalid CVE ID", "security") . '</p>';
    return;
}

// Get user's accessible entities for filtering
list($listEntities, $valuesEntities) = getEntitiesSelectableElements();
$location = implode(',', $valuesEntities);

// Get CVE details from backend (filtered by user's entities)
$cve = xmlrpc_get_cve_details($cve_id, $location);

if (!$cve) {
    echo '<p class="error">' . _T("CVE not found", "security") . '</p>';
    return;
}

// Determine severity class for styling
$severityClass = strtolower($cve['severity']);

// Determine CVSS class
$cvss = floatval($cve['cvss_score']);
if ($cvss >= 9.0) $cvssClass = 'cvss-critical';
elseif ($cvss >= 7.0) $cvssClass = 'cvss-high';
elseif ($cvss >= 4.0) $cvssClass = 'cvss-medium';
else $cvssClass = 'cvss-low';
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<a href="<?php echo urlStrRedirect('security/security/index'); ?>" class="back-link">
    &larr; <?php echo _T("Back to CVE list", "security"); ?>
</a>

<div class="cve-header severity-<?php echo $severityClass; ?>">
    <div class="cve-title"><?php echo htmlspecialchars($cve['cve_id']); ?></div>
    <div class="cve-meta">
        <div class="cve-meta-item">
            <strong><?php echo _T("Severity", "security"); ?>:</strong>
            <span class="badge badge-<?php echo $severityClass; ?>">
                <?php echo htmlspecialchars($cve['severity']); ?>
            </span>
        </div>
        <div class="cve-meta-item">
            <strong><?php echo _T("CVSS Score", "security"); ?>:</strong>
            <span class="cvss-score <?php echo $cvssClass; ?>"><?php echo number_format($cve['cvss_score'], 1); ?></span>
        </div>
        <?php if ($cve['published_at']): ?>
        <div class="cve-meta-item">
            <strong><?php echo _T("Published", "security"); ?>:</strong>
            <span><?php echo date('Y-m-d', strtotime($cve['published_at'])); ?></span>
        </div>
        <?php endif; ?>
        <?php if ($cve['fetched_at']): ?>
        <div class="cve-meta-item">
            <strong><?php echo _T("Last Updated", "security"); ?>:</strong>
            <span><?php echo date('Y-m-d H:i', strtotime($cve['fetched_at'])); ?></span>
        </div>
        <?php endif; ?>
    </div>
    <div class="external-link">
        <a href="https://nvd.nist.gov/vuln/detail/<?php echo urlencode($cve['cve_id']); ?>" target="_blank">
            <?php echo _T("View on NVD", "security"); ?> &rarr;
        </a>
    </div>
</div>

<h3 class="section-title"><?php echo _T("Description", "security"); ?></h3>
<div class="cve-description">
    <?php echo nl2br(htmlspecialchars($cve['description'] ? $cve['description'] : _T("No description available", "security"))); ?>
</div>

<?php if (!empty($cve['softwares'])): ?>
<h3 class="section-title"><?php echo _T("Affected Software", "security"); ?></h3>
<ul class="software-list">
    <?php foreach ($cve['softwares'] as $sw): ?>
    <li>
        <strong><?php echo htmlspecialchars($sw['name']); ?></strong>
        <span class="software-version">v<?php echo htmlspecialchars($sw['version']); ?></span>
    </li>
    <?php endforeach; ?>
</ul>
<?php endif; ?>

<h3 class="section-title">
    <?php echo _T("Affected Machines", "security"); ?>
    <span class="section-count">
        (<?php echo count($cve['machines']); ?>)
    </span>
</h3>

<?php if (!empty($cve['machines'])): ?>
<table class="machines-table">
    <thead>
        <tr>
            <th><?php echo _T("Hostname", "security"); ?></th>
            <th><?php echo _T("Software", "security"); ?></th>
            <th><?php echo _T("Version", "security"); ?></th>
            <th><?php echo _T("Actions", "security"); ?></th>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($cve['machines'] as $machine): ?>
        <tr>
            <td><?php echo htmlspecialchars($machine['hostname']); ?></td>
            <td><?php echo htmlspecialchars($machine['software_name']); ?></td>
            <td><?php echo htmlspecialchars($machine['software_version']); ?></td>
            <td>
                <a href="<?php echo urlStrRedirect('security/security/machineDetail', array('id_glpi' => $machine['id_glpi'], 'hostname' => $machine['hostname'])); ?>">
                    <?php echo _T("View all CVEs", "security"); ?>
                </a>
            </td>
        </tr>
        <?php endforeach; ?>
    </tbody>
</table>
<?php else: ?>
<div class="empty-message">
    <p><?php echo _T("No machines currently affected by this CVE", "security"); ?></p>
</div>
<?php endif; ?>
