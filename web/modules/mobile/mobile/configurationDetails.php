<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");
require_once("modules/imaging/includes/class_form.php");

$configId = isset($_GET['id']) ? $_GET['id'] : '';
if ($configId === '') {
    new NotifyWidgetFailure(_T("Configuration ID is missing", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/configurationsList"));
    exit;
}

$config = xmlrpc_get_hmdm_configuration_by_id($configId);
$configName = isset($config['name']) ? $config['name'] : _T("Configuration details", "mobile");

$notifyMessage = null;
$notifyError = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['bcancel'])) {
        header("Location: " . urlStrRedirect("mobile/mobile/configurationsList"));
        exit;
    }
    if (isset($_POST['bsave']) || isset($_POST['bsaveexit'])) {
        $payload = array(
            'id' => intval($configId)
        );
        
        if (isset($_POST['config_name'])) {
            $payload['name'] = $_POST['config_name'];
        }
        if (isset($_POST['config_description'])) {
            $payload['description'] = $_POST['config_description'];
        }
        if (isset($_POST['config_password'])) {
            $payload['password'] = $_POST['config_password'];
        }
        
        if (isset($_POST['config_location_tracking'])) {
            $payload['requestUpdates'] = $_POST['config_location_tracking'];
        }
        if (isset($_POST['config_app_permissions'])) {
            $payload['appPermissions'] = $_POST['config_app_permissions'];
        }
        
        if (isset($_POST['config_push_options'])) {
            $payload['pushOptions'] = $_POST['config_push_options'];
        }
        if (isset($_POST['config_keepalive_time'])) {
            $payload['keepaliveTime'] = intval($_POST['config_keepalive_time']);
        }
        
        $radioFields = array(
            'config_gps' => 'gps',
            'config_bluetooth' => 'bluetooth',
            'config_wifi' => 'wifi',
            'config_mobile_data' => 'mobileData'
        );
        foreach ($radioFields as $formField => $apiField) {
            if (isset($_POST[$formField])) {
                $val = $_POST[$formField];
                if ($val === '') {
                    $payload[$apiField] = null;
                } else {
                    $payload[$apiField] = ($val === '1');
                }
            }
        }
        
        $checkboxFields = array(
            'config_usb_storage' => 'usbStorage',
            'config_manage_timeout' => 'manageTimeout',
            'config_lock_volume' => 'lockVolume',
            'config_manage_volume' => 'manageVolume',
            'config_schedule_app_update' => 'scheduleAppUpdate',
            'config_show_wifi' => 'showWifi',
            'config_run_default_launcher' => 'runDefaultLauncher',
            'config_disable_screenshots' => 'disableScreenshots',
            'config_autostart_foreground' => 'autostartForeground'
        );
        foreach ($checkboxFields as $formField => $apiField) {
            $payload[$apiField] = isset($_POST[$formField]);
        }
        
        if (isset($_POST['config_brightness'])) {
            $val = $_POST['config_brightness'];
            if ($val === '') {
                $payload['autoBrightness'] = null;
            } elseif ($val === '0') {
                $payload['autoBrightness'] = false;
                if (isset($_POST['config_brightness_value'])) {
                    $payload['brightness'] = intval($_POST['config_brightness_value']);
                }
            } else {
                $payload['autoBrightness'] = true;
            }
        }
        
        if (isset($_POST['config_timeout']) && $_POST['config_timeout'] !== '') {
            $payload['timeout'] = intval($_POST['config_timeout']);
        }
        
        if (isset($_POST['config_volume']) && $_POST['config_volume'] !== '') {
            $payload['volume'] = intval($_POST['config_volume']);
        }
        
        if (isset($_POST['config_timezone_mode'])) {
            $tzMode = $_POST['config_timezone_mode'];
            if ($tzMode === 'manual' && isset($_POST['config_time_zone'])) {
                $payload['timeZone'] = $_POST['config_time_zone'];
            } elseif ($tzMode === 'auto') {
                $payload['timeZone'] = 'auto';
            } else {
                $payload['timeZone'] = '';
            }
        }
        
        if (isset($_POST['config_system_update'])) {
            $payload['systemUpdateType'] = intval($_POST['config_system_update']);
        }
        if (isset($_POST['config_system_update_from'])) {
            $payload['systemUpdateFrom'] = $_POST['config_system_update_from'];
        }
        if (isset($_POST['config_system_update_to'])) {
            $payload['systemUpdateTo'] = $_POST['config_system_update_to'];
        }
        
        if (isset($_POST['config_app_update_from'])) {
            $payload['appUpdateFrom'] = $_POST['config_app_update_from'];
        }
        if (isset($_POST['config_app_update_to'])) {
            $payload['appUpdateTo'] = $_POST['config_app_update_to'];
        }
        
        if (isset($_POST['config_download_updates'])) {
            $payload['downloadUpdates'] = $_POST['config_download_updates'];
        }
        if (isset($_POST['config_password_mode'])) {
            $payload['passwordMode'] = $_POST['config_password_mode'];
        }
        
        $result = xmlrpc_update_hmdm_configuration($payload);
        
        if ($result !== null && $result !== false) {
            $notifyMessage = _T("Configuration saved successfully", "mobile");
            $config = xmlrpc_get_hmdm_configuration_by_id($configId);
            if (isset($_POST['bsaveexit'])) {
                header("Location: " . urlStrRedirect("mobile/mobile/configurationsList"));
                exit;
            }
        } else {
            $notifyError = _T("Failed to save configuration", "mobile");
        }
    }
}

