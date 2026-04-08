<?php
require_once("modules/mobile/includes/xmlrpc.php");

$device_number = isset($_GET['device']) ? $_GET['device'] : '';

if (empty($device_number)) {
    echo '<p style="color:red;font-family:sans-serif;padding:20px;">Missing device number.</p>';
    exit;
}

$session = xmlrpc_start_remote_control_session($device_number);

if (empty($session) || empty($session['id']) || empty($session['token'])) {
    echo '<p style="color:red;font-family:sans-serif;padding:20px;">Failed to start remote control session. The device may be offline or the remote control plugin is not enabled.</p>';
    exit;
}

$session_id = $session['id'];
$token = $session['token'];
$protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
$embed_url = $protocol . '://' . $host . '/hmdm/remotecontrol-embed.html?sessionId=' . urlencode($session_id) . '&token=' . urlencode($token);
$stop_url = 'main.php?module=mobile&submod=mobile&action=remoteControlStop&session_id=' . urlencode($session_id);
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #1a1a1a; display: flex; flex-direction: column; height: 100vh; font-family: sans-serif; }
#rc-header { background: #2c2c2c; color: #ccc; padding: 6px 10px; font-size: 12px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
#rc-header span { font-weight: bold; color: #fff; }
#rc-stop { background: #c0392b; color: #fff; border: none; padding: 4px 12px; border-radius: 3px; cursor: pointer; font-size: 12px; }
#rc-stop:hover { background: #e74c3c; }
#rc-frame { flex: 1; border: none; width: 100%; }
</style>
</head>
<body>
<div id="rc-header">
    <span><?php echo htmlspecialchars($device_number); ?></span>
    <button id="rc-stop" onclick="stopSession()"><?php echo _T("Stop", "mobile"); ?></button>
</div>
<iframe id="rc-frame" src="<?php echo htmlspecialchars($embed_url); ?>" allowfullscreen></iframe>
<script>
var sessionStopped = false;

function stopSession() {
    if (sessionStopped) return;
    sessionStopped = true;
    fetch('<?php echo $stop_url; ?>', { method: 'GET', keepalive: true });
    window.close();
}

window.addEventListener('beforeunload', function() {
    if (!sessionStopped) {
        navigator.sendBeacon('<?php echo $stop_url; ?>');
    }
});
</script>
</body>
</html>
