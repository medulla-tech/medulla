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

$ids = $col1 = $descriptions = [];
$actionDelete = [];
$params = [];

foreach ($configs as $index => $cfg) {
    $id = 'cfg_' . $index;
    $ids[] = $id;

    $cfgId = $cfg['id'] ?? '';
    $name = htmlspecialchars($cfg['name'] ?? 'Unnamed');
    $desc = htmlspecialchars($cfg['description'] ?? '-');

    $col1[] = "<a href='#' class='cfglink'>{$name}</a>";
    $descriptions[] = $desc;

        // Build ActionPopupItem (Delete)
        $actionDelete[] = new ActionPopupItem(_("Delete Configuration"), "deleteConfiguration", "delete", "", "mobile", "mobile");
        $params[] = [
            'id' => $cfgId,
            'name' => $name,
        ];
}

$n = new OptimizedListInfos($col1, _T("Configuration", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

// navbar
$count = safeCount($col1);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($descriptions, _T("Description", "mobile"));
// Attach actions
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();

?>
