<?php
require_once("modules/mobile/includes/xmlrpc.php");

$photoId = isset($_GET['id']) ? intval($_GET['id']) : 0;
$isThumb = isset($_GET['thumb']) && $_GET['thumb'] === '1';

if ($photoId <= 0) {
    header("HTTP/1.0 400 Bad Request");
    echo "Invalid photo ID";
    exit;
}

$result = xmlrpc_get_photo_file($photoId, $isThumb);

if (!$result || !isset($result['content'], $result['contentType'])) {
    header("HTTP/1.0 404 Not Found");
    echo "Photo not found";
    exit;
}

header('Content-Type: ' . $result['contentType']);
header('Cache-Control: public, max-age=3600');

echo base64_decode($result['content']);
exit;
?>
