<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter        = isset($_GET['filter']) ? $_GET['filter'] : '';
$field         = isset($_GET['field'])  ? $_GET['field']  : 'all';
$status_filter = isset($_GET['status']) ? $_GET['status'] : 'all';
$page_num      = isset($_GET['page'])   ? (int)$_GET['page'] : 1;
$page_size     = 50;

$device_number  = '';
$message_filter = $filter;

$status_param = ($status_filter === 'all') ? 'all messages' : $status_filter;
$messages = xmlrpc_get_hmdm_messages($device_number, $message_filter, $status_param,
                                     null, null, $page_size, $page_num);

if (!empty($filter) && $field !== 'all' && is_array($messages)) {
    $messages = array_values(array_filter($messages, function($msg) use ($filter, $field) {
        $fieldMap = ['device' => 'name', 'message' => 'message'];
        $key = $fieldMap[$field] ?? null;
        if (!$key) return true;
        return stripos($msg[$key] ?? '', $filter) !== false;
    }));
}

$statusLabels = [
    '0' => _T("Sent",      "mobile"),
    '1' => _T("Delivered", "mobile"),
    '2' => _T("Read",      "mobile"),
];

$devices  = [];
$times    = [];
$statuses = [];
$texts    = [];
$ids      = [];

if (is_array($messages)) {
    foreach ($messages as $i => $msg) {
        $devices[]  = htmlspecialchars($msg['name'] ?? '');
        $times[]    = isset($msg['time']) ? date("Y-m-d H:i:s", $msg['time']) : '';
        $st         = isset($msg['status']) ? (string)$msg['status'] : '';
        $statuses[] = isset($statusLabels[$st]) ? $statusLabels[$st] : htmlspecialchars($st);
        $texts[]    = htmlspecialchars($msg['message'] ?? '');
        $ids[]      = 'msg_' . $i;
    }
}

$count = count($devices);

$n = new OptimizedListInfos($devices, _T("Device", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();
$n->addExtraInfo($times,    _T("Time",    "mobile"));
$n->addExtraInfo($statuses, _T("Status",  "mobile"));
$n->addExtraInfo($texts,    _T("Message", "mobile"));
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform"));
$n->setItemCount($count);
$n->start = 0;
$n->end   = $count;
$n->display();
echo '<script>(function(){var $tb=jQuery(".listinfos:last tbody");if(!$tb.children("tr").length){$tb.append("<tr><td colspan=\"20\" style=\"text-align:center;color:#888;padding:20px;font-style:italic;\">" + ' . json_encode(_T("No messages found", "mobile")) . ' + "</td></tr>");}})();</script>';
