<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

$configs = xmlrpc_get_hmdm_configurations();
if (!is_array($configs)) $configs = [];

if (!empty($filter)) {
    $configs = array_filter($configs, function($cfg) use ($filter) {
        return stripos($cfg['name'] ?? '', $filter) !== false;
    });
}

$ids = $col1 = $descriptions = [];
$actionEdit  = [];
$params      = [];

foreach ($configs as $index => $cfg) {
    $id = 'ctcfg_' . $index;
    $ids[] = $id;

    $cfgId   = $cfg['id'] ?? '';
    $name    = htmlspecialchars($cfg['name'] ?? 'Unnamed');
    $desc    = htmlspecialchars($cfg['description'] ?? '-');

    $col1[]        = $name;
    $descriptions[] = $desc;

    $actionEdit[] = new ActionItem(_T("Edit contacts sync", "mobile"), "contactsConfig", "edit", "id", "mobile", "mobile");

    $params[] = ['id' => $cfgId];
}

$n = new OptimizedListInfos($col1, _T("Configuration", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$count  = safeCount($col1);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : '';
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($descriptions, _T("Description", "mobile"));
$n->addActionItemArray($actionEdit);
$n->setParamInfo($params);

$n->start = 0;
$n->display();
?>
