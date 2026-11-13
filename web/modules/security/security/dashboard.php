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

<?php
$cards = new StatCards();
$cards->addCard(intval($summary['exploited'] ?? 0), _T("Exploited CVEs", "security"), 'exploited', array(
    'href'  => urlStrRedirect("security/security/allcves", $scope + array('exploited_only' => 1)),
    'title' => _T("Click to view exploited CVEs", "security"),
));
$cards->addCard(intval($summary['critical'] ?? 0), _T("Critical", "security"), 'critical', array(
    'href'  => urlStrRedirect("security/security/allcves", $scope + array('severity' => 'Critical')),
    'title' => _T("Click to view critical CVEs", "security"),
));
$cards->addCard(intval($summary['machines_affected'] ?? 0), _T("Machines Affected", "security"), 'info', array(
    'href'  => urlStrRedirect("security/security/machines", $scope),
    'title' => _T("Click to view affected machines", "security"),
));
if ($lastScan) {
    $status = $lastScan['status'] ?? '';
    $cards->addCard(
        !empty($lastScan['started_at']) ? date('d/m/Y H:i', strtotime($lastScan['started_at'])) : '-',
        _T("Last Scan", "security") . ' : ' . ($scanStatuses[$status] ?? $status),
        'info',
        array('date' => true)
    );
} else {
    $cards->addCard('-', _T("No scan has been performed yet", "security"), 'info', array('date' => true));
}
$cards->display();
?>

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
