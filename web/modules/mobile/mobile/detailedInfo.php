<?php
require_once("modules/mobile/includes/xmlrpc.php");

$device_number = isset($_POST['device']) ? $_POST['device'] : (isset($_GET['device']) ? $_GET['device'] : "");
$device_info = array();

if ((isset($_POST['search']) || isset($_GET['device'])) && $device_number) {
    $device_info = xmlrpc_get_hmdm_detailed_info($device_number);
}

?>

<h3><?php echo _T("Detailed Device Information", "mobile"); ?></h3>
<p><?php echo _T("Search for a device and view its detailed information", "mobile"); ?></p>

<form method="post" name="searchform">
    <table>
        <tr>
            <td>
                <div id="searchBest" style="width:370px; position: relative; justify-self:end;">
                    <input type="text" class="searchfieldreal" name="device" id="device" placeholder="<?php echo _T("Search device...", "mobile"); ?>" value="<?php echo htmlspecialchars($device_number); ?>" autocomplete="off">

                    <button type="button" class="search-clear" onclick="document.getElementById('device').value=''; pushSearch();">
                    </button>

                    <button type="submit" name="search" value="1"><?php echo _T("Search", "mobile"); ?></button>
                    
                    <ul id="device-suggestions" style="position: absolute; top: 100%; left: 0; width: 100%; max-height: 200px; overflow-y: auto; background: white; border: 1px solid #ccc; list-style: none; padding: 0; margin: 5px 0 0 0; display: none; z-index: 1000;"></ul>
                </div>
            </td>
        </tr>
    </table>
</form>

<?php if (!empty($device_info)): ?>
    <div id='device-info-container' style="margin-top: 20px;">
        <table cellpadding="6" cellspacing="0" border="1" style="border-collapse: collapse; width: 100%; ">
            <tr><td colspan="2" style="background-color: #dadadaff; text-align: center; font-weight:bold;"><?php echo _T("Detailed Device Information", "mobile"); ?></td></tr>
            <tr><td><?php echo _T("Time", "mobile"); ?></td><td><?php echo date('Y-m-d H:i:s'); ?></td></tr>
            <tr><td><?php echo _T("Device number", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['deviceNumber'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Description", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['description'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Groups", "mobile"); ?></td><td><?php echo !empty($device_info['groups']) ? implode(', ', $device_info['groups']) : ''; ?></td></tr>
            <tr><td><?php echo _T("IMEI (required)", "mobile"); ?></td><td></td></tr>
            <tr><td><?php echo _T("IMEI", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['imei'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Phone (required)", "mobile"); ?></td><td></td></tr>
            <tr><td><?php echo _T("Phone", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['phone'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("ICCID", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['iccid'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Serial number", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['serial'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("CPU architecture", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['cpuArch'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Permission to install as device administrator", "mobile"); ?></td><td><?php echo $device_info['adminPermission'] ? _T("yes", "mobile") : _T("no", "mobile"); ?></td></tr>
            <tr><td><?php echo _T("Permission to overlay on top of other windows", "mobile"); ?></td><td><?php echo $device_info['overlapPermission'] ? _T("yes", "mobile") : _T("no", "mobile"); ?></td></tr>
            <tr><td><?php echo _T("Permission to access the use of history", "mobile"); ?></td><td><?php echo $device_info['historyPermission'] ? _T("yes", "mobile") : _T("no", "mobile"); ?></td></tr>
            <tr><td><?php echo _T("Permission to access the accessibility services", "mobile"); ?></td><td><?php echo $device_info['accessibilityPermission'] ? _T("yes", "mobile") : _T("no", "mobile"); ?></td></tr>
            <tr><td><?php echo _T("Model", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['model'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("OS version", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['osVersion'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Battery charge", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['battery'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("MDM mode", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['mdmMode'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Kiosk mode", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['kioskMode'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Launcher variant", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['launcherVariant'] ?? ''); ?></td></tr>
            <tr><td><?php echo _T("Default launcher", "mobile"); ?></td><td><?php echo htmlspecialchars($device_info['defaultLauncher'] ?? ''); ?></td></tr>
            <tr><td colspan="2" style="background-color: #dadadaff; text-align: center; font-weight:bold;"><?php echo _T("Installation status", "mobile"); ?></td></tr>
        </table>
        <table cellpadding="6" cellspacing="0" style="border: 1px solid; border-collapse: collapse; width: 100%;">
            <tr>
                <th style="text-align:start;"><?php echo _T("Title", "mobile"); ?></th>
                <th style="text-align:start;"><?php echo _T("Package ID", "mobile"); ?></th>
                <th style="text-align:start;"><?php echo _T("Installed version", "mobile"); ?></th>
                <th style="text-align:start;"><?php echo _T("Required version", "mobile"); ?></th>
            </tr>
            <?php foreach ($device_info['applications'] as $app): ?>
            <tr>
                <td><?php echo htmlspecialchars($app['applicationName']); ?></td>
                <td><?php echo htmlspecialchars($app['applicationPkg']); ?></td>
                <td><?php echo htmlspecialchars($app['versionInstalled']); ?></td>
                <td><?php echo htmlspecialchars($app['versionRequired']); ?></td>
            </tr>
            <?php endforeach; ?>
        </table>
    </div>
<?php elseif (isset($_POST['search'])): ?>
    <div class="info-box" style="margin-top: 20px;">
        <?php echo _T("No information found for this device", "mobile"); ?>
    </div>
<?php endif; ?>

<script type="text/javascript">
// autocomplete logic
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
            .then(response => response.json())
            .then(data => {
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
                        
                        li.onmouseover = function() {
                            li.style.backgroundColor = '#f0f0f0';
                        };
                        li.onmouseout = function() {
                            li.style.backgroundColor = 'white';
                        };
                        
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
            .catch(error => {
                console.error('Error:', error);
                suggestionsList.style.display = 'none';
            });
    }, 300);
});

// Hide autocomplete
document.addEventListener('click', function(e) {
    if (e.target.id !== 'device') {
        document.getElementById('device-suggestions').style.display = 'none';
    }
});

function pushSearch() {
    document.querySelector('form[name="searchform"]').submit();
}
</script>

<?php

