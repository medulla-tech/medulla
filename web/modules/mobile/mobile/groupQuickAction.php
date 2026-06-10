<?php
require_once("modules/mobile/includes/xmlrpc.php");

$deviceKeys = isset($_POST['device_keys']) && is_array($_POST['device_keys']) ? $_POST['device_keys'] : [];
$groupId = isset($_GET['group_id']) ? intval($_GET['group_id']) : 0;

if (empty($deviceKeys) && $groupId <= 0) {
    echo "<p style='color: red; text-align: center;'>" . _T("No devices or group specified", "mobile") . "</p>";
    exit;
}

if (!empty($deviceKeys)) {
    $headerText = sprintf(_T("%d device(s) selected", "mobile"), count($deviceKeys));
    $execTarget = 'device_keys';
} else {
    $groups = xmlrpc_get_hmdm_groups();
    $groupName = _T("Unknown", "mobile");
    foreach ($groups as $g) {
        if (isset($g['id']) && $g['id'] == $groupId) {
            $groupName = $g['name'];
            break;
        }
    }
    $headerText = _T("Group", "mobile") . ": " . htmlspecialchars($groupName);
    $execTarget = 'group_id';
}
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

    <div style="width: 100%;">
        <?php
        echo "<h1>"._T("Quick Actions", "mobile")."</h1>";
        echo "<h2>" . $headerText . "</h2>";
        ?>
        <table style="width: 100%;">
            <tr>
            <?php
                    echo sprintf("<td id='reboot0' align='center' title='%s'><img src='img/actions/restart.svg' height='70' width='70'></td>", _T("Click here to reboot devices in this group", "mobile"));
                    echo sprintf("<td id='sync0' align='center' title='%s'><img src='modules/updates/graph/navbar/updates.svg' height='70' width='70'></td>", _T("Click here to update configuration", "mobile"));
                ?>
            </tr>
                <tr>
                <?php
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
                        echo '<option value="reboot">'._T("Reboot", "mobile").'</option>';
                        echo '<option value="lockDevice">'._T("Lock screen", "mobile").'</option>';
                        echo '<option value="wipe">'._T("Factory reset", "mobile").'</option>';
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
    var payloadTemplates = {
        'reboot': '',
        'lockDevice': '',
        'wipe': '',
        'runApp': '{\n  "pkg": "app.package.id"\n}',
        'uninstallApp': '{\n  "pkg": "app.package.id"\n}',
        'deleteFile': '{\n  "path": "/path/to/file"\n}',
        'deleteDir': '{\n  "path": "/path/to/dir"\n}',
        'purgeDir': '{\n  "path": "/path/to/dir",\n  "recursive": "1"\n}',
        'intent': '{\n  "action": "android.intent.action.VIEW",\n  "data": "https://medulla-tech.io"\n}',
        'runCommand': '{\n  "command": "shell command"\n}',
        'grantPermissions': '{\n  "pkg": "app.package.id"\n}'
    };

    var _destructiveTypes = ['wipe', 'reboot', 'lockDevice', 'runCommand', 'purgeDir', 'deleteDir'];
    var _destructiveLabels = {
        'wipe':       '<?php echo addslashes(_T("Factory Reset", "mobile")); ?>',
        'reboot':     '<?php echo addslashes(_T("Reboot", "mobile")); ?>',
        'lockDevice': '<?php echo addslashes(_T("Lock Screen", "mobile")); ?>',
        'runCommand': '<?php echo addslashes(_T("Run Command", "mobile")); ?>',
        'purgeDir':   '<?php echo addslashes(_T("Purge Directory", "mobile")); ?>',
        'deleteDir':  '<?php echo addslashes(_T("Delete Directory", "mobile")); ?>'
    };
    function requireConfirm(action, messageType, payload) {
        if (_destructiveTypes.indexOf(messageType) === -1) { submitAction(action, messageType, payload); return; }
        var label = _destructiveLabels[messageType] || messageType;
        window._mobileDestructiveAction = function() { submitAction(action, messageType, payload); };
        var savedContent = jQuery('#__popup_container').html();
        var savedWidth = jQuery('#popup').css('width');
        window._mobileRestorePopup = function() {
            jQuery('#popup').css('width', savedWidth);
            jQuery('#__popup_container').html(savedContent);
            var $p = jQuery('#popup');
            $p.css({'visibility':'hidden','display':'block'});
            $p.css({'top':'50%','left':'50%',
                    'margin-top': -($p.outerHeight()/2)+'px',
                    'margin-left': -($p.outerWidth()/2)+'px',
                    'visibility':'visible'});
        };
        var msg = '<?php echo addslashes(_T("You are about to send:", "mobile")); ?> <strong>' + label + '<\/strong> <?php echo addslashes(_T("to group", "mobile")); ?> <strong><?php echo addslashes(htmlspecialchars($groupName, ENT_QUOTES)); ?><\/strong>. <?php echo addslashes(_T("This action may be irreversible.", "mobile")); ?>';
        var html = '<div style="padding:10px">'
                 + '<div class="alert alert-warning">' + msg + '<\/div>'
                 + '<div style="text-align:center">'
                 + '<button class="btn btn-danger" onclick="var f=window._mobileDestructiveAction;window._mobileDestructiveAction=null;window._mobileRestorePopup=null;closePopup();if(f)f();"><?php echo addslashes(_T("Confirm", "mobile")); ?><\/button>'
                 + ' <button class="btn btnSecondary" onclick="var r=window._mobileRestorePopup;window._mobileDestructiveAction=null;window._mobileRestorePopup=null;if(r)r();return false;"><?php echo addslashes(_T("Cancel", "mobile")); ?><\/button>'
                 + '<\/div><\/div>';
        PopupWindow(null, null, 0, function() {
            var $p = jQuery('#popup');
            $p.css({'top':'50%','left':'50%',
                    'margin-top': -($p.outerHeight()/2)+'px',
                    'margin-left': -($p.outerWidth()/2)+'px'});
            jQuery('#overlay').fadeIn().click(function() {
                var r=window._mobileRestorePopup;window._mobileDestructiveAction=null;window._mobileRestorePopup=null;if(r)r();
            });
        }, html);
    }

    var execTarget = '<?php echo $execTarget; ?>';
    var deviceKeys = <?php echo json_encode(array_values($deviceKeys)); ?>;
    var groupId = <?php echo $groupId; ?>;

    function submitAction(action, messageType, payload) {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '<?php echo urlStrRedirect("mobile/mobile/groupQuickActionExec"); ?>';

        var actionInput = document.createElement('input');
        actionInput.type = 'hidden';
        actionInput.name = 'action';
        actionInput.value = action;
        form.appendChild(actionInput);

        var msgTypeInput = document.createElement('input');
        msgTypeInput.type = 'hidden';
        msgTypeInput.name = 'message_type';
        msgTypeInput.value = messageType;
        form.appendChild(msgTypeInput);

        var payloadInput = document.createElement('input');
        payloadInput.type = 'hidden';
        payloadInput.name = 'payload';
        payloadInput.value = payload;
        form.appendChild(payloadInput);

        if (execTarget === 'device_keys') {
            deviceKeys.forEach(function(k) {
                var inp = document.createElement('input');
                inp.type = 'hidden';
                inp.name = 'device_keys[]';
                inp.value = k;
                form.appendChild(inp);
            });
        } else {
            var gidInput = document.createElement('input');
            gidInput.type = 'hidden';
            gidInput.name = 'group_id';
            gidInput.value = groupId;
            form.appendChild(gidInput);
        }

        document.body.appendChild(form);
        form.submit();
    }

    jQuery(function() {
        jQuery('#reboot0, #reboot').on('click', function(){
            requireConfirm('reboot', 'reboot', '');
        });

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

        jQuery('#sync0, #sync').on('click', function(){
            submitAction('configUpdated', 'configUpdated', '');
        });

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

                requireConfirm('custom', messageType, payload);
        });
    });

</script>
