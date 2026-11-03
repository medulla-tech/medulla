<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * Security Module - Export CVE IDs as CSV
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

$limit = isset($_GET['limit']) ? intval($_GET['limit']) : 0;
$allowed = ['cve_id', 'severity', 'cvss_score', 'exploited_since', 'description', 'machines_affected', 'software'];
$columns = array_values(array_intersect(explode(',', $_GET['columns'] ?? 'cve_id'), $allowed)) ?: ['cve_id'];

// 0 means all
if ($limit <= 0) {
    $limit = 10000;
}

$result = xmlrpc_get_cves(
    0,
    $limit,
    $_GET['filter'] ?? '',
    SecurityFilter::severity(),
    SecurityFilter::location(),
    'cvss_score',
    'desc',
    SecurityFilter::platform(),
    SecurityFilter::exploitedOnly()
);

header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="cve_export_' . date('Y-m-d') . '.csv"');
header('Cache-Control: no-cache, no-store, must-revalidate');

$output = fopen('php://output', 'w');

if (count($columns) > 1) {
    fputcsv($output, $columns);
}

foreach ($result['data'] ?? array() as $cve) {
    $row = [];
    foreach ($columns as $col) {
        if ($col === 'software') {
            $sw = [];
            foreach ($cve['softwares'] ?? array() as $s) {
                $sw[] = $s['name'] . ' ' . $s['version'];
            }
            $value = implode('; ', $sw);
        } elseif ($col === 'exploited_since') {
            $value = SecurityFormat::date($cve['exploited_since'] ?? null);
        } else {
            $value = $cve[$col] ?? '';
        }
        $row[] = SecurityFormat::csvCell($value);
    }
    fputcsv($output, $row);
}

fclose($output);
exit;
