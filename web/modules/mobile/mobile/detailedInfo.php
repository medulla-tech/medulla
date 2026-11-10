<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Detailed Information", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$device_number = isset($_POST['device']) ? $_POST['device'] : (isset($_GET['device']) ? $_GET['device'] : "");
$device_info = array();

if ((isset($_POST['search']) || isset($_GET['device'])) && $device_number) {
    $device_info = xmlrpc_get_hmdm_detailed_info($device_number);
}

$dynData = isset($device_info['latestDynamicData']) ? $device_info['latestDynamicData'] : [];
$hasGPS = !empty($dynData['gpsLat']) && !empty($dynData['gpsLon']);
?>

<?php if ($hasGPS): ?>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<?php endif; ?>

<form method="post" name="searchform">
    <div class="searchbox">
        <span class="searchfield">
            <input type="text" class="searchfieldreal" name="device" id="device"
                placeholder="<?php echo _T("Search device...", "mobile"); ?>"
                value="<?php echo htmlspecialchars($device_number); ?>"
                autocomplete="off">
            <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'base'); ?>"
                onclick="document.getElementById('device').value=''; pushSearch();"></button>
        </span>
        <button type="submit" name="search" value="1" class="btn btn-primary"><?php echo _T("Search", "mobile"); ?></button>
        <ul id="device-suggestions" style="position: absolute; top: 100%; left: 0; width: 370px; max-height: 200px; overflow-y: auto; background: white; border: 1px solid #ccc; list-style: none; padding: 0; margin: 5px 0 0 0; display: none; z-index: 1000;"></ul>
    </div>
</form>

<?php if (!empty($device_info)): ?>

<?php
// --- Device info table ---
$keys = [];
$vals = [];

$keys[] = _T("Time", "mobile");                $vals[] = date('Y-m-d H:i:s');
$keys[] = _T("Device number", "mobile");        $vals[] = htmlspecialchars($device_info['deviceNumber'] ?? '');
$keys[] = _T("Description", "mobile");          $vals[] = htmlspecialchars($device_info['description'] ?? '');
$keys[] = _T("Groups", "mobile");               $vals[] = !empty($device_info['groups']) ? htmlspecialchars(implode(', ', $device_info['groups'])) : '';
$keys[] = _T("IMEI", "mobile");                 $vals[] = htmlspecialchars($device_info['imei'] ?? '');
$keys[] = _T("Phone", "mobile");                $vals[] = htmlspecialchars($device_info['phone'] ?? '');
$keys[] = _T("ICCID", "mobile");                $vals[] = htmlspecialchars($device_info['iccid'] ?? '');
$keys[] = _T("Serial number", "mobile");        $vals[] = htmlspecialchars($device_info['serial'] ?? '');
$keys[] = _T("CPU architecture", "mobile");     $vals[] = htmlspecialchars($device_info['cpuArch'] ?? '');
$keys[] = _T("Model", "mobile");                $vals[] = htmlspecialchars($device_info['model'] ?? '');
$keys[] = _T("OS version", "mobile");           $vals[] = htmlspecialchars($device_info['osVersion'] ?? '');
$keys[] = _T("Battery charge", "mobile");       $vals[] = htmlspecialchars($device_info['battery'] ?? '');
$keys[] = _T("MDM mode", "mobile");             $vals[] = htmlspecialchars($device_info['mdmMode'] ?? '');
$keys[] = _T("Kiosk mode", "mobile");           $vals[] = htmlspecialchars($device_info['kioskMode'] ?? '');
$keys[] = _T("Launcher variant", "mobile");     $vals[] = htmlspecialchars($device_info['launcherVariant'] ?? '');
$keys[] = _T("Default launcher", "mobile");     $vals[] = htmlspecialchars($device_info['defaultLauncher'] ?? '');
$keys[] = _T("Admin permission", "mobile");     $vals[] = !empty($device_info['adminPermission'])        ? _T("yes", "mobile") : _T("no", "mobile");
$keys[] = _T("Overlay permission", "mobile");   $vals[] = !empty($device_info['overlapPermission'])      ? _T("yes", "mobile") : _T("no", "mobile");
$keys[] = _T("History permission", "mobile");   $vals[] = !empty($device_info['historyPermission'])      ? _T("yes", "mobile") : _T("no", "mobile");
$keys[] = _T("Accessibility permission", "mobile"); $vals[] = !empty($device_info['accessibilityPermission']) ? _T("yes", "mobile") : _T("no", "mobile");

$n = new ListInfos($keys, _T("Property", "mobile"));
$n->addExtraInfo($vals, _T("Value", "mobile"));
$n->setRowsPerPage(count($keys));
$n->drawTable(0);
?>

