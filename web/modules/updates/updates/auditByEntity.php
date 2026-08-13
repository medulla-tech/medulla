<?php 

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/updates/includes/xmlrpc.php");

$completename = htmlentities($_GET['completename']) ?? '';
$historyType = isset($_GET['history_type']) ? htmlentities($_GET['history_type']) : '';
if ($historyType === 'linux_updates') {
	$pageTitle = _T("Linux updates history for entity %s", 'updates');
} elseif ($historyType === 'windows_updates') {
	$pageTitle = _T("Windows updates history for entity %s", 'updates');
} else {
	$pageTitle = _T("Updates history for entity %s", 'updates');
}

$p = new PageGenerator(sprintf($pageTitle, $completename));
$p->setSideMenu($sidemenu);

$p->display();
$params = ['entity' => $_GET['entity'], 'completename' => $_GET['completename']];
if ($historyType !== '') {
	$params['history_type'] = $historyType;
}
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxAuditByEntity"), "container", $params, 'form');
$ajax->display();
$ajax->displayDivToUpdate();
?>