$p = new PageGenerator(sprintf(_T("Configuration: %s", "mobile"), htmlspecialchars($configName)));
$p->setSideMenu($sidemenu);
$p->display();

?>

<?php if (!empty($notifyMessage)) { new NotifyWidgetSuccess($notifyMessage); } ?>
<?php if (!empty($notifyError)) { new NotifyWidgetFailure($notifyError); } ?>

<style>
.config-tabs {
    border-bottom: 2px solid #ddd;
    margin-bottom: 20px;
}
.config-tabs ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
}
.config-tabs li {
    margin-right: 5px;
}
.config-tabs a {
    display: block;
    padding: 10px 20px;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-bottom: none;
    text-decoration: none;
    color: #333;
    border-radius: 4px 4px 0 0;
}
.config-tabs a.active {
    background: #fff;
    font-weight: bold;
    border-bottom: 2px solid #fff;
    margin-bottom: -2px;
}
.config-tabs a:hover {
    background: #e9e9e9;
}
.config-tabs a.active:hover {
    background: #fff;
}
.tab-content {
    display: none;
    padding: 20px 0;
}
.tab-content.active {
    display: block;
}
</style>

<div class="config-tabs">
    <ul>
        <li><a href="#" class="tab-link active" data-tab="common"><?php echo _T("Common settings", "mobile"); ?></a></li>
        <li><a href="#" class="tab-link" data-tab="design"><?php echo _T("Design settings", "mobile"); ?></a></li>
        <li><a href="#" class="tab-link" data-tab="apps"><?php echo _T("Applications", "mobile"); ?></a></li>
        <li><a href="#" class="tab-link" data-tab="mdm"><?php echo _T("MDM Settings", "mobile"); ?></a></li>
        <li><a href="#" class="tab-link" data-tab="appsettings"><?php echo _T("Application settings", "mobile"); ?></a></li>
        <li><a href="#" class="tab-link" data-tab="files"><?php echo _T("Files", "mobile"); ?></a></li>
    </ul>
</div>

<?php
$form = new Form();
$form->push(new Table());

echo '<div id="tab-common" class="tab-content active">';

$form->add(new TrFormElement(
    _T("Name", "mobile"),
    new InputTpl("config_name", '/^.{1,255}$/', isset($config['name']) ? $config['name'] : '')
), array("value" => isset($config['name']) ? $config['name'] : ''));

