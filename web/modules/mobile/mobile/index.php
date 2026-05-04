<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$status = isset($_GET['status']) ? $_GET['status'] : '';

if ($status === 'online') {
    $pageTitle = sprintf(_T("Group 'Phones online at %s' content", 'mobile'), date('Y-m-d H:i:s'));
} elseif ($status === 'offline') {
    $pageTitle = sprintf(_T("Group 'Phones offline at %s' content", 'mobile'), date('Y-m-d H:i:s'));
} else {
    $pageTitle = _T("List of all devices", 'mobile');
}

$p = new PageGenerator($pageTitle);
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}

$_modal_configurations = [];
try {
    $tmp = xmlrpc_get_hmdm_configurations();
    if (is_array($tmp)) {
        $_modal_configurations = $tmp;
    }
} catch (Exception $e) {
    $_modal_configurations = [];
}
$_modal_groups = [];
try {
    $tmp = xmlrpc_get_hmdm_groups();
    if (is_array($tmp)) {
        $_modal_groups = $tmp;
    }
} catch (Exception $e) {
    $_modal_groups = [];
}

echo '<button class="btn btn-small btn-primary" onclick="PopupWindow(event, \'main.php?module=mobile&submod=mobile&action=qrCode&apk=1\', 450); return false;" type="button">'._T("HMDM APK","mobile").'</button>';
echo ' <button class="btn btn-small btn-primary" type="button" onclick="openAddDeviceModal()">'._T("Add device","mobile").'</button>';

$device_keys_json = '[]';
$device_count = 0;
$suggested_group_name = '';
if ($status) {
    $onlineCodes = ['green', 'yellow'];
    $allDevicesForFilter = xmlrpc_get_hmdm_devices();
    if (!is_array($allDevicesForFilter)) $allDevicesForFilter = [];
    $filteredDeviceKeys = [];
    foreach ($allDevicesForFilter as $d) {
        $isOnline = in_array($d['statusCode'] ?? '', $onlineCodes);
        if (($status === 'online') === $isOnline) {
            $devId = $d['id'] ?? $d['deviceId'] ?? '';
            $filteredDeviceKeys[] = $d['number'] . '##' . $devId;
        }
    }
    $device_count = count($filteredDeviceKeys);
    $device_keys_json = json_encode($filteredDeviceKeys);
    $suggested_group_name = ($status === 'online' ? _T("Online", "mobile") : _T("Offline", "mobile")) . '_' . date('Y-m-d_His');
}

if ($status && $device_count > 0): ?>
<ul class="action">
    <li class="quick" title="<?php echo htmlspecialchars(_T('Quick Actions', 'mobile')); ?>">
        <a href="#" onclick="doTempGroupAction('quickaction'); return false;" title="<?php echo htmlspecialchars(_T('Quick Actions', 'mobile')); ?>">&nbsp;</a>
    </li>
    <li class="add" title="<?php echo htmlspecialchars(_T('Send Message', 'mobile')); ?>">
        <a href="#" onclick="doTempGroupAction('message'); return false;" title="<?php echo htmlspecialchars(_T('Send Message', 'mobile')); ?>">&nbsp;</a>
    </li>
    <li class="edit" title="<?php echo htmlspecialchars(_T('Save as Group', 'mobile')); ?>">
        <a href="#" onclick="doTempGroupAction('savegroup'); return false;" title="<?php echo htmlspecialchars(_T('Save as Group', 'mobile')); ?>">&nbsp;</a>
    </li>
</ul>
<?php endif;

if (isset($_GET['error'])) {
	switch ($_GET['error']) {
		case 'missing_device_number':
			new NotifyWidgetFailure(_T('Missing device number for QR Code', 'mobile'));
			break;
		case 'qr_key_missing':
			new NotifyWidgetFailure(_T('Unable to fetch configuration QR key', 'mobile'));
			break;
		default:
			new NotifyWidgetFailure(_T('Unable to load QR Code', 'mobile'));
			break;
	}
}


$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxDeviceList") . ($status ? '&status=' . urlencode($status) : ''));
$ajax->display();
echo '<div id="mobileFlash" style="display:none;margin-bottom:10px;"></div>';
$ajax->displayDivToUpdate();

