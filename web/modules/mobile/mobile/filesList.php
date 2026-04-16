<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Files", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}

$_file_configurations = [];
try {
    $tmp = xmlrpc_get_hmdm_configurations();
    if (is_array($tmp)) {
        $_file_configurations = $tmp;
    }
} catch (Exception $e) {
    $_file_configurations = [];
}

echo '<button class="btn btn-small btn-primary" type="button" onclick="openAddFileModal()">'._T("Add file","mobile").'</button>';

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxFilesList"));
$ajax->display();
echo '<div id="mobileFlash" style="display:none;margin-bottom:10px;"></div>';
$ajax->displayDivToUpdate();

?>

<div id="addFileModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; overflow-y:auto;">
    <div style="background:#fff; width:540px; margin:60px auto 40px; border-radius:6px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.25);">
        <div style="background:#25607d; padding:16px 24px; display:flex; align-items:center; justify-content:space-between;">
            <span style="color:#fff; font-size:1.15em; font-weight:600;"><?php echo _T("Add file", "mobile"); ?></span>
            <button type="button" onclick="closeAddFileModal()" style="background:none; border:none; color:#fff; font-size:1.3em; line-height:1; cursor:pointer; padding:0 2px; opacity:0.85;">&times;</button>
        </div>
        <div style="padding:24px;">
            <div id="addFileError" style="display:none; color:#c00; margin-bottom:12px;"></div>

            <div style="margin-bottom:14px;">
                <label style="margin-right:20px; font-weight:bold;">
                    <input type="radio" name="modal_file_source" value="upload" checked onchange="modalFileSourceChange(this.value)" />
                    <?php echo _T("Upload a file", "mobile"); ?>
                </label>
                <label style="font-weight:bold;">
                    <input type="radio" name="modal_file_source" value="external" onchange="modalFileSourceChange(this.value)" />
                    <?php echo _T("External URL", "mobile"); ?>
                </label>
            </div>

            <table style="width:100%; border-collapse:collapse;">
                <tr id="modal_file_row_upload">
                    <td style="width:35%; padding:6px 0; font-weight:bold;"><?php echo _T("File", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="file" id="modal_file_upload" style="width:100%; box-sizing:border-box;" onchange="modalFileSelected(this)" /></td>
                </tr>
                <tr id="modal_file_row_url" style="display:none;">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("URL", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_file_url" style="width:100%; padding:5px; box-sizing:border-box;" placeholder="https://..." /></td>
                </tr>
                <tr id="modal_file_row_name">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("File name", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_file_name" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Description", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_file_desc" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Path on device", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_file_path" style="width:100%; padding:5px; box-sizing:border-box;" placeholder="/sdcard/..." /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Variable Content", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_file_variable" /></td>
                </tr>
            </table>

            <?php if (!empty($_file_configurations)): ?>
            <div style="margin-top:16px;">
                <div style="font-weight:bold; margin-bottom:8px; padding-bottom:4px; border-bottom:2px solid #e0e0e0;"><?php echo _T("Link to Configurations", "mobile"); ?></div>
                <div style="display:flex; flex-wrap:wrap; gap:6px 20px;">
                    <?php foreach ($_file_configurations as $conf): ?>
                    <label style="display:flex; align-items:center; gap:5px;">
                        <input type="checkbox" class="modal_file_config" value="<?php echo (int)$conf['id']; ?>" />
                        <?php echo htmlspecialchars($conf['name']); ?>
                    </label>
                    <?php endforeach; ?>
                </div>
            </div>
            <?php endif; ?>

            <div style="margin-top:20px; text-align:right;">
                <button type="button" class="btnSecondary" onclick="closeAddFileModal()" style="margin-right:8px;"><?php echo _T("Cancel", "mobile"); ?></button>
                <button type="button" class="btnPrimary" id="modal_file_submit" onclick="submitAddFile()"><?php echo _T("Add", "mobile"); ?></button>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
function openAddFileModal() {
    jQuery('#modal_file_upload').val('');
    jQuery('#modal_file_url').val('');
    jQuery('#modal_file_name').val('');
    jQuery('#modal_file_desc').val('');
    jQuery('#modal_file_path').val('');
    jQuery('.modal_file_config').prop('checked', false);
    jQuery('#modal_file_variable').prop('checked', false);
    jQuery('#addFileError').hide().text('');
    jQuery('input[name="modal_file_source"][value="upload"]').prop('checked', true);
    jQuery('#modal_file_row_upload').show();
    jQuery('#modal_file_row_url').hide();
    jQuery('#addFileModal').fadeIn(150);
}
function closeAddFileModal() {
    jQuery('#addFileModal').fadeOut(150);
}
jQuery('#addFileModal').on('click', function(e) {
    if (e.target.id === 'addFileModal') closeAddFileModal();
});
function modalFileSourceChange(source) {
    if (source === 'upload') {
        jQuery('#modal_file_row_upload').show();
        jQuery('#modal_file_row_url').hide();
        jQuery('#modal_file_row_name').show();
    } else {
        jQuery('#modal_file_row_upload').hide();
        jQuery('#modal_file_row_url').show();
        jQuery('#modal_file_row_name').hide();
        jQuery('#modal_file_name').val('');
    }
}
function modalFileSelected(input) {
    if (input.files && input.files[0] && !jQuery('#modal_file_name').val()) {
        jQuery('#modal_file_name').val(input.files[0].name);
    }
}
function submitAddFile() {
    var source   = jQuery('input[name="modal_file_source"]:checked').val();
    var fileName = jQuery('#modal_file_name').val().trim();
    var fileUrl  = jQuery('#modal_file_url').val().trim();
    jQuery('#addFileError').hide().text('');
    if (source === 'upload' && !fileName) {
        jQuery('#addFileError').text('<?php echo _T("File name is required", "mobile"); ?>').show();
        return;
    }
    if (source === 'external') {
        if (!fileUrl) {
            jQuery('#addFileError').text('<?php echo _T("File URL is required", "mobile"); ?>').show();
            return;
        }
        if (!fileName) {
            fileName = fileUrl.split('/').pop().split('?')[0] || 'file';
        }
    }
    var formData = new FormData();
    formData.append('file-source', source);
    formData.append('file_name', fileName);
    formData.append('description', jQuery('#modal_file_desc').val().trim());
    formData.append('path_device', jQuery('#modal_file_path').val().trim());
    formData.append('variable_content', jQuery('#modal_file_variable').is(':checked') ? '1' : '0');
    jQuery('.modal_file_config:checked').each(function() {
        formData.append('configs[]', jQuery(this).val());
    });
    if (source === 'upload') {
        var fileInput = document.getElementById('modal_file_upload');
        if (!fileInput.files || !fileInput.files[0]) {
            jQuery('#addFileError').text('<?php echo _T("Please select a file to upload", "mobile"); ?>').show();
            return;
        }
        formData.append('file_upload', fileInput.files[0]);
    } else {
        formData.append('file_url', fileUrl);
    }
    jQuery('#modal_file_submit').prop('disabled', true);
    jQuery.ajax({
        url: 'modules/mobile/mobile/addFileAjax.php',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        dataType: 'json',
        success: function(resp) {
            jQuery('#modal_file_submit').prop('disabled', false);
            if (resp.status === 'ok') {
                closeAddFileModal();
                jQuery('#container').load('<?php echo urlStrRedirect("mobile/mobile/ajaxFilesList"); ?>', function() {
                    mobileFlash('success', resp.message);
                });
            } else {
                jQuery('#addFileError').text(resp.message).show();
            }
        },
        error: function() {
            jQuery('#modal_file_submit').prop('disabled', false);
            jQuery('#addFileError').text('<?php echo _T("An error occurred. Please try again.", "mobile"); ?>').show();
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