$descTpl = new TextareaTpl("config_description");
$descTpl->setRows(4);
$form->add(new TrFormElement(
    _T("Description", "mobile"),
    $descTpl
), array("value" => isset($config['description']) ? $config['description'] : ''));

$passwordTpl = new InputTpl("config_password", '/^.+$/', isset($config['password']) ? $config['password'] : '');
$passwordTpl->fieldType = "password";
$form->add(new TrFormElement(
    _T("Unlock password", "mobile"),
    $passwordTpl
), array("value" => isset($config['password']) ? $config['password'] : ''));

$locationTpl = new SelectItem("config_location_tracking");
$locationTpl->setElements(array(
    _T("No active tracking (use third-party app location data)", "mobile"),
    _T("Track location by GPS", "mobile"),
    _T("Track location by Wi-Fi (Google services must be enabled)", "mobile")
));
$locationTpl->setElementsVal(array("DONOTTRACK", "GPS", "WIFI"));
$locationTpl->setSelected(isset($config['requestUpdates']) ? $config['requestUpdates'] : 'DONOTTRACK');
$form->add(new TrFormElement(
    _T("Location Tracking", "mobile"),
    $locationTpl
));

$permissionsTpl = new SelectItem("config_app_permissions");
$permissionsTpl->setElements(array(
    _T("Auto-grant all permissions", "mobile"),
    _T("Auto-grant all, ask user for the location permission", "mobile"),
    _T("Auto-grant all, do not grant the location permission", "mobile"),
    _T("Ask user for all permissions", "mobile")
));
$permissionsTpl->setElementsVal(array("GRANTALL", "ASKLOCATION", "DENYLOCATION", "ASKALL"));
$permissionsTpl->setSelected(isset($config['appPermissions']) ? $config['appPermissions'] : 'GRANTALL');
$form->add(new TrFormElement(
    _T("Permissions for other apps", "mobile"),
    $permissionsTpl
));

$pushTpl = new SelectItem("config_push_options");
$pushTpl->setElements(array(
    _T("MQTT protocol", "mobile"),
    _T("HTTP polling", "mobile")
));
$pushTpl->setElementsVal(array("mqttAlarm", "polling"));
$pushTpl->setSelected(isset($config['pushOptions']) ? $config['pushOptions'] : 'mqttAlarm');
$form->add(new TrFormElement(
    _T("Push notifications", "mobile"),
    $pushTpl
));

$keepaliveTpl = new SelectItem("config_keepalive_time");
$keepaliveTpl->setElements(array(
    _T("1 minute", "mobile"),
    _T("2 minutes", "mobile"),
    _T("3 minutes", "mobile"),
    _T("5 minutes", "mobile"),
    _T("10 minutes", "mobile"),
    _T("15 minutes", "mobile")
));
$keepaliveTpl->setElementsVal(array("60", "120", "180", "300", "600", "900"));
$keepaliveTpl->setSelected(isset($config['keepaliveTime']) ? $config['keepaliveTime'] : '60');
$form->add(new TrFormElement(
    _T("Keep-Alive time", "mobile"),
    $keepaliveTpl,
    array(
        "class" => "keepalive-row",
        "style" => "display:none;"
    )
));

$gpsTpl = new RadioTpl("config_gps");
$gpsTpl->setChoices(array(_T("Any", "mobile"), _T("Disabled", "mobile"), _T("Enabled", "mobile")));
$gpsTpl->setValues(array("", "0", "1"));
$gpsVal = array_key_exists('gps', $config) ? $config['gps'] : null;
$gpsTpl->setSelected(($gpsVal === null || $gpsVal === '') ? '' : ($gpsVal ? '1' : '0'));
$form->add(new TrFormElement(
    _T("GPS", "mobile"),
    $gpsTpl
));

