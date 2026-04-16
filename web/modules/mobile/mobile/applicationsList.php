<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Applications", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}

$_app_files = [];
try {
    $tmp = xmlrpc_get_hmdm_files();
    if (is_array($tmp)) $_app_files = $tmp;
} catch (Exception $e) {
    $_app_files = [];
}

echo '<button class="btn btn-small btn-primary" type="button" onclick="openAddAppModal()">'._T("Add application","mobile").'</button>';

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxApplicationsList"));
$ajax->display();
echo '<div id="mobileFlash" style="display:none;margin-bottom:10px;"></div>';
$ajax->displayDivToUpdate();

?>

<div id="addAppModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; overflow-y:auto;">
    <div style="background:#fff; width:640px; margin:60px auto 40px; border-radius:6px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.25);">
        <div style="background:#25607d; padding:16px 24px; display:flex; align-items:center; justify-content:space-between;">
            <span style="color:#fff; font-size:1.15em; font-weight:600;"><?php echo _T("Add application", "mobile"); ?></span>
            <button type="button" onclick="closeAddAppModal()" style="background:none; border:none; color:#fff; font-size:1.3em; line-height:1; cursor:pointer; padding:0 2px; opacity:0.85;">&times;</button>
        </div>
        <div style="padding:24px;">
            <div id="addAppError" style="display:none; color:#c00; margin-bottom:12px;"></div>

            <div style="margin-bottom:16px; display:flex; gap:8px;">
                <button type="button" id="tab_app"    class="btnPrimary"   style="flex:1;" onclick="appTabSwitch('app')"><?php echo _T("App", "mobile"); ?></button>
                <button type="button" id="tab_web"    class="btnSecondary" style="flex:1;" onclick="appTabSwitch('web')"><?php echo _T("Web Page", "mobile"); ?></button>
                <button type="button" id="tab_intent" class="btnSecondary" style="flex:1;" onclick="appTabSwitch('intent')"><?php echo _T("System Action", "mobile"); ?></button>
            </div>
            <input type="hidden" id="modal_app_type" value="app" />

            <!-- ===== APP TAB ===== -->
            <table id="app_fields" style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="width:38%; padding:6px 0; font-weight:bold;"><?php echo _T("Name", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_name_app" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Package", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_pkg" style="width:100%; padding:5px; box-sizing:border-box;" placeholder="com.example.app" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Version", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_version" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Run after install", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_app_runafter" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Run at boot", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_app_runatboot" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("System app", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_app_system" onchange="appUpdateApkVisibility()" /></td>
                </tr>
                <tr id="app_row_url">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("APK URL", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_url_app" style="width:100%; padding:5px; box-sizing:border-box;" placeholder="http://..." /></td>
                </tr>
                <tr id="app_row_upload">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Upload APK", "mobile"); ?></td>
                    <td style="padding:6px 0;">
                        <input type="file" id="modal_app_apk_file" accept=".apk,.xapk" style="width:100%;" onchange="appHandleApkUpload(this)" />
                        <div id="modal_app_apk_status" style="margin-top:4px; font-size:0.85em; color:#666;"></div>
                    </td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Architecture", "mobile"); ?></td>
                    <td style="padding:6px 0;">
                        <select id="modal_app_arch" style="width:100%; padding:5px; box-sizing:border-box;">
                            <option value=""><?php echo _T("None (Universal APK)", "mobile"); ?></option>
                            <option value="armeabi-v7a">armeabi-v7a</option>
                            <option value="arm64-v8a">arm64-v8a</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Show icon", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_app_showicon" onchange="appUpdateIconVisibility('app')" /></td>
                </tr>
                <tr class="app-icon-extra" style="display:none;">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Icon", "mobile"); ?></td>
                    <td style="padding:6px 0;"><select id="modal_icon_select_app" style="width:100%; padding:5px; box-sizing:border-box;"><option value=""><?php echo _T("Choose an icon", "mobile"); ?></option></select></td>
                </tr>
                <tr class="app-icon-extra" style="display:none;">
                    <td style="padding:6px 0;"></td>
                    <td style="padding:6px 0;"><button type="button" class="btnPrimary" onclick="openNewIconModal()"><?php echo _T("New icon", "mobile"); ?></button></td>
                </tr>
                <tr class="app-icon-extra" style="display:none;">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Icon text", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_icon_text_app" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
            </table>
            <input type="hidden" id="modal_app_versioncode" value="" />
            <input type="hidden" id="modal_app_filepath" value="" />

            <!-- ===== WEB TAB ===== -->
            <table id="web_fields" style="display:none; width:100%; border-collapse:collapse;">
                <tr>
                    <td style="width:38%; padding:6px 0; font-weight:bold;"><?php echo _T("Name", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_name_web" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("URL", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_url_web" style="width:100%; padding:5px; box-sizing:border-box;" placeholder="https://..." /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Kiosk browser", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_app_kiosk" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Show icon", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_web_showicon" onchange="appUpdateIconVisibility('web')" /></td>
                </tr>
                <tr class="web-icon-extra" style="display:none;">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Icon", "mobile"); ?></td>
                    <td style="padding:6px 0;"><select id="modal_icon_select_web" style="width:100%; padding:5px; box-sizing:border-box;"><option value=""><?php echo _T("Choose an icon", "mobile"); ?></option></select></td>
                </tr>
                <tr class="web-icon-extra" style="display:none;">
                    <td style="padding:6px 0;"></td>
                    <td style="padding:6px 0;"><button type="button" class="btnPrimary" onclick="openNewIconModal()"><?php echo _T("New icon", "mobile"); ?></button></td>
                </tr>
                <tr class="web-icon-extra" style="display:none;">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Icon text", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_icon_text_web" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
            </table>

            <!-- ===== INTENT TAB ===== -->
            <table id="intent_fields" style="display:none; width:100%; border-collapse:collapse;">
                <tr>
                    <td style="width:38%; padding:6px 0; font-weight:bold;"><?php echo _T("Name", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_name_intent" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Action", "mobile"); ?> *</td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_action" style="width:100%; padding:5px; box-sizing:border-box;" placeholder="android.intent.action.MAIN" /></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Show icon", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="checkbox" id="modal_intent_showicon" onchange="appUpdateIconVisibility('intent')" /></td>
                </tr>
                <tr class="intent-icon-extra" style="display:none;">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Icon", "mobile"); ?></td>
                    <td style="padding:6px 0;"><select id="modal_icon_select_intent" style="width:100%; padding:5px; box-sizing:border-box;"><option value=""><?php echo _T("Choose an icon", "mobile"); ?></option></select></td>
                </tr>
                <tr class="intent-icon-extra" style="display:none;">
                    <td style="padding:6px 0;"></td>
                    <td style="padding:6px 0;"><button type="button" class="btnPrimary" onclick="openNewIconModal()"><?php echo _T("New icon", "mobile"); ?></button></td>
                </tr>
                <tr class="intent-icon-extra" style="display:none;">
                    <td style="padding:6px 0; font-weight:bold;"><?php echo _T("Icon text", "mobile"); ?></td>
                    <td style="padding:6px 0;"><input type="text" id="modal_app_icon_text_intent" style="width:100%; padding:5px; box-sizing:border-box;" /></td>
                </tr>
            </table>

            <div style="margin-top:20px; text-align:right;">
                <button type="button" class="btnSecondary" onclick="closeAddAppModal()" style="margin-right:8px;"><?php echo _T("Cancel", "mobile"); ?></button>
                <button type="button" class="btnPrimary" id="modal_app_submit" onclick="submitAddApp()"><?php echo _T("Add", "mobile"); ?></button>
            </div>
        </div>
    </div>
</div>

<!-- New icon modal -->
<div id="newIconModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:10000;">
    <div style="width:500px; margin:100px auto; background:#fff; padding:24px; border-radius:6px; box-shadow:0 2px 10px rgba(0,0,0,0.3);">
        <h3 style="margin-top:0;"><?php echo _T("Create new icon", "mobile"); ?></h3>
        <div style="margin-bottom:14px;">
            <label style="font-weight:bold;"><?php echo _T("Icon name", "mobile"); ?></label><br/>
            <input type="text" id="newicon_name" style="width:100%; padding:5px; box-sizing:border-box; margin-top:4px;" />
        </div>
        <div style="margin-bottom:14px;">
            <label style="font-weight:bold;"><?php echo _T("Select file", "mobile"); ?></label><br/>
            <select id="newicon_file_id" style="width:100%; padding:5px; box-sizing:border-box; margin-top:4px;">
                <option value=""><?php echo _T("Choose a file", "mobile"); ?></option>
                <?php foreach ($_app_files as $f): ?>
                <option value="<?php echo (int)$f['id']; ?>"><?php echo htmlspecialchars($f['filePath'] ?? $f['name'] ?? ''); ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div style="text-align:right;">
            <button type="button" class="btnSecondary" style="margin-right:8px;" onclick="closeNewIconModal()"><?php echo _T("Cancel", "mobile"); ?></button>
            <button type="button" class="btnPrimary" onclick="saveNewIcon()"><?php echo _T("Save", "mobile"); ?></button>
        </div>
    </div>
</div>

<script type="text/javascript">
function openAddAppModal() {
    jQuery('#modal_app_name_app, #modal_app_name_web, #modal_app_name_intent').val('');
    jQuery('#modal_app_pkg, #modal_app_version, #modal_app_url_app, #modal_app_url_web, #modal_app_action').val('');
    jQuery('#modal_app_icon_text_app, #modal_app_icon_text_web, #modal_app_icon_text_intent').val('');
    jQuery('#modal_app_versioncode, #modal_app_filepath').val('');
    jQuery('#modal_app_arch').val('');
    jQuery('#modal_app_apk_status').text('');
    jQuery('#modal_app_apk_file').val('');
    jQuery('#modal_app_system, #modal_app_showicon, #modal_app_runafter, #modal_app_runatboot').prop('checked', false);
    jQuery('#modal_app_kiosk, #modal_web_showicon, #modal_intent_showicon').prop('checked', false);
    jQuery('#addAppError').hide().text('');
    appTabSwitch('app');
    appLoadIcons('#modal_icon_select_app');
    appLoadIcons('#modal_icon_select_web');
    appLoadIcons('#modal_icon_select_intent');
    jQuery('#addAppModal').fadeIn(150);
}
function closeAddAppModal() {
    jQuery('#addAppModal').fadeOut(150);
}
jQuery('#addAppModal').on('click', function(e) {
    if (e.target.id === 'addAppModal') closeAddAppModal();
});
function appTabSwitch(type) {
    jQuery('#modal_app_type').val(type);
    jQuery('#app_fields, #web_fields, #intent_fields').hide();
    jQuery('#' + type + '_fields').show();
    jQuery('#tab_app, #tab_web, #tab_intent').removeClass('btnPrimary').addClass('btnSecondary');
    jQuery('#tab_' + type).removeClass('btnSecondary').addClass('btnPrimary');
}
function appUpdateApkVisibility() {
    var isSystem = jQuery('#modal_app_system').is(':checked');
    jQuery('#app_row_url, #app_row_upload').toggle(!isSystem);
}
function appUpdateIconVisibility(tab) {
    var showIconId = tab === 'app' ? '#modal_app_showicon' : (tab === 'web' ? '#modal_web_showicon' : '#modal_intent_showicon');
    var checked = jQuery(showIconId).is(':checked');
    jQuery('.' + tab + '-icon-extra').toggle(checked);
}
function appLoadIcons(selector) {
    jQuery.ajax({
        url: 'modules/mobile/mobile/ajaxGetIcons.php',
        method: 'GET',
        dataType: 'json',
        global: false,
        success: function(resp) {
            var $sel = jQuery(selector);
            $sel.empty().append('<option value=""><?php echo _T("Choose an icon", "mobile"); ?></option>');
            if (resp && resp.success && Array.isArray(resp.data)) {
                jQuery.each(resp.data, function(i, icon) {
                    $sel.append(jQuery('<option>').val(icon.id).text(icon.name));
                });
            }
        }
    });
}
function appHandleApkUpload(input) {
    var file = input.files[0];
    if (!file) return;
    var $status = jQuery('#modal_app_apk_status');
    $status.css('color', '#666').text('<?php echo _T("Uploading...", "mobile"); ?>');
    jQuery('#modal_app_submit').prop('disabled', true);
    var formData = new FormData();
    formData.append('action', 'upload_apk');
    formData.append('apk_file', file);
    jQuery.ajax({
        url: 'modules/mobile/mobile/ajaxUploadApk.php',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        dataType: 'json',
        global: false,
        success: function(resp) {
            if (resp.status === 'success' && resp.data) {
                var fileDetails = resp.data.fileDetails || {};
                var version     = fileDetails.version     || resp.data.version     || '';
                var pkg         = fileDetails.pkg         || resp.data.pkg         || '';
                var versionCode = fileDetails.versionCode || resp.data.versionCode || '';
                var appName     = fileDetails.name        || resp.data.name        || '';
                var fileName    = resp.data.fileName      || file.name;
                var serverPath  = resp.data.serverPath    || resp.data.tmpPath     || resp.data.filePath || '';

                if (version)     jQuery('#modal_app_version').val(version);
                if (pkg)         jQuery('#modal_app_pkg').val(pkg);
                if (versionCode) jQuery('#modal_app_versioncode').val(versionCode);
                if (appName)     jQuery('#modal_app_name_app').val(appName);
                if (serverPath)  jQuery('#modal_app_filepath').val(serverPath);

                if (fileName) {
                    var fileUrl = 'http://' + window.location.hostname + '/hmdm/files/' + fileName;
                    jQuery('#modal_app_url_app').val(fileUrl);
                }

                $status.html('<span style="color:#3c763d;">&#10003; <?php echo _T("Upload successful", "mobile"); ?></span>');
            } else {
                $status.html('<span style="color:#c00;"><?php echo _T("Upload failed", "mobile"); ?>: ' + (resp.error || '') + '</span>');
            }
        },
        error: function() {
            $status.html('<span style="color:#c00;"><?php echo _T("Upload failed", "mobile"); ?></span>');
        },
        complete: function() {
            jQuery('#modal_app_submit').prop('disabled', false);
        }
    });
}
function openNewIconModal() {
    jQuery('#newicon_name').val('');
    jQuery('#newicon_file_id').val('');
    jQuery('#newIconModal').fadeIn(150);
}
function closeNewIconModal() {
    jQuery('#newIconModal').fadeOut(150);
}
function saveNewIcon() {
    var name   = jQuery('#newicon_name').val().trim();
    var fileId = jQuery('#newicon_file_id').val();
    var fileName = jQuery('#newicon_file_id option:selected').text();
    if (!name) { alert('<?php echo _T("Please enter an icon name", "mobile"); ?>'); return; }
    if (!fileId) { alert('<?php echo _T("Please select a file", "mobile"); ?>'); return; }
    jQuery.ajax({
        url: 'modules/mobile/mobile/ajaxCreateIcon.php',
        method: 'POST',
        dataType: 'json',
        global: false,
        data: { name: name, fileId: fileId, fileName: fileName },
        success: function(resp) {
            if (resp.success) {
                closeNewIconModal();
                var newId = resp.data && resp.data.id ? resp.data.id : '';
                appLoadIcons('#modal_icon_select_app');
                appLoadIcons('#modal_icon_select_web');
                appLoadIcons('#modal_icon_select_intent');
                var type = jQuery('#modal_app_type').val();
                setTimeout(function() {
                    jQuery('#modal_icon_select_' + type).val(newId);
                }, 300);
            } else {
                alert(resp.error || '<?php echo _T("Failed to create icon", "mobile"); ?>');
            }
        },
        error: function() {
            alert('<?php echo _T("An error occurred. Please try again.", "mobile"); ?>');
        }
    });
}
function submitAddApp() {
    var type = jQuery('#modal_app_type').val();
    var nameId = '#modal_app_name_' + type;
    var data = { type: type, name: jQuery(nameId).val().trim() };
    jQuery('#addAppError').hide().text('');
    if (type === 'app') {
        data.pkg     = jQuery('#modal_app_pkg').val().trim();
        data.version = jQuery('#modal_app_version').val().trim();
        data.url     = jQuery('#modal_app_url_app').val().trim();
        data.arch    = jQuery('#modal_app_arch').val();
        data.filePath    = jQuery('#modal_app_filepath').val();
        data.versioncode = jQuery('#modal_app_versioncode').val();
        if (jQuery('#modal_app_system').is(':checked'))    data.system = 1;
        if (jQuery('#modal_app_runafter').is(':checked'))  data.runAfterInstall = 1;
        if (jQuery('#modal_app_runatboot').is(':checked')) data.runAtBoot = 1;
        if (jQuery('#modal_app_showicon').is(':checked')) {
            data.showicon  = 1;
            data.icon_id   = jQuery('#modal_icon_select_app').val();
            data.icon_text = jQuery('#modal_app_icon_text_app').val().trim();
        }
    } else if (type === 'web') {
        data.url = jQuery('#modal_app_url_web').val().trim();
        if (jQuery('#modal_app_kiosk').is(':checked'))     data.useKiosk = 1;
        if (jQuery('#modal_web_showicon').is(':checked')) {
            data.showicon  = 1;
            data.icon_id   = jQuery('#modal_icon_select_web').val();
            data.icon_text = jQuery('#modal_app_icon_text_web').val().trim();
        }
    } else if (type === 'intent') {
        data.action = jQuery('#modal_app_action').val().trim();
        if (jQuery('#modal_intent_showicon').is(':checked')) {
            data.showicon  = 1;
            data.icon_id   = jQuery('#modal_icon_select_intent').val();
            data.icon_text = jQuery('#modal_app_icon_text_intent').val().trim();
        }
    }
    jQuery.ajax({
        url: 'modules/mobile/mobile/addApplicationAjax.php',
        method: 'POST',
        data: data,
        dataType: 'json',
        success: function(resp) {
            if (resp.status === 'ok') {
                closeAddAppModal();
                jQuery('#container').load('<?php echo urlStrRedirect("mobile/mobile/ajaxApplicationsList"); ?>', function() {
                    mobileFlash('success', resp.message);
                });
            } else {
                jQuery('#addAppError').text(resp.message).show();
            }
        },
        error: function() {
            jQuery('#addAppError').text('<?php echo _T("An error occurred. Please try again.", "mobile"); ?>').show();
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
