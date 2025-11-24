<?php
require_once("modules/mobile/includes/xmlrpc.php");

$name = "";
$id = 0;

if (isset($_GET['name'])) {
	$name = htmlentities($_GET['name']);
}

if (isset($_GET['id'])) {
	$id = htmlentities($_GET['id']);
} else {
	new NotifyWidgetFailure(_T("Missing parameter id", "mobile"));
	header("location:" . urlStrRedirect("mobile/mobile/files"));
	exit;
}

if (isset($_GET['action']) && $_GET['action'] === 'deleteFile') {
	$result = xmlrpc_delete_file_by_id($_GET['id']);
		if ($result) {
		new NotifyWidgetSuccess(sprintf(_T("File %s successfully deleted", "mobile"), $name));
		header("location:" . urlStrRedirect("mobile/mobile/files"));
		exit;
	} else {
		new NotifyWidgetFailure(sprintf(_T("Impossible to delete file %s", "mobile"), $name));
		header("location:" . urlStrRedirect("mobile/mobile/files"));
		exit;
	}
}

?>
