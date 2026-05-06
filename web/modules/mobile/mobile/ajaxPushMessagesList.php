<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter    = isset($_GET['filter']) ? $_GET['filter'] : '';
$field     = isset($_GET['field'])  ? $_GET['field']  : 'all';
$page_num  = isset($_GET['page'])   ? (int)$_GET['page'] : 1;
$page_size = 50;

$device_number  = '';
$message_filter = $filter;

$messages = xmlrpc_get_hmdm_push_messages($device_number, $message_filter, '',
                                          null, null, $page_size, $page_num);

if (!empty($filter) && $field !== 'all' && is_array($messages)) {
    $messages = array_values(array_filter($messages, function($msg) use ($filter, $field) {
        $fieldMap = ['device' => 'name', 'type' => 'type', 'payload' => 'payload'];
        $key = $fieldMap[$field] ?? null;
        if (!$key) return true;
        return stripos($msg[$key] ?? '', $filter) !== false;
    }));
}


$devices  = [];
$times    = [];
$types    = [];
$payloads = [];
$ids      = [];

if (is_array($messages)) {
    foreach ($messages as $i => $msg) {
        $device = htmlspecialchars($msg['name'] ?? '');
        $devices[]  = $device;
        $times[]    = isset($msg['time']) ? date("Y-m-d H:i:s", $msg['time']) : '';
        $types[]    = htmlspecialchars($msg['type'] ?? '');
        $payloads[] = htmlspecialchars($msg['payload'] ?? '');
        $ids[]      = 'pm_' . $i;
    }
}

$count = count($devices);

$n = new OptimizedListInfos($devices, _T("Device", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();
$n->addExtraInfo($times,    _T("Time",    "mobile"));
$n->addExtraInfo($types,    _T("Type",    "mobile"));
$n->addExtraInfo($payloads, _T("Payload", "mobile"));
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform"));
$n->setItemCount($count);
$n->start = 0;
$n->end   = $count;
$n->display();
