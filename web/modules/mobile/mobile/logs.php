<?php
require_once("modules/mobile/includes/xmlrpc.php");

$field_device = isset($_POST['device']) ? $_POST['device'] : (isset($_GET['device']) ? $_GET['device'] : "");
$field_app_id = isset($_POST['app_id']) ? $_POST['app_id'] : (isset($_GET['app_id']) ? $_GET['app_id'] : "");
$field_severity = isset($_POST['severity']) ? $_POST['severity'] : (isset($_GET['severity']) ? $_GET['severity'] : "-1");
$page_num = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$page_size = 50;

$logs = array();
$show_results = true;

if ($show_results) {
    $logs = xmlrpc_get_hmdm_device_logs($field_device, $field_app_id, $field_severity, $page_size, $page_num);
}
?>

<h3><?php echo _T("Device Logs", "mobile"); ?></h3>
<p><?php echo _T("Search device logs with filters and export", "mobile"); ?></p>

<hr/>

<div style="display:flex; justify-content:space-between; width:100%;">
    <form method="post" name="searchform" id="searchform" onsubmit="return false;">
        <div id="searchBest" style="width: 800px; display:flex; gap:12px; align-items:center;">
            <span class="searchfield" style="width: 300px; position: relative;">
                <input type="text" class="searchfieldreal" name="device" id="device" placeholder="<?php echo _T("Device's name", "mobile"); ?>" value="<?php echo htmlspecialchars($field_device); ?>" autocomplete="off">
                <button type="button" class="search-clear" aria-label="<?php echo _T('Clear device', 'mobile'); ?>" onclick="document.getElementById('device').value=''; document.getElementById('device-suggestions').innerHTML=''; document.getElementById('device-suggestions').style.display='none';"></button>
                <ul id="device-suggestions" style="position: absolute; top: 100%; left: 0; width: 100%; max-height: 200px; overflow-y: auto; background: white; border: 1px solid #ccc; list-style: none; padding: 0; margin: 5px 0 0 0; display: none; z-index: 1000;"></ul>
            </span>

            <span class="searchfield" style="width: 300px; position: relative;">
                <input type="text" class="searchfieldreal" name="app" id="app" placeholder="<?php echo _T("Package name", "mobile"); ?>" value="" autocomplete="off">
                <input type="hidden" id="app_id" name="app_id" value="<?php echo htmlspecialchars($field_app_id); ?>">
                <button type="button" class="search-clear" aria-label="<?php echo _T('Clear app', 'mobile'); ?>" onclick="document.getElementById('app').value=''; document.getElementById('app_id').value=''; document.getElementById('app-suggestions').innerHTML=''; document.getElementById('app-suggestions').style.display='none';"></button>
                <ul id="app-suggestions" style="position: absolute; top: 100%; left: 0; width: 100%; max-height: 200px; overflow-y: auto; background: white; border: 1px solid #ccc; list-style: none; padding: 0; margin: 5px 0 0 0; display: none; z-index: 1000;"></ul>
            </span>

            <span class="searchfield">
                <select class="searchfieldreal noborder" name="severity" id="severity" onchange="document.getElementById('searchform').submit();">
                    <option value="-1" <?php echo $field_severity === "-1" ? "selected" : ""; ?>><?php echo _T("Severity search...", "mobile"); ?></option>
                    <option value="0" <?php echo $field_severity === "0" ? "selected" : ""; ?>><?php echo _T("None", "mobile"); ?></option>
                    <option value="1" <?php echo $field_severity === "1" ? "selected" : ""; ?>><?php echo _T("Error", "mobile"); ?></option>
                    <option value="2" <?php echo $field_severity === "2" ? "selected" : ""; ?>><?php echo _T("Warning", "mobile"); ?></option>
                    <option value="3" <?php echo $field_severity === "3" ? "selected" : ""; ?>><?php echo _T("Info", "mobile"); ?></option>
                    <option value="4" <?php echo $field_severity === "4" ? "selected" : ""; ?>><?php echo _T("Debug", "mobile"); ?></option>
                    <option value="5" <?php echo $field_severity === "5" ? "selected" : ""; ?>><?php echo _T("Verbose", "mobile"); ?></option>
                </select>
            </span>

            <button type="submit" name="search" value="1" class="btnPrimary" onclick="document.getElementById('searchform').submit(); return false;"><?php echo _T("Search", "mobile"); ?></button>
            <span class="loader" aria-hidden="true"></span>
            <input type="hidden" name="app_id" id="search_app_id" value="">
        </div>
    </form>
    <div>
        <button type="button" name="export" class="btnPrimary" onclick="exportLogs(); return false;"><?php echo _T("Export", "mobile"); ?></button>
    </div>
</div>