$bluetoothTpl = new RadioTpl("config_bluetooth");
$bluetoothTpl->setChoices(array(_T("Any", "mobile"), _T("Disabled", "mobile"), _T("Enabled", "mobile")));
$bluetoothTpl->setValues(array("", "0", "1"));
$btVal = array_key_exists('bluetooth', $config) ? $config['bluetooth'] : null;
$bluetoothTpl->setSelected(($btVal === null || $btVal === '') ? '' : ($btVal ? '1' : '0'));
$form->add(new TrFormElement(
    _T("Bluetooth", "mobile"),
    $bluetoothTpl
));

$wifiTpl = new RadioTpl("config_wifi");
$wifiTpl->setChoices(array(_T("Any", "mobile"), _T("Disabled", "mobile"), _T("Enabled", "mobile")));
$wifiTpl->setValues(array("", "0", "1"));
$wifiVal = array_key_exists('wifi', $config) ? $config['wifi'] : null;
$wifiTpl->setSelected(($wifiVal === null || $wifiVal === '') ? '' : ($wifiVal ? '1' : '0'));
$form->add(new TrFormElement(
    _T("Wi-Fi", "mobile"),
    $wifiTpl
));

$mobiledataTpl = new RadioTpl("config_mobile_data");
$mobiledataTpl->setChoices(array(_T("Any", "mobile"), _T("Disabled", "mobile"), _T("Enabled", "mobile")));
$mobiledataTpl->setValues(array("", "0", "1"));
$mdVal = array_key_exists('mobileData', $config) ? $config['mobileData'] : null;
$mobiledataTpl->setSelected(($mdVal === null || $mdVal === '') ? '' : ($mdVal ? '1' : '0'));
$form->add(new TrFormElement(
    _T("Mobile data", "mobile"),
    $mobiledataTpl
));

$form->add(new TrFormElement(
    _T("Block USB storage", "mobile"),
    new CheckboxTpl("config_usb_storage")
), array("value" => isset($config['usbStorage']) && $config['usbStorage'] ? 'checked' : ''));

$brightnessTpl = new RadioTpl("config_brightness");
$brightnessTpl->setChoices(array(_T("None", "mobile"), _T("Value", "mobile"), _T("Auto", "mobile")));
$brightnessTpl->setValues(array("", "0", "1"));
$brightnessMode = '';
if (array_key_exists('autoBrightness', $config)) {
    $autoBrightness = $config['autoBrightness'];
    if ($autoBrightness === null || $autoBrightness === '' || $autoBrightness === 'null') {
        $brightnessMode = '';
    } elseif ($autoBrightness) {
        $brightnessMode = '1';
    } else {
        $brightnessMode = '0';
    }
}
$brightnessTpl->setSelected($brightnessMode);
$brightnessValue = isset($config['brightness']) ? (string)$config['brightness'] : '128';
$brightnessSliderTpl = new InputTpl("config_brightness_value", '/^\\d+$/', $brightnessValue);
$brightnessSliderTpl->fieldType = "range";
$brightnessSliderTpl->setAttributCustom(' min="0" max="255" step="1" oninput="document.getElementById(\'brightness_value_display\').textContent=this.value"');
$brightnessField = new multifieldTpl(array(
    $brightnessTpl,
    $brightnessSliderTpl,
    new TextTpl('<span id="brightness_value_display">' . $brightnessValue . '</span>')
));
$form->add(new TrFormElement(
    _T("Manage brightness", "mobile"),
    $brightnessField,
    array("separator" => ' &nbsp; ')
));

$form->add(new TrFormElement(
    _T("Manage screen timeout", "mobile"),
    new CheckboxTpl("config_manage_timeout")
), array("value" => isset($config['manageTimeout']) && $config['manageTimeout'] ? 'checked' : ''));
$timeoutDefault = isset($config['timeout']) ? (string)$config['timeout'] : '';
$timeoutTpl = new IntegerTpl("config_timeout", '/^\\d+$/');
$timeoutTpl->defaultValue = $timeoutDefault;
$timeoutTpl->setAttributCustom(' data-default-timeout="' . $timeoutDefault . '"');
$form->add(new TrFormElement(
    _T("Screen timeout (s)", "mobile"),
    $timeoutTpl,
    array(
        "value" => isset($config['timeout']) ? (string)$config['timeout'] : '',
        "class" => "timeout-row",
        "style" => "display:none;"
    )
));

