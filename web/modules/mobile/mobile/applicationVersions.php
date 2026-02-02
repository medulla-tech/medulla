<?php
/**
 * Application Versions page
 * Display all versions of a specific application
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$appId = isset($_GET['id']) ? intval($_GET['id']) : 0;
$appName = isset($_GET['name']) ? htmlentities($_GET['name']) : '';

if (!$appId) {
    new NotifyWidgetFailure(_T("Application ID is required", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/applications"));
    exit;
}

// Fetch versions
$versions = xmlrpc_get_application_versions($appId);

$p = new PageGenerator(sprintf(_T("Versions of %s", "mobile"), $appName));
$p->setSideMenu($sidemenu);
$p->display();

if (!is_array($versions) || empty($versions)) {
    echo '<div class="alert alert-info">' . _T("No versions found for this application", "mobile") . '</div>';
    echo '<div style="margin-top: 20px;">';
    echo '<a href="' . urlStrRedirect("mobile/mobile/applications") . '" class="btn btn-primary">' . _T("Back to Applications", "mobile") . '</a>';
    echo '</div>';
} else {
    $ids = $versionIds = $versionNames = $versionCodes = $archs = $urls = $dates = [];
    
    foreach ($versions as $index => $version) {
        $id = 'version_' . $index;
        $ids[] = $id;
        
        $versionIds[] = htmlspecialchars($version['id'] ?? '');
        $versionNames[] = htmlspecialchars($version['version'] ?? '-');
        $versionCodes[] = htmlspecialchars($version['versionCode'] ?? '-');
        $archs[] = htmlspecialchars($version['arch'] ?? 'Universal');
        
        $urlVal = '';
        if (!empty($version['url'])) {
            $urlVal = '<a href="' . htmlspecialchars($version['url']) . '" target="_blank">' . htmlspecialchars($version['url']) . '</a>';
        }
        $urls[] = $urlVal;
        
        $dateVal = '';
        if (!empty($version['ts'])) {
            $dateVal = date('Y-m-d H:i:s', $version['ts'] / 1000);
        }
        $dates[] = $dateVal;
    }
    
    $n = new OptimizedListInfos($versionIds, _T("Version ID", "mobile"));
    $n->setCssIds($ids);
    $n->disableFirstColumnActionLink();
    
    $n->addExtraInfo($versionNames, _T("Version", "mobile"));
    $n->addExtraInfo($versionCodes, _T("Version Code", "mobile"));
    $n->addExtraInfo($urls, _T("URL", "mobile"));

    $filter = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : "";
    $n->setNavBar(new AjaxNavBar(safeCount($versionIds), $filter));
    $n->start = 0;
    $n->end = safeCount($versionIds);
    
    print '<div style="margin-bottom: 15px;">';
    print '<a href="' . urlStrRedirect("mobile/mobile/applications") . '" class="btn btn-primary">' . _T("Back to Applications", "mobile") . '</a>';
    print '</div>';
    
    $n->display();
}
?>