?>

<div id="addDeviceModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; overflow-y:auto;">
    <div style="background:#fff; width:640px; margin:60px auto 40px; border-radius:6px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.25); position:relative;">
        <div style="background:#25607d; padding:16px 24px; display:flex; align-items:center; justify-content:space-between;">
            <span style="color:#fff; font-size:1.15em; font-weight:600; letter-spacing:0.01em;"><?php echo _T("Add device", "mobile"); ?></span>
            <button type="button" onclick="closeAddDeviceModal()" style="background:none; border:none; color:#fff; font-size:1.3em; line-height:1; cursor:pointer; padding:0 2px; opacity:0.85;">&times;</button>
        </div>
        <div style="padding:24px;">
            <div id="addDeviceError" style="display:none; color:#c00; margin-bottom:12px;"></div>

            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="width:32%; padding:6px 0; font-weight:bold;"><?php echo _T("Device's name", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_add_phone" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Description", "mobile"); ?></td>
                    <td style="padding:6px 0;"><textarea id="modal_desc_zone" style="width:100%; padding:5px; box-sizing:border-box; resize:vertical;" rows="2"></textarea></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("IMEI", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_add_imei" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Email", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_add_custom1" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Configuration", "mobile"); ?> *</td>
                    <td style="padding:6px 0;">
                        <select id="modal_configuration_id" style="width:100%; padding:5px; box-sizing:border-box;">
                            <option value=""></option>
                            <?php foreach ($_modal_configurations as $conf): ?>
                            <option value="<?php echo (int)$conf['id']; ?>"><?php echo htmlspecialchars($conf['name']); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </td>
                </tr>
            </table>

            <?php if (!empty($_modal_groups)): ?>
            <div style="margin-top:16px;">
                <div style="display:flex; gap:10px; align-items:flex-start;">
                    <div style="flex:1; min-width:0;">
                        <div style="font-weight:bold; margin-bottom:6px;"><?php echo _T("Available groups", "mobile"); ?></div>
                        <select id="modal_groups_available" multiple size="6" style="width:100%;">
                            <?php foreach ($_modal_groups as $grp): ?>
                            <option value="<?php echo (int)$grp['id']; ?>"><?php echo htmlspecialchars($grp['name']); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:8px; padding-top:28px;">
                        <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="modalGroupAdd()" title="<?php echo _T('Add', 'mobile'); ?>">&#8594;</button>
                        <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="modalGroupRemove()" title="<?php echo _T('Remove', 'mobile'); ?>">&#8592;</button>
                    </div>
                    <div style="flex:1; min-width:0;">
                        <div style="font-weight:bold; margin-bottom:6px;"><?php echo _T("Selected groups", "mobile"); ?></div>
                        <select id="modal_groups_selected" multiple size="6" style="width:100%;"></select>
                    </div>
                </div>
            </div>
            <?php endif; ?>

            <div style="margin-top:20px; text-align:right;">
                <button type="button" class="btnSecondary" onclick="closeAddDeviceModal()" style="margin-right:8px;"><?php echo _T("Cancel", "mobile"); ?></button>
                <button type="button" class="btnPrimary" onclick="submitAddDevice()"><?php echo _T("Add", "mobile"); ?></button>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
function modalGroupAdd() {
    jQuery('#modal_groups_available option:selected').each(function() {
        jQuery('#modal_groups_selected').append(jQuery(this).clone());
        jQuery(this).remove();
    });
}

function modalGroupRemove() {
    jQuery('#modal_groups_selected option:selected').each(function() {
        jQuery('#modal_groups_available').append(jQuery(this).clone());
        jQuery(this).remove();
    });
}

function openAddDeviceModal() {
    jQuery('#modal_add_phone').val('');
    jQuery('#modal_add_imei').val('');
    jQuery('#modal_add_custom1').val('');
    jQuery('#modal_desc_zone').val('');
    jQuery('#modal_configuration_id').val('');
    jQuery('#addDeviceError').hide().text('');
    jQuery('#modal_groups_selected option').each(function() {
        jQuery('#modal_groups_available').append(jQuery(this).clone());
        jQuery(this).remove();
    });
    jQuery('#addDeviceModal').fadeIn(150);
}