$form->add(new TrFormElement(
    _T("Lock volume", "mobile"),
    new CheckboxTpl("config_lock_volume")
), array("value" => isset($config['lockVolume']) && $config['lockVolume'] ? 'checked' : ''));

$form->add(new TrFormElement(
    _T("Manage volume", "mobile"),
    new CheckboxTpl("config_manage_volume")
), array("value" => isset($config['manageVolume']) && $config['manageVolume'] ? 'checked' : ''));
$volumeTpl = new InputTpl("config_volume");
$volumeTpl->fieldType = "range";
$volumeTpl->defaultValue = isset($config['volume']) ? (string)$config['volume'] : '50';
$volumeTpl->setAttributCustom(' min="0" max="100" step="1" oninput="document.getElementById(\'volume_value\').textContent=this.value"');
$volumeDisplay = '<span id="volume_value">' . (isset($config['volume']) ? (string)$config['volume'] : '50') . '</span>';
$form->add(new TrFormElement(
    _T("Volume (0-100)", "mobile"),
    new multifieldTpl(array($volumeTpl, new TextTpl($volumeDisplay))),
    array(
        "value" => array(isset($config['volume']) ? (string)$config['volume'] : '50', ''),
        "separator" => ' &nbsp; ',
        "class" => "volume-row",
        "style" => "display:none;"
    )
));

$timezoneTpl = new SelectItem("config_timezone_mode");
$timezoneTpl->setElements(array(
    _T("Do not manage", "mobile"),
    _T("Auto", "mobile"),
    _T("Manual", "mobile")
));
$timezoneTpl->setElementsVal(array("default", "auto", "manual"));
$form->add(new TrFormElement(
    _T("Manage time zone", "mobile"),
    $timezoneTpl
));
$selectedTimeZoneMode = 'default';
if (isset($config['timeZoneMode']) && $config['timeZoneMode'] !== '') {
    $selectedTimeZoneMode = $config['timeZoneMode'];
} elseif (isset($config['timeZone'])) {
    if ($config['timeZone'] === 'auto') {
        $selectedTimeZoneMode = 'auto';
    } elseif ($config['timeZone'] !== '') {
        $selectedTimeZoneMode = 'manual';
    }
}
$timezoneTpl->setSelected($selectedTimeZoneMode);
$timeZoneValue = (isset($config['timeZone']) && $config['timeZone'] !== 'auto') ? $config['timeZone'] : '';
$form->add(new TrFormElement(
    _T("Time Zone", "mobile"),
    new InputTpl("config_time_zone", '/^.+$/', $timeZoneValue),
    array(
        "value" => $timeZoneValue,
        "class" => "timezone-row",
        "style" => "display:none;"
    )
));

$systemupdateTpl = new RadioTpl("config_system_update");
$systemupdateTpl->setChoices(array(
    _T("Default", "mobile"),
    _T("Immediately", "mobile"),
    _T("Scheduled", "mobile"),
    _T("Postponed", "mobile")
));
$systemupdateTpl->setValues(array("0", "1", "2", "3"));
$systemupdateTpl->setSelected(isset($config['systemUpdateType']) ? (string)$config['systemUpdateType'] : '0');
$form->add(new TrFormElement(
    _T("System Update", "mobile"),
    $systemupdateTpl
));

