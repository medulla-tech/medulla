<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? trim($_GET['filter']) : '';

$result = xmlrpc_list_photos($filter, null, null, 0, 50);

$photos = array();
if (is_array($result) && isset($result['items'])) {
    $photos = $result['items'];
}

$ids = $thumbnails = $devices = $filenames = $dates = $locations = [];
$actionDelete = [];
$params = [];

foreach ($photos as $index => $photo) {
    $photoId = $photo['id'] ?? '';
    $deviceNumber = htmlspecialchars($photo['deviceNumber'] ?? '');
    $originalName = htmlspecialchars($photo['originalName'] ?? '');
    $uploadTs = isset($photo['uploadTs']) ? (is_string($photo['uploadTs']) ? intval($photo['uploadTs']) : intval($photo['uploadTs'])) : 0;
    $lat = $photo['lat'] ?? null;
    $lon = $photo['lon'] ?? null;
    $address = htmlspecialchars($photo['address'] ?? '');

    $id = 'photo_' . $index;
    $ids[] = $id;

    $thumbUrl = urlStrRedirect("mobile/mobile/photoFile", array('id' => $photoId, 'thumb' => '1'));
    $fullUrl = urlStrRedirect("mobile/mobile/photoFile", array('id' => $photoId));

    $thumbnails[] = sprintf(
        '<a href="%s" target="_blank"><img src="%s" style="max-width: 80px; max-height: 60px; border: 1px solid #ddd; border-radius: 3px;" /></a>',
        $fullUrl,
        $thumbUrl
    );

    $devices[] = $deviceNumber;
    $filenames[] = $originalName;

    if ($uploadTs > 0) {
        $dateStr = date('Y-m-d H:i:s', $uploadTs / 1000);
        $dates[] = $dateStr;
    } else {
        $dates[] = '-';
    }

    if ($lat !== null && $lon !== null) {
        $location = sprintf('%s (%.4f, %.4f)', $address ?: _T("Unknown location", "mobile"), $lat, $lon);
    } else {
        $location = '-';
    }
    $locations[] = $location;

    $actionDelete[] = new ActionPopupItem(_T("Delete", "mobile"), "deletePhoto", "delete", "id", "mobile", "mobile", null, 500);

    $params[] = array('id' => $photoId);
}

$n = new OptimizedListInfos($thumbnails, _T("Preview", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$count = safeCount($photos);
$filter_val = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : '';
$n->setNavBar(new AjaxNavBar($count, $filter_val));

$n->addExtraInfo($devices, _T("Device", "mobile"));
$n->addExtraInfo($filenames, _T("File name", "mobile"));
$n->addExtraInfo($dates, _T("Upload date", "mobile"));
$n->addExtraInfo($locations, _T("Location", "mobile"));
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();
?>