<?php if ($hasGPS): ?>
<br/>
<h2><?php echo _T("GPS Location", "mobile"); ?></h2>
<?php
$gkeys = [];
$gvals = [];
$gkeys[] = _T("GPS Status", "mobile");   $gvals[] = htmlspecialchars($dynData['gpsState'] ?? '');
$gkeys[] = _T("GPS Enabled", "mobile");  $gvals[] = !empty($dynData['deviceGpsEnabled']) ? _T("yes", "mobile") : _T("no", "mobile");
$gkeys[] = _T("Latitude", "mobile");     $gvals[] = htmlspecialchars($dynData['gpsLat']);
$gkeys[] = _T("Longitude", "mobile");    $gvals[] = htmlspecialchars($dynData['gpsLon']);
$gkeys[] = _T("Altitude (m)", "mobile"); $gvals[] = htmlspecialchars($dynData['gpsAlt'] ?? '');
$gkeys[] = _T("Speed (m/s)", "mobile");  $gvals[] = htmlspecialchars($dynData['gpsSpeed'] ?? '');
$gkeys[] = _T("Course (°)", "mobile");   $gvals[] = htmlspecialchars($dynData['gpsCourse'] ?? '');

$g = new ListInfos($gkeys, _T("Property", "mobile"));
$g->addExtraInfo($gvals, _T("Value", "mobile"));
$g->setRowsPerPage(count($gkeys));
$g->drawTable(0);
?>
<div id="map" style="width: 100%; height: 400px; margin-top: 16px;"></div>
<?php endif; ?>

<?php if (!empty($device_info['applications'])): ?>
<br/>
<h2><?php echo _T("Installation status", "mobile"); ?></h2>
<?php
$appNames    = [];
$appPkgs     = [];
$appInstalled = [];
$appRequired  = [];

foreach ($device_info['applications'] as $app) {
    $appNames[]     = htmlspecialchars($app['applicationName'] ?? '');
    $appPkgs[]      = htmlspecialchars($app['applicationPkg'] ?? '');
    $appInstalled[] = htmlspecialchars($app['versionInstalled'] ?? '');
    $appRequired[]  = htmlspecialchars($app['versionRequired'] ?? '');
}

$a = new OptimizedListInfos($appNames, _T("Title", "mobile"));
$a->addExtraInfo($appPkgs,      _T("Package ID", "mobile"));
$a->addExtraInfo($appInstalled, _T("Installed version", "mobile"));
$a->addExtraInfo($appRequired,  _T("Required version", "mobile"));
$a->setItemCount(count($appNames));
$a->start = 0;
$a->end   = count($appNames);
$a->disableFirstColumnActionLink();
$a->display(false, false);
?>
<?php endif; ?>

<?php elseif (isset($_POST['search'])): ?>
    <p><?php echo _T("No information found for this device", "mobile"); ?></p>
<?php endif; ?>

<script type="text/javascript">
var autocompleteTimeout;

document.getElementById('device').addEventListener('input', function(e) {
    clearTimeout(autocompleteTimeout);
    var query = e.target.value;
    var suggestionsList = document.getElementById('device-suggestions');

    if (query.length < 1) {
        suggestionsList.style.display = 'none';
        return;
    }

    autocompleteTimeout = setTimeout(function() {
        fetch('<?php echo urlStrRedirect("mobile/mobile/ajaxDeviceSearch"); ?>&filter=' + encodeURIComponent(query))
            .then(function(r) { return r.json(); })
            .then(function(data) {
                suggestionsList.innerHTML = '';
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(function(device) {
                        var li = document.createElement('li');
                        li.style.padding = '8px 12px';
                        li.style.cursor = 'pointer';
                        li.style.borderBottom = '1px solid #eee';
                        var deviceName = device.name || '';
                        li.textContent = deviceName;
                        li.title = deviceName;
                        li.onmouseover = function() { li.style.backgroundColor = '#f0f0f0'; };
                        li.onmouseout  = function() { li.style.backgroundColor = 'white'; };
                        li.onclick = function() {
                            document.getElementById('device').value = deviceName;
                            suggestionsList.style.display = 'none';
                        };
                        suggestionsList.appendChild(li);
                    });
                    suggestionsList.style.display = 'block';
                } else {
                    suggestionsList.style.display = 'none';
                }
            })
            .catch(function() { suggestionsList.style.display = 'none'; });
    }, 300);
});

document.addEventListener('click', function(e) {
    if (e.target.id !== 'device') {
        document.getElementById('device-suggestions').style.display = 'none';
    }
});

function pushSearch() {
    document.querySelector('form[name="searchform"]').submit();
}
</script>

<?php if (!empty($device_info) && $hasGPS): ?>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('map').setView([<?php echo (float)$dynData['gpsLat']; ?>, <?php echo (float)$dynData['gpsLon']; ?>], 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
L.marker([<?php echo (float)$dynData['gpsLat']; ?>, <?php echo (float)$dynData['gpsLon']; ?>]).addTo(map)
    .bindPopup('<?php echo htmlspecialchars($device_info['deviceNumber'] ?? ''); ?>');
</script>
<?php endif; ?>