$sysUpdateFromTpl = new InputTpl("config_system_update_from", '/^.*$/', isset($config['systemUpdateFrom']) ? $config['systemUpdateFrom'] : '');
$sysUpdateFromTpl->fieldType = "time";
$sysUpdateFromTpl->setSize(6);
$sysUpdateToTpl = new InputTpl("config_system_update_to", '/^.*$/', isset($config['systemUpdateTo']) ? $config['systemUpdateTo'] : '');
$sysUpdateToTpl->fieldType = "time";
$sysUpdateToTpl->setSize(6);
$sysUpdateWindowTpl = new multifieldTpl(array($sysUpdateFromTpl, $sysUpdateToTpl));
$form->add(new TrFormElement(
    _T("System update window (From / To)", "mobile"),
    $sysUpdateWindowTpl,
    array(
        "value" => array(
            isset($config['systemUpdateFrom']) ? $config['systemUpdateFrom'] : '',
            isset($config['systemUpdateTo']) ? $config['systemUpdateTo'] : ''
        ),
        "separator" => ' &nbsp;–&nbsp; ',
        "class" => "system-update-row",
        "style" => "display:none;"
    )
));

$form->add(new TrFormElement(
    _T("Schedule app update", "mobile"),
    new CheckboxTpl("config_schedule_app_update")
), array("value" => isset($config['scheduleAppUpdate']) && $config['scheduleAppUpdate'] ? 'checked' : ''));

$appUpdateFromTpl = new InputTpl("config_app_update_from", '/^.*$/', isset($config['appUpdateFrom']) ? $config['appUpdateFrom'] : '');
$appUpdateFromTpl->fieldType = "time";
$appUpdateFromTpl->setSize(6);
$appUpdateToTpl   = new InputTpl("config_app_update_to", '/^.*$/', isset($config['appUpdateTo']) ? $config['appUpdateTo'] : '');
$appUpdateToTpl->fieldType = "time";
$appUpdateToTpl->setSize(6);
$appUpdateWindowTpl = new multifieldTpl(array($appUpdateFromTpl, $appUpdateToTpl));
$form->add(new TrFormElement(
    _T("App update window (From / To)", "mobile"),
    $appUpdateWindowTpl,
    array(
        "value" => array(
            isset($config['appUpdateFrom']) ? $config['appUpdateFrom'] : '',
            isset($config['appUpdateTo']) ? $config['appUpdateTo'] : ''
        ),
        "separator" => ' &nbsp;–&nbsp; ',
        "class" => "app-update-row",
        "style" => "display:none;"
    )
));

$downloadTpl = new SelectItem("config_download_updates");
$downloadTpl->setElements(array(
    _T("Without limits", "mobile"),
    _T("3 attempts in the mobile network", "mobile"),
    _T("By WiFi only", "mobile")
));
$downloadTpl->setElementsVal(array("UNLIMITED", "LIMITED", "WIFI"));
$form->add(new TrFormElement(
    _T("Download content", "mobile"),
    $downloadTpl
));
$downloadTpl->setSelected(isset($config['downloadUpdates']) ? $config['downloadUpdates'] : 'UNLIMITED');

$passwordmodeTpl = new SelectItem("config_password_mode");
$passwordmodeTpl->setElements(array(
    _T("None", "mobile"),
    _T("Password presents", "mobile"),
    _T("Easy (at least 6 symbols)", "mobile"),
    _T("Moderate (8+ symbols, letters and digits)", "mobile"),
    _T("Strong (8+, upper & lowercase, digits, signs)", "mobile")
));
$passwordmodeTpl->setElementsVal(array("any", "present", "easy", "moderate", "strong"));
$form->add(new TrFormElement(
    _T("Password requirements", "mobile"),
    $passwordmodeTpl
));
$passwordmodeTpl->setSelected(isset($config['passwordMode']) ? $config['passwordMode'] : 'any');

$form->add(new TrFormElement(
    _T("WiFi settings on connection error", "mobile"),
    new CheckboxTpl("config_show_wifi")
), array("value" => isset($config['showWifi']) && $config['showWifi'] ? 'checked' : ''));

