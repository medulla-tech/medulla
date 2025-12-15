<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get filter parameter
$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

// Fetch configurations from HMDM via xmlrpc wrapper
$configs = xmlrpc_get_hmdm_configurations();
if (!is_array($configs)) $configs = [];

// Filter by configuration name if filter is provided
if (!empty($filter)) {
    $configs = array_filter($configs, function($cfg) use ($filter) {
        $cfgName = $cfg['name'] ?? '';
        return stripos($cfgName, $filter) !== false;
    });
}

$ids = $col1 = $descriptions = $actions = [];

foreach ($configs as $index => $cfg) {
    $id = 'cfg_' . $index;
    $ids[] = $id;

    $cfgId = $cfg['id'] ?? '';
    $name = htmlspecialchars($cfg['name'] ?? 'Unnamed');
    $desc = htmlspecialchars($cfg['description'] ?? '-');

    $col1[] = "<a href='#' class='cfglink'>{$name}</a>";
    $descriptions[] = $desc;

    $deleteUrl = urlStrRedirect("mobile/mobile/deleteConfiguration", array('action' => 'deleteConfiguration', 'id' => $cfgId, 'name' => $name));
    $actions[] = "<ul class='action' style='list-style-type: none; padding: 0; margin: 0; display: flex; gap: 8px; align-items: center;'>
    </ul>";
}

$n = new OptimizedListInfos($col1, _T("Configuration", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

// navbar
$count = safeCount($col1);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($descriptions, _T("Description", "mobile"));
$n->addExtraInfo($actions, _T("Actions", "mobile"));

$n->start = 0;
$n->display();

?>