<?php if ($show_results): ?>
    <?php if (is_array($logs) && count($logs) > 0): ?>
        <div id='logs-container' style="margin-top: 20px;">
            <table cellpadding="6" cellspacing="0" style="border: 1px solid; border-collapse: collapse; width: 100%;">
                <tr style="background-color: #dadadaff; ">
                    <th style="text-align:start;"><?php echo _T("Time", "mobile"); ?></th>
                    <th style="text-align:start;"><?php echo _T("Device", "mobile"); ?></th>
                    <th style="text-align:start;"><?php echo _T("Package", "mobile"); ?></th>
                    <th style="text-align:start;"><?php echo _T("Severity", "mobile"); ?></th>
                    <th style="text-align:start;"><?php echo _T("Message", "mobile"); ?></th>
                </tr>
                <?php foreach ($logs as $row): ?>
                <tr>
                    <td><?php echo isset($row['time']) ? date("Y-m-d H:i:s", $row['time']) : ""; ?></td>
                    <td><?php echo htmlspecialchars(isset($row['device']) ? $row['device'] : ""); ?></td>
                    <td><?php echo htmlspecialchars(isset($row['package']) ? $row['package'] : ""); ?></td>
                    <td><?php echo htmlspecialchars(isset($row['severity']) ? $row['severity'] : ""); ?></td>
                    <td><?php echo htmlspecialchars(isset($row['message']) ? $row['message'] : ""); ?></td>
                </tr>
                <?php endforeach; ?>
            </table>
        </div>
    <?php else: ?>
        <div class="info-box" style="margin-top: 20px;">
            <?php echo _T("No logs found matching the criteria", "mobile"); ?>
        </div>
    <?php endif; ?>
<?php endif; ?>

<script type="text/javascript">
// Device autocomplete using existing backend search
const deviceInput = document.getElementById('device');
const deviceSuggestions = document.getElementById('device-suggestions');
let deviceTimeout;

deviceInput.addEventListener('input', function() {
    clearTimeout(deviceTimeout);
    const query = this.value.trim();
    if (!query) { deviceSuggestions.style.display = 'none'; deviceSuggestions.innerHTML = ''; return; }
    deviceTimeout = setTimeout(() => {
        fetch('<?php echo urlStrRedirect("mobile/mobile/ajaxDeviceSearch"); ?>&filter=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(list => {
                deviceSuggestions.innerHTML = '';
                if (!list || list.length === 0) { deviceSuggestions.style.display = 'none'; return; }
                list.forEach(item => {
                    const name = item.name || '';
                    const li = document.createElement('li');
                    li.textContent = name;
                    li.style.padding = '6px 8px';
                    li.style.cursor = 'pointer';
                    li.addEventListener('click', () => {
                        deviceInput.value = name;
                        deviceSuggestions.style.display = 'none';
                        deviceSuggestions.innerHTML = '';
                    });
                    deviceSuggestions.appendChild(li);
                });
                deviceSuggestions.style.display = 'block';
            })
            .catch(() => { deviceSuggestions.style.display = 'none'; deviceSuggestions.innerHTML = ''; });
    }, 300);
});

deviceInput.addEventListener('blur', function() { setTimeout(() => { deviceSuggestions.style.display = 'none'; }, 200); });

deviceInput.addEventListener('focus', function() { if (deviceSuggestions.innerHTML.trim()) deviceSuggestions.style.display = 'block'; });

// App package autocomplete (new backend function)
const appInput = document.getElementById('app');
const appIdInput = document.getElementById('app_id');
const appSuggestions = document.getElementById('app-suggestions');
let appTimeout;

appInput.addEventListener('input', function() {
    clearTimeout(appTimeout);
    const query = this.value.trim();
    if (!query) { appSuggestions.style.display = 'none'; appSuggestions.innerHTML = ''; return; }
    appTimeout = setTimeout(() => {
        fetch('<?php echo urlStrRedirect("mobile/mobile/ajaxAppSearch"); ?>&q=' + encodeURIComponent(query))
            .then(resp => resp.json())
            .then(list => {
                appSuggestions.innerHTML = '';
                if (!list || list.length === 0) { appSuggestions.style.display = 'none'; return; }
                list.forEach(item => {
                    const pkgName = item.name || '';
                    const pkgId = item.id || '';
                    const li = document.createElement('li');
                    li.textContent = pkgName;
                    li.style.padding = '6px 8px';
                    li.style.cursor = 'pointer';
                    li.addEventListener('click', () => {
                        appInput.value = pkgName;
                        appIdInput.value = pkgId;
                        document.getElementById('search_app_id').value = pkgId;
                        document.getElementById('export_app_id').value = pkgId;
                        appSuggestions.style.display = 'none';
                        appSuggestions.innerHTML = '';
                    });
                    appSuggestions.appendChild(li);
                });
                appSuggestions.style.display = 'block';
            })
            .catch(() => { appSuggestions.style.display = 'none'; appSuggestions.innerHTML = ''; });
    }, 300);
});

appInput.addEventListener('blur', function() { setTimeout(() => { appSuggestions.style.display = 'none'; }, 200); });

appInput.addEventListener('focus', function() { if (appSuggestions.innerHTML.trim()) appSuggestions.style.display = 'block'; });

function exportLogs() {
    const device = document.getElementById('device').value;
    const app = document.getElementById('app').value;
    const severity = document.getElementById('severity').value;
    
    let url = '<?php echo urlStrRedirect("mobile/mobile/exportLogs"); ?>' + '&device=' + encodeURIComponent(device) + '&app=' + encodeURIComponent(app) + '&severity=' + encodeURIComponent(severity);
    
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Export failed');
            return response.blob();
        })
        .then(blob => {
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = 'logs_export.txt';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Export error:', error);
            alert('<?php echo _T("Failed to export logs", "mobile"); ?>');
        });
}
</script>