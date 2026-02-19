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
$sectionFilter = isset($_GET['section']) ? trim((string)$_GET['section']) : '';
$entryPatternsRaw = isset($_GET['entry_patterns']) ? trim((string)$_GET['entry_patterns']) : '';

$entryPatterns = [];
if ($entryPatternsRaw !== '') {
    $b64 = strtr($entryPatternsRaw, '-_', '+/');
    $padLength = strlen($b64) % 4;
    if ($padLength > 0) {
        $b64 .= str_repeat('=', 4 - $padLength);
    }

    $decoded = base64_decode($b64, true);
    if ($decoded === false) {
        $decoded = base64_decode($entryPatternsRaw, true);
    }

    if ($decoded !== false) {
        $decodedPatterns = json_decode($decoded, true);
        if (is_array($decodedPatterns)) {
            foreach ($decodedPatterns as $pattern) {
                if (!is_string($pattern)) {
                    continue;
                }
                $pattern = trim($pattern);
                if ($pattern === '' || strlen($pattern) > 256) {
                    continue;
                }
                if (@preg_match($pattern, '') === false) {
                    continue;
                }
                $entryPatterns[] = $pattern;
                if (count($entryPatterns) >= 40) {
                    break;
                }
            }
        }
    }
}

if ($sectionFilter !== '') {
    $config_data = array_filter($config_data, function ($row) use ($sectionFilter) {
        $section = trim((string)($row['section'] ?? ''));
        return strcasecmp($section, $sectionFilter) === 0;
    });
}

if (!empty($entryPatterns)) {
    $config_data = array_filter($config_data, function ($row) use ($entryPatterns, $table) {
        $section = trim((string)($row['section'] ?? ''));
        $name = trim((string)($row['nom'] ?? ''));

        foreach ($entryPatterns as $pattern) {
            if (preg_match($pattern, $name) === 1) {
                return true;
            }
            if (preg_match($pattern, $section) === 1) {
                return true;
            }
            if (preg_match($pattern, $table) === 1) {
                return true;
            }
        }

        return false;
    });
}

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