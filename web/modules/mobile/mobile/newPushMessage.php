<?php

/**
 * Mobile Module - Send New Push Message
 * Medulla Management Console (MMC)
 * 
 * Allows users to send push messages to devices, groups, configurations, or all devices
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Send New Push Message", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$send_to_type = isset($_POST['send_to']) ? $_POST['send_to'] : "device";
$message_type = isset($_POST['message_type']) ? $_POST['message_type'] : "configUpdated";
$payload_text = isset($_POST['payload']) ? $_POST['payload'] : "";
$device_number = isset($_POST['device_input']) ? $_POST['device_input'] : "";
$group_id = isset($_POST['group_input']) ? $_POST['group_input'] : "";
$configuration_id = isset($_POST['configuration_input']) ? $_POST['configuration_input'] : "";

$groups = array();
$configurations = array();
$error = "";
$success = "";

// Fetch groups and configurations for selects
$groups = xmlrpc_get_hmdm_groups();
$configurations = xmlrpc_get_hmdm_configurations();

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['send_message'])) {
    // Validate required fields
    if ($send_to_type !== "all_devices") {
        if ($send_to_type === "device" && empty($device_number)) {
            $error = _T("Device is required", "mobile");
        } elseif ($send_to_type === "group" && empty($group_id)) {
            $error = _T("Group is required", "mobile");
        } elseif ($send_to_type === "configuration" && empty($configuration_id)) {
            $error = _T("Configuration is required", "mobile");
        }
    }

    if (empty($error)) {
        // Call the send push message function
        $result = xmlrpc_send_hmdm_push_message(
            $send_to_type,
            $message_type,
            $payload_text,
            $device_number,
            $group_id,
            $configuration_id
        );

        if ($result && (isset($result['status']) && $result['status'] === 'OK') || isset($result['success'])) {
            $success = _T("Push message sent successfully", "mobile");
            // Clear the form
            $send_to_type = "device";
            $message_type = "configUpdated";
            $payload_text = "";
            $device_number = "";
            $group_id = "";
            $configuration_id = "";
        } else {
            $error = _T("Failed to send push message. Please try again.", "mobile");
            if (isset($result['message'])) {
                $error .= ": " . htmlspecialchars($result['message']);
            }
        }
    }
}

?>

<p><?php echo _T("Send a push message to devices, groups, configurations, or all devices", "mobile"); ?></p>

<?php if (!empty($error)): ?>
    <div class="alert alert-error" style="padding: 10px; margin-bottom: 15px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 4px;">
        <?php echo htmlspecialchars($error); ?>
    </div>
<?php endif; ?>

<?php if (!empty($success)): ?>
    <div class="alert alert-success" style="padding: 10px; margin-bottom: 15px; background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; border-radius: 4px;">
        <?php echo htmlspecialchars($success); ?>
    </div>
<?php endif; ?>

<form method="post" name="newpushmessageform">
    <table cellpadding="6" cellspacing="0" border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <td style="width: 200px; font-weight: bold;"><?php echo _T("Send to", "mobile"); ?></td>
            <td>
                <select name="send_to" id="send_to" onchange="updateSecondInput()">
                    <option value="device"><?php echo _T("Device", "mobile"); ?></option>
                    <option value="group"><?php echo _T("Group", "mobile"); ?></option>
                    <option value="configuration"><?php echo _T("Configuration", "mobile"); ?></option>
                    <option value="all_devices"><?php echo _T("All devices", "mobile"); ?></option>
                </select>
            </td>
        </tr>

        <!-- Device Input -->
        <tr id="device_row" style="display: table-row;">
            <td style="font-weight: bold;"><?php echo _T("Device", "mobile"); ?></td>
            <td>
                <div id="deviceSearchContainer" style="width: 370px; position: relative;">
                    <input type="text" class="searchfieldreal" name="device_input" id="device_input" placeholder="<?php echo _T("Device's name", "mobile"); ?>" value="<?php echo htmlspecialchars($device_number); ?>" autocomplete="off">

                    <button type="button" class="search-clear" aria-label="<?php echo _T('Clear device', 'mobile'); ?>" onclick="document.getElementById('device_input').value=''; document.getElementById('device-suggestions').innerHTML = ''; document.getElementById('device-suggestions').style.display = 'none';" style="margin-left: 5px;"></button>

                    <ul id="device-suggestions" style="position: absolute; top: 100%; left: 0; width: 100%; max-height: 200px; overflow-y: auto; background: white; border: 1px solid #ccc; list-style: none; padding: 0; margin: 5px 0 0 0; display: none; z-index: 1000;"></ul>
                </div>
            </td>
        </tr>

        <!-- Group Input -->
        <tr id="group_row" style="display: none;">
            <td style="font-weight: bold;"><?php echo _T("Group", "mobile"); ?></td>
            <td>
                <select name="group_input" id="group_input">
                    <option value=""><?php echo _T("Select a group", "mobile"); ?></option>
                    <?php foreach ($groups as $group): ?>
                        <option value="<?php echo htmlspecialchars($group['id']); ?>" <?php echo ($group_id == $group['id']) ? 'selected' : ''; ?>>
                            <?php echo htmlspecialchars($group['name']); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </td>
        </tr>

        <!-- Configuration Input -->
        <tr id="configuration_row" style="display: none;">
            <td style="font-weight: bold;"><?php echo _T("Configuration", "mobile"); ?></td>
            <td>
                <select name="configuration_input" id="configuration_input">
                    <option value=""><?php echo _T("Select a configuration", "mobile"); ?></option>
                    <?php foreach ($configurations as $config): ?>
                        <option value="<?php echo htmlspecialchars($config['id']); ?>" <?php echo ($configuration_id == $config['id']) ? 'selected' : ''; ?>>
                            <?php echo htmlspecialchars($config['name']); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </td>
        </tr>

        <!-- Message Type -->
        <tr>
            <td style="font-weight: bold;"><?php echo _T("Message Type", "mobile"); ?></td>
            <td>
                <select name="message_type" id="message_type">
                    <option value="configUpdated" <?php echo $message_type === "configUpdated" ? "selected" : ""; ?>>configUpdated</option>
                    <option value="runApp" <?php echo $message_type === "runApp" ? "selected" : ""; ?>>runApp</option>
                    <option value="uninstallApp" <?php echo $message_type === "uninstallApp" ? "selected" : ""; ?>>uninstallApp</option>
                    <option value="deleteFile" <?php echo $message_type === "deleteFile" ? "selected" : ""; ?>>deleteFile</option>
                    <option value="deleteDir" <?php echo $message_type === "deleteDir" ? "selected" : ""; ?>>deleteDir</option>
                    <option value="purgeDir" <?php echo $message_type === "purgeDir" ? "selected" : ""; ?>>purgeDir</option>
                    <option value="permissiveMode" <?php echo $message_type === "permissiveMode" ? "selected" : ""; ?>>permissiveMode</option>
                    <option value="intent" <?php echo $message_type === "intent" ? "selected" : ""; ?>>intent</option>
                    <option value="runCommand" <?php echo $message_type === "runCommand" ? "selected" : ""; ?>>runCommand</option>
                    <option value="reboot" <?php echo $message_type === "reboot" ? "selected" : ""; ?>>reboot</option>
                    <option value="exitKiosk" <?php echo $message_type === "exitKiosk" ? "selected" : ""; ?>>exitKiosk</option>
                    <option value="clearDownloadHistory" <?php echo $message_type === "clearDownloadHistory" ? "selected" : ""; ?>>clearDownloadHistory</option>
                    <option value="grantPermissions" <?php echo $message_type === "grantPermissions" ? "selected" : ""; ?>>grantPermissions</option>
                    <option value="(custom)" <?php echo $message_type === "(custom)" ? "selected" : ""; ?>>(custom)</option>
                </select>
            </td>
        </tr>

        <!-- Payload Text -->
        <tr>
            <td style="font-weight: bold;"><?php echo _T("Payload", "mobile"); ?></td>
            <td>
                <textarea name="payload" id="payload" rows="6" cols="50" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-family: Arial, sans-serif;"><?php echo htmlspecialchars($payload_text); ?></textarea>
            </td>
        </tr>

        <!-- Submit Buttons -->
        <tr>
            <td colspan="2" style="text-align: center; padding: 15px;">
                <button type="submit" name="send_message" value="1" class="btnPrimary" style="margin-right: 10px;">
                    <?php echo _T("Send", "mobile"); ?>
                </button>
                <button type="button" onclick="history.go(-1)" class="btnPrimary">
                    <?php echo _T("Cancel", "mobile"); ?>
                </button>
            </td>
        </tr>
    </table>
</form>

<script type="text/javascript">
// Show/hide input fields based on "Send to" selection
function updateSecondInput() {
    var sendTo = document.getElementById('send_to').value;
    
    // Hide all rows
    document.getElementById('device_row').style.display = 'none';
    document.getElementById('group_row').style.display = 'none';
    document.getElementById('configuration_row').style.display = 'none';
    
    // Show the appropriate row
    if (sendTo === 'device') {
        document.getElementById('device_row').style.display = 'table-row';
    } else if (sendTo === 'group') {
        document.getElementById('group_row').style.display = 'table-row';
    } else if (sendTo === 'configuration') {
        document.getElementById('configuration_row').style.display = 'table-row';
    }
    // For 'all_devices', no additional input row is shown
}

// Initialize the form based on current selection
updateSecondInput();

// Device autocomplete logic
var autocompleteTimeout;

document.getElementById('device_input').addEventListener('input', function(e) {
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
                            document.getElementById('device_input').value = deviceName;
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

// Hide autocomplete when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.id !== 'device_input') {
        document.getElementById('device-suggestions').style.display = 'none';
    }
});
</script>