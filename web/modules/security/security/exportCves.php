<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * Security Module - Export CVE IDs as CSV
 */

require_once("modules/security/includes/xmlrpc.php");

$location = isset($_GET['location']) ? $_GET['location'] : '';
$severity = isset($_GET['severity']) && $_GET['severity'] !== '' ? $_GET['severity'] : null;
$filter = isset($_GET['filter']) ? $_GET['filter'] : '';
$limit = isset($_GET['limit']) ? intval($_GET['limit']) : 0;

// 0 means all
if ($limit <= 0) {
    $limit = 10000;
}

$result = xmlrpc_get_cves(0, $limit, $filter, $severity, $location, 'cvss_score', 'desc');

$cve_ids = [];
if (isset($result['data']) && is_array($result['data'])) {
    foreach ($result['data'] as $cve) {
        if (isset($cve['cve_id'])) {
            $cve_ids[] = $cve['cve_id'];
        }
    }
}

// Send CSV
header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="cve_export_' . date('Y-m-d') . '.csv"');
header('Cache-Control: no-cache, no-store, must-revalidate');

$output = fopen('php://output', 'w');
foreach ($cve_ids as $id) {
    fwrite($output, $id . "\n");
}
fclose($output);
exit;
