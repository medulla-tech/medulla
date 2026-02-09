<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

$configs = xmlrpc_get_hmdm_configurations();
if (!is_array($configs)) $configs = [];

if (!empty($filter)) {
    $configs = array_filter($configs, function($cfg) use ($filter) {
        $cfgName = $cfg['name'] ?? '';
        return stripos($cfgName, $filter) !== false;
    });
}

$ids = $col1 = $descriptions = [];
$actionDelete = [];
$actionModify = [];
$actionDuplicate = [];
$params = [];

foreach ($configs as $index => $cfg) {
    $id = 'cfg_' . $index;
    $ids[] = $id;

    $cfgId = $cfg['id'] ?? '';
    $name = htmlspecialchars($cfg['name'] ?? 'Unnamed');
    $desc = htmlspecialchars($cfg['description'] ?? '-');

    $col1[] = "<a href='" . htmlspecialchars($detailsUrl, ENT_QUOTES, 'UTF-8') . "' class='cfglink'>{$name}</a>";
    $descriptions[] = $desc;

    $actionModify[] = new ActionItem(_T("Modify", "mobile"), "configurationDetails", "edit", "id", "mobile", "mobile");
    $actionDuplicate[] = new ActionItem(_T("Duplicate", "mobile"), "duplicateConfiguration", "duplicatescript", "id", "mobile", "mobile");
    $actionDelete[] = new ActionPopupItem(_T("Delete Configuration", "mobile"), "deleteConfiguration", "delete", "", "mobile", "mobile");

    $params[] = [
            'id' => $cfgId,
            'name' => $name,
        ];
}

$n = new OptimizedListInfos($col1, _T("Configuration", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$count = safeCount($col1);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($descriptions, _T("Description", "mobile"));
$n->addActionItemArray($actionModify);
$n->addActionItemArray($actionDuplicate);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();

?>
