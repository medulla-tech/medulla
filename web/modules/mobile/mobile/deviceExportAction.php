<?php
require_once("modules/mobile/includes/xmlrpc.php");

$group_id = isset($_POST['group_id']) && $_POST['group_id'] !== '' ? intval($_POST['group_id']) : null;
$configuration_id = isset($_POST['configuration_id']) && $_POST['configuration_id'] !== '' ? intval($_POST['configuration_id']) : null;
$filter_text = isset($_POST['filter_text']) && $_POST['filter_text'] !== '' ? trim($_POST['filter_text']) : null;
$columns = isset($_POST['columns']) && is_array($_POST['columns']) ? $_POST['columns'] : ['description', 'configuration', 'imei', 'phone', 'groups'];

if (empty($columns)) {
    header("Location: " . urlStrRedirect("mobile/mobile/deviceExport") . "&error=no_columns");
    exit;
}

$csv_content = xmlrpc_export_hmdm_devices($group_id, $configuration_id, $filter_text, $columns);

if ($csv_content === null || $csv_content === false) {
    header("Location: " . urlStrRedirect("mobile/mobile/deviceExport") . "&error=export_failed");
    exit;
}

header('Content-Type: text/csv; charset=UTF-8');
header('Content-Disposition: attachment; filename="devices.csv"');
header('Cache-Control: no-cache, must-revalidate');
header('Pragma: no-cache');

echo $csv_content;
exit;
?>
