<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

$files = xmlrpc_get_hmdm_files();
if (!is_array($files)) $files = [];

if (!empty($filter)) {
    $files = array_filter($files, function($file) use ($filter) {
        $fileName = basename($file['filePath'] ?? '');
        return stripos($fileName, $filter) !== false;
    });
}

$ids = $col1 = $descriptions = $sizes = $updated = $devicePaths = $externals = $variables = [];
$actionDelete = $actionEdit = [];
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

	$actionDelete[] = new ActionPopupItem(_("Delete File"), "deleteFile", "delete", "", "mobile", "mobile");
	$actionEdit[] = new ActionItem(_("Edit"), "modifyFile", "edit", "id", "mobile", "mobile");
	$actionConfig[] = new ActionItem(_("Assign Configurations"), "fileConfigurations", "config", "id", "mobile", "mobile");
	$params[] = [
		'id' => $fileId,
		'name' => $name,
		'filePath' => htmlspecialchars($file['filePath'] ?? ''),
		'devicePath' => $file['devicePath'] ?? '',
		'external' => !empty($file['external']) ? 1 : 0,
	];
}

$n = new OptimizedListInfos($col1, _T("File", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$count = safeCount($col1);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($descriptions, _T("Description", "mobile"));
$n->addExtraInfo($sizes, _T("Size", "mobile"));
$n->addExtraInfo($updated, _T("Updated at", "mobile"));
$n->addExtraInfo($devicePaths, _T("Path on device", "mobile"));
$n->addExtraInfo($externals, _T("External", "mobile"));
$n->addExtraInfo($variables, _T("Variable", "mobile"));
$n->addActionItemArray($actionEdit);
$n->addActionItemArray($actionConfig);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();
?>

<script>
var copySuccessMsg = <?php echo json_encode(_T("Link copied to clipboard!", "mobile")); ?>;

function copyFileLink(filePath) {
    navigator.clipboard.writeText(filePath).then(function() {
        // Show success notification
        var notification = jQuery('<div style="position:fixed;top:20px;right:20px;background:#8CB63C;color:white;padding:12px 20px;border-radius:4px;z-index:10000;box-shadow:0 2px 8px rgba(0,0,0,0.2);font-size:14px;">'+copySuccessMsg+'</div>');
        jQuery('body').append(notification);
        setTimeout(function() {
            notification.fadeOut(300, function() { jQuery(this).remove(); });
        }, 2000);
    })
}

jQuery(function() {
    var fileData = <?php 
        $fileDataArray = [];
        foreach ($files as $index => $file) {
            $fileDataArray['file_' . $index] = $file['url'] ?? '';
        }
        echo json_encode($fileDataArray); 
    ?>;
    
    jQuery.each(fileData, function(rowId, fileUrl) {
        var actionList = jQuery('#' + rowId + ' .action');
        if (actionList.length) {
            var copyBtn = '<li class="download"><a title="Copy Link" href="#" onclick="copyFileLink(\'' + fileUrl.replace(/'/g, "\\'") + '\'); return false;">&nbsp;</a></li>';
            actionList.find('li.edit').before(copyBtn);
        }
    });
});
</script>