function closeAddDeviceModal() {
    jQuery('#addDeviceModal').fadeOut(150);
}

jQuery('#addDeviceModal').on('click', function(e) {
    if (e.target.id === 'addDeviceModal') {
        closeAddDeviceModal();
    }
});

function submitAddDevice() {
    var name   = jQuery('#modal_add_phone').val().trim();
    var imei   = jQuery('#modal_add_imei').val().trim();
    var custom1 = jQuery('#modal_add_custom1').val().trim();
    var desc   = jQuery('#modal_desc_zone').val().trim();
    var config = jQuery('#modal_configuration_id').val();

    jQuery('#addDeviceError').hide().text('');

    if (!name) {
        jQuery('#addDeviceError').text('<?php echo _T("The device name is required", "mobile"); ?>').show();
        return;
    }
    if (config === '') {
        jQuery('#addDeviceError').text('<?php echo _T("Configuration is required", "mobile"); ?>').show();
        return;
    }

    var groups = [];
    jQuery('#modal_groups_selected option').each(function() {
        groups.push(jQuery(this).val());
    });

    var postData = {
        'add-phone':        name,
        'add-imei':         imei,
        'add-custom1':      custom1,
        'desc-zone':        desc,
        'configuration_id': config,
        'groups':           groups
    };

    jQuery.ajax({
        url: 'modules/mobile/mobile/addDeviceAjax.php',
        method: 'POST',
        data: postData,
        dataType: 'json',
        success: function(resp) {
            if (resp.status === 'ok') {
                closeAddDeviceModal();
                jQuery('#container').load('<?php echo urlStrRedirect("mobile/mobile/ajaxDeviceList"); ?>', function() {
                    mobileFlash('success', resp.message);
                });
            } else {
                jQuery('#addDeviceError').text(resp.message).show();
            }
        },
        error: function() {
            jQuery('#addDeviceError').text('<?php echo _T("An error occurred. Please try again.", "mobile"); ?>').show();
        }
    });
}
function mobileFlash(type, msg) {
    var bg = type === 'success' ? '#dff0d8' : '#f2dede';
    var color = type === 'success' ? '#3c763d' : '#a94442';
    var border = type === 'success' ? '#d6e9c6' : '#ebccd1';
    jQuery('#mobileFlash')
        .html(msg)
        .css({'background':bg,'color':color,'border':'1px solid '+border,'padding':'10px 16px','border-radius':'4px','font-weight':'500'})
        .show();
    setTimeout(function(){ jQuery('#mobileFlash').fadeOut(400); }, 4000);
}

<?php if ($status && $device_count > 0): ?>
var filteredDeviceKeys = <?php echo $device_keys_json; ?>;

function doTempGroupAction(action) {
    if (action === 'quickaction') {
        jQuery.ajax({
            url: 'main.php?module=mobile&submod=mobile&action=groupQuickAction',
            type: 'POST',
            data: jQuery.param({ device_keys: filteredDeviceKeys }),
            success: function(html) {
                PopupWindow(null, null, 650, null, html);
            },
            error: function() {
                mobileFlash('error', '<?php echo addslashes(_T("An error occurred. Please try again.", "mobile")); ?>');
            }
        });
        return;
    }

    var form = document.createElement('form');
    form.method = 'POST';
    form.style.display = 'none';

    filteredDeviceKeys.forEach(function(k) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = action === 'savegroup' ? 'devices[]' : 'device_keys[]';
        input.value = k;
        form.appendChild(input);
    });

    if (action === 'savegroup') {
        form.action = 'main.php?module=mobile&submod=mobile&action=addGroup';
        var nameInput = document.createElement('input');
        nameInput.type = 'hidden';
        nameInput.name = 'suggested_name';
        nameInput.value = '<?php echo addslashes($suggested_group_name); ?>';
        form.appendChild(nameInput);
        document.body.appendChild(form);
        form.submit();
    } else if (action === 'message') {
        form.action = 'main.php?module=mobile&submod=mobile&action=newMessage';
        document.body.appendChild(form);
        form.submit();
    }
}
<?php endif; ?>
</script>
