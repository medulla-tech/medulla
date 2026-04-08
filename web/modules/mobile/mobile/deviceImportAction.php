<?php
require_once("modules/mobile/includes/xmlrpc.php");

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_FILES['csv_file'])) {
    new NotifyWidgetFailure(_T("No file uploaded", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/deviceExport"));
    exit;
}

$upload_error = $_FILES['csv_file']['error'];
if ($upload_error !== UPLOAD_ERR_OK) {
    new NotifyWidgetFailure(_T("File upload failed", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/deviceExport"));
    exit;
}

$csv_path = $_FILES['csv_file']['tmp_name'];
$csv_content = file_get_contents($csv_path);

if ($csv_content === false || empty($csv_content)) {
    new NotifyWidgetFailure(_T("Failed to read CSV file or file is empty", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/deviceExport"));
    exit;
}

$csv_content = preg_replace('/^\xEF\xBB\xBF/', '', $csv_content);

$result = xmlrpc_import_hmdm_devices($csv_content);

if ($result === null || $result === false) {
    new NotifyWidgetFailure(_T("Import failed. Please check the CSV format and try again.", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/deviceExport"));
    exit;
}

$created = isset($result['created']) ? intval($result['created']) : 0;
$updated = isset($result['updated']) ? intval($result['updated']) : 0;
$skipped = isset($result['skipped']) ? intval($result['skipped']) : 0;
$errors = isset($result['errors']) && is_array($result['errors']) ? $result['errors'] : [];

if (empty($errors)) {
    new NotifyWidgetSuccess(sprintf(
        _T("Import completed: %d created, %d updated, %d skipped", "mobile"),
        $created, $updated, $skipped
    ));
} else {
    new NotifyWidgetWarning(sprintf(
        _T("Import completed with errors: %d created, %d updated, %d skipped. Errors: %s", "mobile"),
        $created, $updated, $skipped, implode("; ", array_slice($errors, 0, 3))
    ));
}

header("Location: " . urlStrRedirect("mobile/mobile/index"));
exit;
?>