$form->add(new TrFormElement(
    _T("Background mode", "mobile"),
    new CheckboxTpl("config_run_default_launcher"),
    array("tooltip" => _T("Do not replace a system launcher, only run background MDM services. Not recommended with the kiosk mode.", "mobile"))
), array("value" => isset($config['runDefaultLauncher']) && $config['runDefaultLauncher'] ? 'checked' : ''));

$form->add(new TrFormElement(
    _T("Disable screen capture", "mobile"),
    new CheckboxTpl("config_disable_screenshots")
), array("value" => isset($config['disableScreenshots']) && $config['disableScreenshots'] ? 'checked' : ''));

$form->add(new TrFormElement(
    _T("Autostart apps in foreground", "mobile"),
    new CheckboxTpl("config_autostart_foreground")
), array("value" => isset($config['autostartForeground']) && $config['autostartForeground'] ? 'checked' : ''));

echo '</div>'; // END tab-common

echo '<div id="tab-design" class="tab-content">';
echo '<h3>' . _T("Design Settings", "mobile") . '</h3>';
echo '<p>' . _T("Coming soon...", "mobile") . '</p>';
echo '</div>';

echo '<div id="tab-apps" class="tab-content">';
echo '<h3>' . _T("Applications", "mobile") . '</h3>';
echo '<p>' . _T("Coming soon...", "mobile") . '</p>';
echo '</div>';

echo '<div id="tab-mdm" class="tab-content">';
echo '<h3>' . _T("MDM Settings", "mobile") . '</h3>';
echo '<p>' . _T("Coming soon...", "mobile") . '</p>';
echo '</div>';

echo '<div id="tab-appsettings" class="tab-content">';
echo '<h3>' . _T("Application Settings", "mobile") . '</h3>';
echo '<p>' . _T("Coming soon...", "mobile") . '</p>';
echo '</div>';

echo '<div id="tab-files" class="tab-content">';
echo '<h3>' . _T("Files", "mobile") . '</h3>';
echo '<p>' . _T("Coming soon...", "mobile") . '</p>';
echo '</div>';

$form->addButton('bsave', _T('Save', 'mobile'), 'btnPrimary');
$form->addButton('bsaveexit', _T('Save and exit', 'mobile'), 'btnPrimary');
$form->addButton('bcancel', _T('Cancel', 'mobile'), 'btnSecondary');

$form->display();
?>

<style>
  .pw-wrap { position: relative; display: inline-block; vertical-align: middle; }
  .pw-wrap > .pw-toggle {
    position: absolute; right: 1rem; top: 50%; transform: translateY(-50%);
    border: 0; background: transparent; cursor: pointer; padding: 0;
    width: 1.2rem; height: 1.2rem; line-height: 1; z-index: 2;
  }
  .pw-toggle img { width: 100%; height: 100%; display: block; pointer-events: none; }
</style>

