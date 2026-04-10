<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$_modal_devices = [];
try {
    $tmp = xmlrpc_get_hmdm_devices();
    if (is_array($tmp)) {
        $_modal_devices = $tmp;
    }
} catch (Exception $e) {
    $_modal_devices = [];
}

$p = new PageGenerator(_T("List of all groups", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

echo '<button class="btn btn-small btn-primary" type="button" onclick="openAddGroupModal()">'._T("Add group","mobile").'</button>';

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxGroupList"));
$ajax->display();
echo '<div id="mobileFlash" style="display:none;margin-bottom:10px;"></div>';
$ajax->displayDivToUpdate();

?>

<div id="addGroupModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; overflow-y:auto;">
    <div style="background:#fff; width:640px; margin:60px auto 40px; border-radius:6px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.25);">
        <div style="background:#25607d; padding:16px 24px; display:flex; align-items:center; justify-content:space-between;">
            <span style="color:#fff; font-size:1.15em; font-weight:600;"><?php echo _T("Add group", "mobile"); ?></span>
            <button type="button" onclick="closeAddGroupModal()" style="background:none; border:none; color:#fff; font-size:1.3em; line-height:1; cursor:pointer; padding:0 2px; opacity:0.85;">&times;</button>
        </div>
        <div style="padding:24px;">
            <div id="addGroupError" style="display:none; color:#c00; margin-bottom:12px;"></div>
            <table style="width:100%; border-collapse:collapse; margin-bottom:16px;">
                <tr>
                    <td style="width:32%; padding:6px 0; font-weight:bold;"><?php echo _T("Group name", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_group_name" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
            </table>

            <?php if (!empty($_modal_devices)): ?>
            <div style="display:flex; gap:10px; align-items:flex-start;">
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:bold; margin-bottom:6px;"><?php echo _T("All devices", "mobile"); ?></div>
                    <input type="text" id="modal_device_filter" style="width:100%; padding:4px; box-sizing:border-box; margin-bottom:4px;" placeholder="<?php echo _T('Filter...', 'mobile'); ?>" oninput="modalGroupFilterDevices(this.value)" />
                    <select id="modal_group_available" multiple size="8" style="width:100%;">
                        <?php foreach ($_modal_devices as $dev):
                            $devId   = $dev['id'] ?? $dev['deviceId'] ?? null;
                            $devName = $dev['number'] ?? '';
                            if (!$devId) continue;
                            $key = htmlspecialchars($devName . '##' . $devId);
                        ?>
                        <option value="<?php echo $key; ?>"><?php echo htmlspecialchars($devName); ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; padding-top:52px;">
                    <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="modalGroupDeviceAdd()" title="<?php echo _T('Add', 'mobile'); ?>">&#8594;</button>
                    <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="modalGroupDeviceRemove()" title="<?php echo _T('Remove', 'mobile'); ?>">&#8592;</button>
                </div>
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:bold; margin-bottom:6px;"><?php echo _T("Group members", "mobile"); ?></div>
                    <div style="height:28px;"></div>
                    <select id="modal_group_selected" multiple size="8" style="width:100%;"></select>
                </div>
            </div>
            <?php endif; ?>

            <div style="margin-top:20px; text-align:right;">
                <button type="button" class="btnSecondary" onclick="closeAddGroupModal()" style="margin-right:8px;"><?php echo _T("Cancel", "mobile"); ?></button>
                <button type="button" class="btnPrimary" onclick="submitAddGroup()"><?php echo _T("Add", "mobile"); ?></button>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
function openAddGroupModal() {
    jQuery('#modal_group_name').val('');
    jQuery('#modal_device_filter').val('');
    jQuery('#addGroupError').hide().text('');
    jQuery('#modal_group_selected option').each(function() {
        jQuery('#modal_group_available').append(jQuery(this).clone());
        jQuery(this).remove();
    });
    jQuery('#addGroupModal').fadeIn(150);
}
function closeAddGroupModal() {
    jQuery('#addGroupModal').fadeOut(150);
}
jQuery('#addGroupModal').on('click', function(e) {
    if (e.target.id === 'addGroupModal') closeAddGroupModal();
});
function modalGroupDeviceAdd() {
    jQuery('#modal_group_available option:selected').each(function() {
        jQuery('#modal_group_selected').append(jQuery(this).clone());
        jQuery(this).remove();
    });
}
function modalGroupDeviceRemove() {
    jQuery('#modal_group_selected option:selected').each(function() {
        jQuery('#modal_group_available').append(jQuery(this).clone());
        jQuery(this).remove();
    });
}
function modalGroupFilterDevices(q) {
    jQuery('#modal_group_available option').each(function() {
        var text = jQuery(this).text().toLowerCase();
        jQuery(this).toggle(!q || text.indexOf(q.toLowerCase()) !== -1);
    });
}
function submitAddGroup() {
    var name = jQuery('#modal_group_name').val().trim();
    jQuery('#addGroupError').hide().text('');
    if (!name) {
        jQuery('#addGroupError').text('<?php echo _T("Group name is required", "mobile"); ?>').show();
        return;
    }
    var devices = [];
    jQuery('#modal_group_selected option').each(function() {
        devices.push(jQuery(this).val());
    });
    jQuery.ajax({
        url: 'modules/mobile/mobile/addGroupAjax.php',
        method: 'POST',
        data: { 'name': name, 'devices': devices },
        dataType: 'json',
        success: function(resp) {
            if (resp.status === 'ok') {
                closeAddGroupModal();
                jQuery('#container').load('<?php echo urlStrRedirect("mobile/mobile/ajaxGroupList"); ?>', function() {
                    mobileFlash('success', resp.message);
                });
            } else {
                jQuery('#addGroupError').text(resp.message).show();
            }
        },
        error: function() {
            jQuery('#addGroupError').text('<?php echo _T("An error occurred. Please try again.", "mobile"); ?>').show();
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
</script>
