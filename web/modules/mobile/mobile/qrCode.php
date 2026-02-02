<?php
require_once("modules/mobile/includes/xmlrpc.php");

$deviceNumber = isset($_GET['device_number']) ? $_GET['device_number'] : '';
$configId = isset($_GET['configuration_id']) ? intval($_GET['configuration_id']) : 1;
$apkMode = isset($_GET['apk']);

function apkQrCacheDir() {
    return 'img/mobiles';
}

function apkQrCacheFilename($version) {
    return 'qr_hmdm_latest_' . $version . '.png';
}

function apkQrCachePath($version) {
    return apkQrCacheDir() . '/' . apkQrCacheFilename($version);
}

function apkQrPublicUrl($version) {
    return 'img/mobiles/' . apkQrCacheFilename($version);
}

function ensureApkQrCache($downloadUrl, $version) {
    $dir = apkQrCacheDir();
    $currentFile = apkQrCacheFilename($version);
    $currentPath = apkQrCachePath($version);
    $externalQRUrl = 'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=' . urlencode($downloadUrl);

    if (!is_dir($dir)) {
        return $externalQRUrl;
    }

    foreach (glob($dir . '/qr_hmdm_latest_*.png') ?: [] as $path) {
        if (basename($path) !== $currentFile) {
            @unlink($path);
        }
    }

    if (!file_exists($currentPath)) {
        $qrImageData = @file_get_contents($externalQRUrl);
        if ($qrImageData === false) {
            return $externalQRUrl;
        }
        if (@file_put_contents($currentPath, $qrImageData) === false) {
            return $externalQRUrl;
        }
    }

    return apkQrPublicUrl($version);
}

if ($apkMode) {
    $scheme = 'http';
    if (!empty($_SERVER['HTTP_X_FORWARDED_PROTO'])) {
        $scheme = $_SERVER['HTTP_X_FORWARDED_PROTO'];
    } elseif (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') {
        $scheme = 'https';
    } elseif (!empty($_SERVER['HTTP_REFERER'])) {
        $parsed = parse_url($_SERVER['HTTP_REFERER']);
        if (isset($parsed['scheme'])) {
            $scheme = $parsed['scheme'];
        }
    }
    
    $host = null;
    if (!empty($_SERVER['HTTP_X_FORWARDED_HOST'])) {
        $host = $_SERVER['HTTP_X_FORWARDED_HOST'];
    } elseif (!empty($_SERVER['HTTP_REFERER'])) {
        $parsed = parse_url($_SERVER['HTTP_REFERER']);
        if (isset($parsed['host'])) {
            $host = $parsed['host'];
        }
    }
    
    if (!$host) {
        $host = $_SERVER['HTTP_HOST'] ?? $_SERVER['SERVER_NAME'] ?? 'localhost';
    }
    
    $downloadUrl = $scheme . '://' . $host . '/downloads/android/hmdm-latest.apk';
    // version qr cache
    $APK_QR_VERSION = 3;

    $qrCodeUrl = ensureApkQrCache($downloadUrl, $APK_QR_VERSION);
    $pageTitle = _T("QR Code", "mobile") . ": hmdm-latest.apk";
    $subtitle = _T("Download agent", "mobile");
    $deviceLabel = $downloadUrl;
} else {
    if (!$deviceNumber) {
        echo "<p style='color: red; text-align: center;'>" . _T("Device number is required", "mobile") . "</p>";
        exit;
    }

    // fetch qr code
    $qrKey = xmlrpc_get_hmdm_configuration_by_id($configId);
    if (empty($qrKey) || !is_array($qrKey) || empty($qrKey['qrCodeKey'])) {
        echo "<p style='color: red; text-align: center;'>" . _T("Unable to retrieve QR code key for this configuration", "mobile") . "</p>";
        exit;
    }

    $qrCodeUrl = "/hmdm/rest/public/qr/" . urlencode($qrKey['qrCodeKey']) . "?deviceId=" . urlencode($deviceNumber);
    $pageTitle = _T("QR Code", "mobile") . ": " . htmlspecialchars($deviceNumber);
    $subtitle = _T("Scan this QR code with your mobile device to enroll", "mobile");
    $deviceLabel = htmlspecialchars($deviceNumber);
}
?>

<div style="display:flex; flex-direction:column; align-items:center;">
        <h1><?php echo $pageTitle; ?></h1>
        <?php if (!$apkMode): ?>
        <div style="margin-bottom: 15px; padding: 10px 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; color: #856404; max-width: 400px;">
            <strong><?php echo _T("Warning", "mobile"); ?>:</strong> <?php echo _T("This QR code can only be scanned during fresh installation of Android", "mobile"); ?>
        </div>
        <?php else: ?>
        <h2><?php echo _T("Device", "mobile"); ?>: <?php echo $deviceLabel; ?></h2>
        <?php endif; ?>
    
    <div style="text-align: center; padding: 10px 7px;">
        <img src="<?php echo htmlspecialchars($qrCodeUrl); ?>" 
             alt="<?php echo _T("QR Code", "mobile"); ?>" 
             style="width: 400px; aspect-ratio: 1 / 1; border: 3px solid #ddd; padding: 5px; background: white;" />
    </div>
    
    <p style="text-align: center; color: #666; font-size: 0.95em; margin-top: 10px;">
            <?php echo $subtitle; ?>
    </p>
</div>
