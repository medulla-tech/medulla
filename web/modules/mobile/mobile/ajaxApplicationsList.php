<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get filter parameter
$filter     = isset($_GET['filter'])      ? $_GET['filter']      : '';
$field      = isset($_GET['field'])       ? trim($_GET['field']) : 'all';
$showSystem = isset($_GET['show_system']) ? $_GET['show_system'] : '0';

$apps = xmlrpc_get_hmdm_applications();

if (!is_array($apps)) $apps = [];

// Filter out system apps unless requested
if ($showSystem !== '1') {
    $apps = array_filter($apps, function($app) {
        return empty($app['system']);
    });
}

if (!empty($filter)) {
    $apps = array_filter($apps, function($app) use ($filter, $field) {
        if ($field === 'package') {
            return stripos($app['pkg'] ?? '', $filter) !== false;
        }
        if ($field === 'version') {
            return stripos((string)($app['version'] ?? ''), $filter) !== false;
        }
        return stripos($app['name'] ?? '', $filter) !== false
            || ($field === 'all' && stripos($app['pkg'] ?? '', $filter) !== false);
    });
}

$apps = array_values($apps);

$ids = $col1 = $packages = $versions = $urls = [];
$actionEdit = [];
$actionVersions = [];
$actionDelete = [];
$params = [];
$totalCount = safeCount($apps);

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

        $actionEdit[] = new ActionItem(_("Edit Application"), "editApplication", "edit", "", "mobile", "mobile");
        $actionVersions[] = new ActionItem(_("Versions"), "applicationVersions", "history", "", "mobile", "mobile");
        $actionDelete[] = new ActionPopupItem(_("Delete Application"), "deleteApplication", "delete", "", "mobile", "mobile", null, 500);
        $params[] = [
                'id' => $appId,
                'name' => $name,
        ];
}

$n = new OptimizedListInfos($col1, _T("Application name", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$n->setNavBar(new AjaxNavBar($totalCount, $filter));
$n->setItemCount($totalCount);

$n->addExtraInfo($packages, _T("Package ID", "mobile"));
$n->addExtraInfo($versions, _T("Version", "mobile"));
$n->addExtraInfo($urls, _T("URL", "mobile"));
$n->addActionItemArray($actionEdit);
$n->addActionItemArray($actionVersions);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->display();

?>