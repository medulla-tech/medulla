<?php
require_once("modules/mobile/includes/xmlrpc.php");

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_FILES['csv_file'])) {
    echo json_encode(['status' => 'error', 'message' => 'No file uploaded']);
    exit;
}

$upload_error = $_FILES['csv_file']['error'];
if ($upload_error !== UPLOAD_ERR_OK) {
    echo json_encode(['status' => 'error', 'message' => 'File upload failed']);
    exit;
}

$csv_path = $_FILES['csv_file']['tmp_name'];
$csv_content = file_get_contents($csv_path);

if ($csv_content === false || empty($csv_content)) {
    echo json_encode(['status' => 'error', 'message' => 'Failed to read CSV file or file is empty']);
    exit;
}

$csv_content = preg_replace('/^\xEF\xBB\xBF/', '', $csv_content);

$email_list = [];
$normalized = str_replace(["\r\n", "\r"], "\n", $csv_content);
$all_lines  = array_values(array_filter(explode("\n", $normalized), function($l) { return trim($l) !== ''; }));

if (count($all_lines) >= 2) {
    $header_row = array_map(function($h) { return strtolower(trim($h)); }, str_getcsv($all_lines[0]));
    $number_idx = array_search('number', $header_row);
    $email_idx  = array_search('custom1', $header_row);
    if ($number_idx !== false && $email_idx !== false) {
        for ($i = 1; $i < count($all_lines); $i++) {
            $row   = str_getcsv($all_lines[$i]);
            $name  = isset($row[$number_idx]) ? trim($row[$number_idx]) : '';
            $email = isset($row[$email_idx])  ? trim($row[$email_idx])  : '';
            if ($email !== '' && $name !== '' && filter_var($email, FILTER_VALIDATE_EMAIL)) {
                $email_list[] = ['name' => $name, 'email' => $email];
            }
        }
    }
}

$result = xmlrpc_import_hmdm_devices($csv_content);

if ($result === null || $result === false) {
    echo json_encode(['status' => 'error', 'message' => 'Import failed. Please check the CSV format and try again.']);
    exit;
}

$created = isset($result['created']) ? intval($result['created']) : 0;
$updated = isset($result['updated']) ? intval($result['updated']) : 0;
$skipped = isset($result['skipped']) ? intval($result['skipped']) : 0;
$errors  = isset($result['errors']) && is_array($result['errors']) ? $result['errors'] : [];

echo json_encode([
    'status'     => 'ok',
    'created'    => $created,
    'updated'    => $updated,
    'skipped'    => $skipped,
    'errors'     => $errors,
    'email_list' => $email_list,
]);
exit;
?>
