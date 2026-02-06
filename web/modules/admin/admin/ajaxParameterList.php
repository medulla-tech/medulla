<?php
require_once("modules/admin/includes/xmlrpc.php");

// Get table parameter
$table = isset($_GET['table']) ? preg_replace('/[^a-zA-Z0-9_]/', '', $_GET['table']) : '';

if (empty($table)) {
    echo json_encode(['error' => 'Invalid table name']);
    exit;
}

// Fetch config data
$config_data = xmlrpc_get_config_data($table);

if (!$config_data || !is_array($config_data)) {
    $config_data = [];
}

// Get filter if any
$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

// Filter data if needed (e.g., by section or name)
if (!empty($filter)) {
    $config_data = array_filter($config_data, function($row) use ($filter) {
        $section = $row['section'] ?? '';
        $nom = $row['nom'] ?? '';
        return stripos($section, $filter) !== false || stripos($nom, $filter) !== false;
    });
}

$ids = $sections = $params = $enableds = $values = $defaults = $descriptions = [];
$actionEdit = [];
$actionDelete = [];
$paramsArray = [];

foreach ($config_data as $index => $row) {
    $id = 'config_' . $index;
    $ids[] = $id;

    $section = htmlspecialchars($row['section'] ?? '');
    $param_name = htmlspecialchars($row['nom'] ?? '');
    $is_enabled = htmlspecialchars($row['activer'] ?? '');
    $value = htmlspecialchars($row['valeur'] ?? '');
    $default_value = htmlspecialchars($row['valeur_defaut'] ?? '');
    $description = htmlspecialchars($row['description'] ?? '');

    $sections[] = $section;
    $params[] = $param_name;
    $enableds[] = $is_enabled;
    $values[] = $value;
    $defaults[] = $default_value;
    $descriptions[] = $description;

    // Actions
    $actionEdit[] = new ActionItem(_("Edit Parameter"), "editParameter", "edit", "", "admin", "admin");
    $actionDelete[] = new ActionItem(_("Delete Parameter"), "deleteParameter", "delete", "", "admin", "admin");

    $paramsArray[] = [
        'table' => $table,
        'section' => $row['section'] ?? '',
        'nom' => $row['nom'] ?? '',
    ];
}

$n = new OptimizedListInfos($sections, _T("Section", "admin"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$count = safeCount($sections);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($params, _T("Parameter", "admin"));
$n->addExtraInfo($enableds, _T("Enabled", "admin"));
$n->addExtraInfo($values, _T("Value", "admin"));
$n->addExtraInfo($defaults, _T("Default Value", "admin"));
$n->addExtraInfo($descriptions, _T("Description", "admin"));

$n->addActionItemArray($actionEdit);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($paramsArray);

$n->start = 0;
$n->display();

?>