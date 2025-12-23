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
$actionModify = [];
$params = [];

foreach ($configs as $index => $cfg) {
    $id = 'cfg_' . $index;
    $ids[] = $id;

    $cfgId = $cfg['id'] ?? '';
    $name = htmlspecialchars($cfg['name'] ?? 'Unnamed');
    $desc = htmlspecialchars($cfg['description'] ?? '-');

    // Link to configuration details in-place (no new tab)
    $detailsUrl = urlStr("mobile/mobile/configurationDetails", array("id" => $cfgId));
    $col1[] = "<a href='" . htmlspecialchars($detailsUrl, ENT_QUOTES, 'UTF-8') . "' class='cfglink'>{$name}</a>";
    $descriptions[] = $desc;

        // Build Modify action (same tab)
        $actionModify[] = new ActionItem(_T("Modify", "mobile"), "configurationDetails", "edit", "id", "mobile", "mobile");

        // Build ActionPopupItem (Delete)
        $actionDelete[] = new ActionPopupItem(_T("Delete Configuration", "mobile"), "deleteConfiguration", "delete", "", "mobile", "mobile");

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
$n->addActionItemArray($actionModify);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();

?>
