<?php
require("graph/navbar.inc.php");
require("localSidebar.php");


$p = new PageGenerator(_T("List of all devices", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

echo '<button class="btn btn-small btn-primary" onclick="PopupWindow(event, \'main.php?module=mobile&submod=mobile&action=qrCode&apk=1\', 300); return false;" type="button">'._T("HMDM APK","mobile").'</button>';

// Display notifications for QR errors
if (isset($_GET['error'])) {
	switch ($_GET['error']) {
		case 'missing_device_number':
			new NotifyWidgetFailure(_T('Missing device number for QR Code', 'mobile'));
			break;
		case 'qr_key_missing':
			new NotifyWidgetFailure(_T('Unable to fetch configuration QR key', 'mobile'));
			break;
		default:
			new NotifyWidgetFailure(_T('Unable to load QR Code', 'mobile'));
			break;
	}
}


$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxDeviceList"));
$ajax->display();
$ajax->displayDivToUpdate();

?>