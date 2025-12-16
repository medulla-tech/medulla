<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get filter parameter
$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

$files = xmlrpc_get_hmdm_files();
if (!is_array($files)) $files = [];

// Filter by file name if filter is provided
if (!empty($filter)) {
    $files = array_filter($files, function($file) use ($filter) {
        $fileName = basename($file['filePath'] ?? '');
        return stripos($fileName, $filter) !== false;
    });
}

$ids = $col1 = $descriptions = $sizes = $updated = $devicePaths = $externals = $variables = [];
$actionDelete = [];
$params = [];

foreach ($files as $index => $file) {
	$id = 'file_' . $index;
	$ids[] = $id;

	$fileId = $file['id'] ?? '';
	$name = htmlspecialchars(basename($file['filePath'] ?? ''));
	$desc = htmlspecialchars($file['description'] ?? '-');
	$size = $file['size'].' Mb' ?? '';
	$uploadTime = isset($file['uploadTime']) ? date('Y-m-d H:i:s', intval($file['uploadTime'])) : '';
	$devicePath = htmlspecialchars($file['devicePath'] ?? '');
	$external = !empty($file['external']) ? 'Yes' : 'No';
	$variable = !empty($file['replaceVariables']) ? 'Yes' : 'No';

	$col1[] = "<a href='#' class='filelink'>{$name}</a>";
	$descriptions[] = $desc;
	$sizes[] = $size;
	$updated[] = $uploadTime;
	$devicePaths[] = $devicePath;
	$externals[] = $external;
	$variables[] = $variable;

	// Build ActionPopupItem (Delete)
	$actionDelete[] = new ActionPopupItem(_("Delete File"), "deleteFile", "delete", "", "mobile", "mobile");
	$params[] = [
		'id' => $fileId,
		'name' => $name,
	];
}

$n = new OptimizedListInfos($col1, _T("File", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

// navbar
$count = safeCount($col1);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($descriptions, _T("Description", "mobile"));
$n->addExtraInfo($sizes, _T("Size", "mobile"));
$n->addExtraInfo($updated, _T("Updated at", "mobile"));
$n->addExtraInfo($devicePaths, _T("Path on device", "mobile"));
$n->addExtraInfo($externals, _T("External", "mobile"));
$n->addExtraInfo($variables, _T("Variable", "mobile"));
// Attach actions
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();

?>
