<?php
require_once("modules/mobile/includes/xmlrpc.php");

$files = xmlrpc_get_hmdm_files();
if (!is_array($files)) $files = [];

$ids = $col1 = $descriptions = $sizes = $updated = $devicePaths = $externals = $variables = $actions = [];

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

	$deleteUrl = urlStrRedirect("mobile/mobile/deleteFile", array('action' => 'deleteFile', 'id' => $fileId, 'name' => $name));
	$actions[] = "<ul class='action' style='list-style-type: none; padding: 0; margin: 0; display: flex; gap: 8px; align-items: center;'><li class='delete'><a href='{$deleteUrl}' class='delete-link' data-id='{$fileId}' title='Delete'>" . _T("", "mobile") . "</a></li></ul>";
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
$n->addExtraInfo($actions, _T("Actions", "mobile"));

$n->start = 0;
$n->display();

?>
