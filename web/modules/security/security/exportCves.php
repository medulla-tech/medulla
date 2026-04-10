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
$columns = isset($_GET['columns']) ? explode(',', $_GET['columns']) : ['cve_id'];

// Allowed columns
$allowed = ['cve_id', 'severity', 'cvss_score', 'description', 'machines_affected', 'software'];
$columns = array_intersect($columns, $allowed);
if (empty($columns)) {
    $columns = ['cve_id'];
}

// 0 means all
if ($limit <= 0) {
    $limit = 10000;
}

$result = xmlrpc_get_cves(0, $limit, $filter, $severity, $location, 'cvss_score', 'desc');

// Send CSV
header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="cve_export_' . date('Y-m-d') . '.csv"');
header('Cache-Control: no-cache, no-store, must-revalidate');

$output = fopen('php://output', 'w');

// Write header if more than one column
if (count($columns) > 1) {
    fputcsv($output, $columns);
}

if (isset($result['data']) && is_array($result['data'])) {
    foreach ($result['data'] as $cve) {
        $row = [];
        foreach ($columns as $col) {
            if ($col === 'software') {
                $sw = [];
                if (isset($cve['softwares']) && is_array($cve['softwares'])) {
                    foreach ($cve['softwares'] as $s) {
                        $sw[] = $s['name'] . ' ' . $s['version'];
                    }
                }
                $row[] = implode('; ', $sw);
            } else {
                $row[] = isset($cve[$col]) ? $cve[$col] : '';
            }
        }
        fputcsv($output, $row);
    }
}

fclose($output);
exit;
