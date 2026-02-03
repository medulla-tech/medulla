<?php
require_once("modules/mobile/includes/xmlrpc.php");

$deviceId = isset($_GET['id']) ? intval($_GET['id']) : 0;

if ($deviceId <= 0) {
    echo "<p style='color: red; text-align: center;'>" . _T("Invalid device ID", "mobile") . "</p>";
    exit;
}

// device info
$devices = xmlrpc_get_hmdm_devices();
$device = null;
foreach ($devices as $d) {
    if (isset($d['id']) && $d['id'] == $deviceId) {
        $device = $d;
        break;
    }
}

if (!$device) {
    echo "<p style='color: red; text-align: center;'>" . _T("Device not found", "mobile") . "</p>";
    exit;
}

$deviceNumber = $device['number'] ?? _T("Unknown", "mobile");
$deviceDescription = $device['description'] ?? '';
?>
<style type="text/css">
    .popup{
        width : 500px
    }

    td img {
        transition: filter 0.3s ease;
    }

    td img:hover {
        filter: brightness(50%);
        cursor: pointer;
    }
</style>

    <div style="width : 600px;">
        <?
        echo "<h1>"._T("Quick Actions", "mobile")."</h1>";
        echo "<h2>"._T("Device", "mobile")." : ".$deviceNumber."</h2>";
        if ($deviceDescription) {
            echo "<h2>"._T("Description", "mobile")." : ".$deviceDescription."</h2>";
        }
        ?>
        <table style="width : 500px;">
            <tr>
            <?
                    echo sprintf("<td id='reboot0' align='center' title='%s'><img src='img/actions/restart.svg' height='70' width='70'></td>", _T("Click here to reboot this device", "mobile"));
                    echo sprintf("<td id='sync0' align='center' title='%s'><img src='modules/updates/graph/navbar/updates.svg' height='70' width='70'></td>", _T("Click here to update configuration", "mobile"));
                ?>
            </tr>
                <tr>
                <?
                    echo '<td id="reboot" align="center">'._T("Reboot", "mobile")."</td>";
                    echo '<td id="sync" align="center">'._T("Update Config", "mobile")."</td>";
                ?>
            </tr>
            </table>
            <?php
                echo "<table>";
                    echo '<tr>';
                    echo '<td>'._T("Custom command", "mobile").'</td>
                    <td>
                        <select id="select">';
                        echo '<option value="runApp">'._T("Run App", "mobile").'</option>';
                        echo '<option value="uninstallApp">'._T("Uninstall App", "mobile").'</option>';
                        echo '<option value="deleteFile">'._T("Delete File", "mobile").'</option>';
                        echo '<option value="deleteDir">'._T("Delete Directory", "mobile").'</option>';
                        echo '<option value="purgeDir">'._T("Purge Directory", "mobile").'</option>';
                        echo '<option value="permissiveMode">'._T("Permissive Mode", "mobile").'</option>';
                        echo '<option value="intent">'._T("Send Intent", "mobile").'</option>';
                        echo '<option value="runCommand">'._T("Run Command", "mobile").'</option>';
                        echo '<option value="exitKiosk">'._T("Exit Kiosk", "mobile").'</option>';
                        echo '<option value="clearDownloadHistory">'._T("Clear Download History", "mobile").'</option>';
                        echo '<option value="grantPermissions">'._T("Grant Permissions", "mobile").'</option>';
                        echo '<option value="custom">'._T("Custom", "mobile").'</option>';
                        echo'</select>
                    </td>
                    <td><input id="buttoncmd" class="btn btn-primary" type=button value="'._T("Send custom command", "mobile").'"></td>';
                    echo '</tr>';
                    echo '<tr id="custom-type-row" style="display: none;">';
                    echo '<td>'._T("Message type", "mobile").'</td>';
                    echo '<td colspan="2"><input type="text" id="custom-type" style="width: 100%;" placeholder="'._T("Enter custom message type", "mobile").'"></td>';
                    echo '</tr>';
                    echo '<tr>';
                    echo '<td>'._T("Payload", "mobile").'</td>';
                    echo '<td colspan="2"><textarea id="payload" rows="4" style="width: 100%; font-family: monospace;" placeholder="'._T("Enter JSON payload (optional)", "mobile").'"></textarea></td>';
                    echo '</tr>';
                echo "</table>";
             ?>
    </div>
<script type="text/javascript">
    
    // payload templates
    var payloadTemplates = {
        'runApp': '{\n  "pkg": "app.package.id"\n}',
        'uninstallApp': '{\n  "pkg": "app.package.id"\n}',
        'deleteFile': '{\n  "path": "/path/to/file"\n}',
        'deleteDir': '{\n  "path": "/path/to/dir"\n}',
        'purgeDir': '{\n  "path": "/path/to/dir",\n  "recursive": "1"\n}',
        'intent': '{\n  "action": "android.intent.action.VIEW",\n  "data": "https://medulla-tech.io"\n}',
        'runCommand': '{\n  "command": "shell command"\n}',
        'grantPermissions': '{\n  "pkg": "app.package.id"\n}'
    };
    
    var deviceId = <?php echo $deviceId; ?>;
    
    function submitAction(action, messageType, payload) {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '<?php echo urlStrRedirect("mobile/mobile/deviceQuickActionExec"); ?>';
        
        var fields = {
            'id': deviceId,
            'action': action,
            'message_type': messageType,
            'payload': payload
        };
        
        for (var key in fields) {
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = fields[key];
            form.appendChild(input);
        }
        
        document.body.appendChild(form);
        form.submit();
    }
   
    jQuery(function() {
        jQuery('#select').change(function() {
            var selectedCmd = jQuery(this).val();
            
            if (selectedCmd === 'custom') {
                jQuery('#custom-type-row').show();
            } else {
                jQuery('#custom-type-row').hide();
            }
            
            if (payloadTemplates[selectedCmd]) {
                jQuery('#payload').val(payloadTemplates[selectedCmd]);
            } else {
                jQuery('#payload').val('');
            }
        });
        
        jQuery('#select').trigger('change');
        
        jQuery('#reboot0, #reboot').on('click', function(){
            submitAction('reboot', 'reboot', '');
        });
        
        jQuery('#sync0, #sync').on('click', function(){
            submitAction('configUpdated', 'configUpdated', '');
        });
        
        // custom Command
        jQuery('#buttoncmd').click(function() {
            var messageType = jQuery('#select').val();
            var payload = jQuery('#payload').val();
            
            if (messageType === 'custom') {
                var customType = jQuery('#custom-type').val().trim();
                if (customType === '') {
                    alert('<?php echo _T("Please enter a custom message type.", "mobile"); ?>');
                    return;
                }
                messageType = customType;
            }
            
            if (payload.trim() !== '') {
                try {
                    JSON.parse(payload);
                } catch (e) {
                    alert('<?php echo _T("Invalid JSON payload. Please check the format.", "mobile"); ?>');
                    return;
                }
            }
            
            submitAction('custom', messageType, payload);
        });
    });

</script>