<script type="text/javascript">
jQuery(document).ready(function() {
    function wirePwToggle(id) {
        var $input = jQuery('#' + id);
        if (!$input.length) { return; }

        var $wrap = jQuery('#container_input_' + id);
        if (!$wrap.length) { $wrap = $input.closest('span,div,td'); }
        $wrap.addClass('pw-wrap');

        var $btn = $wrap.find('.pw-toggle[data-for="' + id + '"]');
        if (!$btn.length) {
            $btn = jQuery('<button type="button" class="pw-toggle" data-for="' + id + '" aria-label="Show password" aria-controls="' + id + '" aria-pressed="false" data-open="img/login/open.svg" data-close="img/login/close.svg"><img class="pw-icon" alt=""></button>');
            $wrap.append($btn);
        } else if (!$btn.find('img.pw-icon').length) {
            $btn.append('<img class="pw-icon" alt="">');
        }

        function syncBtn(isHidden) {
            var $icon = $btn.find('img.pw-icon');
            var open = $btn.data('open') || '';
            var close = $btn.data('close') || '';
            $icon.attr('src', isHidden ? close : open);
            $btn.attr('aria-label', isHidden ? 'Show password' : 'Hide password')
                .attr('aria-pressed', !isHidden);
        }
        syncBtn(($input.attr('type') === 'password'));

        $btn.off('click').on('click', function() {
            var wasHidden = ($input.attr('type') === 'password');
            var newType = wasHidden ? 'text' : 'password';
            var start = $input[0] && $input[0].selectionStart;
            var end = $input[0] && $input[0].selectionEnd;
            $input.attr('type', newType);
            try { if (start != null && end != null) { $input[0].setSelectionRange(start, end); } } catch (e) {}
            syncBtn(newType === 'password');
            $input.trigger('focus');
        });
    }

    wirePwToggle('config_password');

    function toggleTimeoutRow() {
        var checked = jQuery('input[name="config_manage_timeout"]').is(':checked');
        if (checked) {
            jQuery('.timeout-row').show();
            var $t = jQuery('#config_timeout');
            var def = $t.data('default-timeout');
            if ($t.val() === '' && typeof def !== 'undefined') { $t.val(def); }
        } else {
            jQuery('.timeout-row').hide();
        }
    }
    jQuery('input[name="config_manage_timeout"]').on('change', toggleTimeoutRow);

    function toggleTimeZoneRow() {
        var val = jQuery('select[name="config_timezone_mode"]').val();
        if (val === 'manual') {
            jQuery('.timezone-row').show();
        } else {
            jQuery('.timezone-row').hide();
        }
    }
    jQuery('select[name="config_timezone_mode"]').on('change', toggleTimeZoneRow);

    function toggleAppUpdateWindow() {
        var on = jQuery('input[name="config_schedule_app_update"]').is(':checked');
        if (on) {
            jQuery('.app-update-row').show();
        } else {
            jQuery('.app-update-row').hide();
        }
    }
    jQuery('input[name="config_schedule_app_update"]').on('change', toggleAppUpdateWindow);

    function toggleSystemUpdateWindow() {
        var val = jQuery('input[name="config_system_update"]:checked').val();
        if (val === '2') {
            jQuery('.system-update-row').show();
        } else {
            jQuery('.system-update-row').hide();
        }
    }
    jQuery('input[name="config_system_update"]').on('change', toggleSystemUpdateWindow);

    function toggleVolumeSlider() {
        var on = jQuery('input[name="config_manage_volume"]').is(':checked');
        if (on) {
            jQuery('.volume-row').show();
        } else {
            jQuery('.volume-row').hide();
        }
    }
    jQuery('input[name="config_manage_volume"]').on('change', toggleVolumeSlider);

    function toggleKeepAliveTime() {
        var pushOption = jQuery('select[name="config_push_options"]').val();
        if (pushOption === 'mqttAlarm') {
            jQuery('.keepalive-row').show();
        } else {
            jQuery('.keepalive-row').hide();
        }
    }
    jQuery('select[name="config_push_options"]').on('change', toggleKeepAliveTime);

    function toggleBrightnessSlider() {
        var val = jQuery('input[name="config_brightness"]:checked').val();
        var show = (val === '0');
        if (show) {
            jQuery('#config_brightness_value').show();
            jQuery('#brightness_value_display').show();
        } else {
            jQuery('#config_brightness_value').hide();
            jQuery('#brightness_value_display').hide();
        }
    }
    jQuery('input[name="config_brightness"]').on('change', toggleBrightnessSlider);

    jQuery('.tab-link').click(function(e) {
        e.preventDefault();
        var targetTab = jQuery(this).data('tab');
        jQuery('.tab-link').removeClass('active');
        jQuery(this).addClass('active');
        jQuery('.tab-content').removeClass('active');
        jQuery('#tab-' + targetTab).addClass('active');
    });

    setTimeout(function() {
        toggleTimeoutRow();
        toggleTimeZoneRow();
        toggleAppUpdateWindow();
        toggleSystemUpdateWindow();
        toggleVolumeSlider();
        toggleKeepAliveTime();
        toggleBrightnessSlider();
    }, 100);
});
</script>
