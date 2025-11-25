<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Fetch applications from HMDM via xmlrpc wrapper
$apps = xmlrpc_get_hmdm_applications();

if (!is_array($apps)) $apps = [];

$ids = $col1 = $packages = $versions = $urls = $actions = [];

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

	// Action: Delete (server-side via xmlrpc wrapper for security/consistency)
	$deleteUrl = urlStrRedirect("mobile/mobile/deleteApplication", array('action' => 'deleteApplication', 'id' => $appId, 'name' => $name));
	$actions[] = "<ul class='action' style='list-style-type: none; padding: 0; margin: 0; display: flex; gap: 8px; align-items: center;'>
		<li class='delete'><a href='{$deleteUrl}' class='delete-link' data-id='{$appId}' title='Supprimer'>" . _T("", "mobile") . "</a></li>
	</ul>";
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
$n->addExtraInfo($actions, _T("Actions", "mobile"));

$n->start = 0;
$n->display();

?>
