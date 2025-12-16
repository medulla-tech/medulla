<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get filter parameter
$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

// Fetch applications from HMDM via xmlrpc wrapper
$apps = xmlrpc_get_hmdm_applications();

if (!is_array($apps)) $apps = [];

// Filter by application name if filter is provided
if (!empty($filter)) {
    $apps = array_filter($apps, function($app) use ($filter) {
        $appName = $app['name'] ?? '';
        return stripos($appName, $filter) !== false;
    });
}

$ids = $col1 = $packages = $versions = $urls = [];
$actionDelete = [];
$params = [];

foreach ($apps as $index => $app) {
	$id = 'app_' . $index;
	$ids[] = $id;

	$appId = $app['id'] ?? '';
	$name = htmlspecialchars($app['name'] ?? 'Unnamed');
	$package = htmlspecialchars($app['pkg'] ?? '-');
	$version = htmlspecialchars($app['version'] ?? '-');
	$url = htmlspecialchars($app['url'] ?? '');

	$col1[] = "<a href='#' class='applink'>{$name}</a>";
	$packages[] = $package;
	$versions[] = $version;
	$urls[] = $url;

	// Build ActionPopupItem (Delete) using standard action API
	$actionDelete[] = new ActionPopupItem(_("Delete Application"), "deleteApplication", "delete", "", "mobile", "mobile");
	$params[] = [
		'id' => $appId,
		'name' => $name,
	];
}

$n = new OptimizedListInfos($col1, _T("Application name", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

// Prepare navigation bar (required by ListInfos display)
$count = safeCount($col1);
$filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->addExtraInfo($packages, _T("Package ID", "mobile"));
$n->addExtraInfo($versions, _T("Version", "mobile"));
$n->addExtraInfo($urls, _T("URL", "mobile"));
// Attach actions
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();

?>
