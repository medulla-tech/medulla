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
 * Security Module - Dashboard tab content (cards and vulnerable software)
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

$tabPlatforms = array('tabwindows' => 'windows', 'tablinux' => 'linux');
$platform = $tabPlatforms[$_GET['tab'] ?? ''] ?? '';
$location = SecurityFilter::location();

$summary = xmlrpc_get_dashboard_summary($location, $platform);
$priorities = xmlrpc_get_softwares_summary(0, 10, '', $location, '', $platform);

$scope = array('location' => $location, 'platform' => $platform);
$lastScan = $summary['last_scan'] ?? null;
$scanStatuses = array(
    'completed' => _T("Completed", "security"),
    'running' => _T("Running", "security"),
    'failed' => _T("Failed", "security"),
);

SecurityFilter::script();
?>

<div class="filters-row">
    <?php SecurityFilter::entitySelect($location); ?>
</div>

<div class="security-dashboard">
    <a class="security-card exploited clickable" href="<?php echo htmlspecialchars(urlStrRedirect("security/security/allcves", $scope + array('exploited_only' => 1))); ?>"
       title="<?php echo htmlspecialchars(_T("Click to view exploited CVEs", "security")); ?>">
        <div class="card-value"><?php echo intval($summary['exploited'] ?? 0); ?></div>
        <div class="card-label"><?php echo _T("Exploited CVEs", "security"); ?></div>
    </a>
    <a class="security-card critical clickable" href="<?php echo htmlspecialchars(urlStrRedirect("security/security/allcves", $scope + array('severity' => 'Critical'))); ?>"
       title="<?php echo htmlspecialchars(_T("Click to view critical CVEs", "security")); ?>">
        <div class="card-value"><?php echo intval($summary['critical'] ?? 0); ?></div>
        <div class="card-label"><?php echo _T("Critical", "security"); ?></div>
    </a>
    <a class="security-card info clickable" href="<?php echo htmlspecialchars(urlStrRedirect("security/security/machines", $scope)); ?>"
       title="<?php echo htmlspecialchars(_T("Click to view affected machines", "security")); ?>">
        <div class="card-value"><?php echo intval($summary['machines_affected'] ?? 0); ?></div>
        <div class="card-label"><?php echo _T("Machines Affected", "security"); ?></div>
    </a>
    <div class="security-card info">
        <?php if ($lastScan): $status = $lastScan['status'] ?? ''; ?>
        <div class="card-value card-date"><?php echo !empty($lastScan['started_at']) ? date('d/m/Y H:i', strtotime($lastScan['started_at'])) : '-'; ?></div>
        <div class="card-label"><?php echo _T("Last Scan", "security") . ' : ' . ($scanStatuses[$status] ?? htmlspecialchars($status)); ?></div>
        <?php else: ?>
        <div class="card-value card-date">-</div>
        <div class="card-label"><?php echo _T("No scan has been performed yet", "security"); ?></div>
        <?php endif; ?>
    </div>
</div>

<div class="priority-header">
    <h3><?php echo _T("To fix first", "security"); ?></h3>
    <a href="<?php echo htmlspecialchars(urlStrRedirect("security/security/softwares", $scope)); ?>"><?php echo _T("View all software", "security"); ?> &rarr;</a>
</div>

<?php
$count = min(10, intval($priorities['total'] ?? 0));
if ($count > 0) {
    SecurityLists::softwares($priorities['data'] ?? array(), $count, null, SecurityFilter::here());
} else {
    EmptyStateBox::show(
        _T("No vulnerable software found", "security"),
        _T("No software with CVE data match your current filters.", "security")
    );
}
?>
