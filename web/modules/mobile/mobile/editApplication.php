<?php
/**
 * Edit Application page
 * Loads existing application data and reuses addApplication.php form logic
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$appId = isset($_GET['id']) ? $_GET['id'] : null;

if (!$appId) {
    new NotifyWidgetFailure(_T("Application ID is required", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/applications"));
    exit;
}

// Fetch application details
$apps = xmlrpc_get_hmdm_applications();
$app = null;

if (is_array($apps)) {
    foreach ($apps as $a) {
        if (isset($a['id']) && $a['id'] == $appId) {
            $app = $a;
            break;
        }
    }
}

if (!$app) {
    new NotifyWidgetFailure(_T("Application not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/applications"));
    exit;
}

// Fetch files for the "New icon" modal dropdown. Icons themselves are loaded via AJAX.
$availableFiles = xmlrpc_get_hmdm_files();

$errors = [];
$values = [
    'id' => $app['id'] ?? '',
    'type' => $app['type'] ?? '',
    'name' => $app['name'] ?? '',
    'pkg' => $app['pkg'] ?? '',
    'version' => $app['version'] ?? '',
    'url' => $app['url'] ?? '',
    'filePath' => $app['filePath'] ?? '',
    'system' => isset($app['system']) ? $app['system'] : false,
    'arch' => $app['arch'] ?? '',
    'showicon' => isset($app['showIcon']) ? $app['showIcon'] : false,
    'runAfterInstall' => isset($app['runAfterInstall']) ? $app['runAfterInstall'] : false,
    'runAtBoot' => isset($app['runAtBoot']) ? $app['runAtBoot'] : false,
    'useKiosk' => isset($app['useKiosk']) ? $app['useKiosk'] : false,
    'action' => $app['action'] ?? '',
    'icon_id' => $app['iconId'] ?? '',
    'icon_text' => $app['iconText'] ?? '',
    'usedVersionId' => $app['usedVersionId'] ?? ''
];

// POST handler (update)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    $values['type'] = trim($_POST['type'] ?? '');
    $values['name'] = trim($_POST['name'] ?? '');
    $values['pkg'] = trim($_POST['pkg'] ?? '');
    $values['version'] = trim($_POST['version'] ?? '');
    $values['url'] = trim($_POST['url'] ?? '');
    $values['filePath'] = trim($_POST['filePath'] ?? '');
    $values['system'] = isset($_POST['system']) ? true : false;
    $values['arch'] = trim($_POST['arch'] ?? '');
    $values['showicon'] = isset($_POST['showicon']) ? true : false;
    $values['runAfterInstall'] = isset($_POST['runAfterInstall']) ? true : false;
    $values['runAtBoot'] = isset($_POST['runAtBoot']) ? true : false;
    $values['useKiosk'] = isset($_POST['useKiosk']) ? true : false;
    $values['action'] = trim($_POST['action'] ?? '');
    $values['icon_id'] = trim($_POST['icon_id'] ?? '');
    $values['icon_text'] = trim($_POST['icon_text'] ?? '');
    $values['versioncode'] = trim($_POST['versioncode'] ?? '');
    $values['usedVersionId'] = trim($_POST['usedVersionId'] ?? '');

    // Validation
    if (empty($values['name'])) {
        $errors[] = _T("Application name is required", "mobile");
    }

    if (empty($errors)) {
        // Build application data without sending empty/null fields
        $appData = [
            'id' => intval($appId),
            'type' => $values['type'],
            'name' => $values['name'],
        ];

        if ($values['type'] === 'app') {
            if ($values['pkg'] !== '') $appData['pkg'] = $values['pkg'];
            if ($values['version'] !== '') $appData['version'] = $values['version'];
            if ($values['system']) $appData['system'] = true;
            if ($values['arch'] !== '') $appData['arch'] = $values['arch'];
            if (!$values['system'] && $values['url'] !== '') $appData['url'] = $values['url'];
            if ($values['filePath'] !== '') $appData['filePath'] = $values['filePath'];
            if ($values['runAfterInstall']) $appData['runAfterInstall'] = true;
            if ($values['runAtBoot']) $appData['runAtBoot'] = true;
            if (!empty($values['versioncode'])) $appData['versionCode'] = intval($values['versioncode']);
            if (!empty($values['usedVersionId'])) $appData['usedVersionId'] = intval($values['usedVersionId']);
        } elseif ($values['type'] === 'web') {
            if ($values['url'] !== '') $appData['url'] = $values['url'];
            if ($values['useKiosk']) $appData['useKiosk'] = true;
        } elseif ($values['type'] === 'intent') {
            if ($values['action'] !== '') $appData['action'] = $values['action'];
        }

        if ($values['showicon']) $appData['showIcon'] = true;
        if (!empty($values['icon_id'])) $appData['iconId'] = intval($values['icon_id']);
        if ($values['icon_text'] !== '') $appData['iconText'] = $values['icon_text'];

        error_log('[editApplication] Updating application with data: ' . json_encode($appData));
        $result = xmlrpc_add_hmdm_application($appData);
        error_log('[editApplication] Result: ' . json_encode($result));

        if ($result && isset($result['status']) && $result['status'] === 'OK') {
            new NotifyWidgetSuccess(_T("Application updated successfully", "mobile"));
            header("Location: " . urlStrRedirect("mobile/mobile/applications"));
            exit;
        } else {
            $errorMsg = isset($result['message']) ? $result['message'] : _T("Unknown error", "mobile");
            new NotifyWidgetFailure(sprintf(_T("Error updating application: %s", "mobile"), $errorMsg));
        }
    } else {
        foreach ($errors as $error) {
            new NotifyWidgetFailure($error);
        }
    }
}

// Display title
$p = new PageGenerator(sprintf(_T("Edit Application : %s", "mobile"), $values['name']));
$p->setSideMenu($sidemenu);
$p->display();

// Include the same form rendering code as addApplication.php
// We'll create the forms and JavaScript the same way
?>

<style>
.form-container { display: none; }
.form-container.active { display: block; }
#newIconModal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}
#newIconModal .modal-content {
    background-color: #fff;
    margin: 10% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 400px;
    border-radius: 5px;
}
.icon-extra { }
</style>

<?php

// Build the forms (same as addApplication.php)
require_once("modules/imaging/includes/class_form.php");

$formApp = new ValidatingForm(['id' => 'formApp', 'class' => 'form-container']);
$formWeb = new ValidatingForm(['id' => 'formWeb', 'class' => 'form-container']);
$formIntent = new ValidatingForm(['id' => 'formIntent', 'class' => 'form-container']);

$sep = new SpanElement('<hr/>');

// Hidden field for app ID
$appIdHidden = new InputTpl('id', '/^.{0,255}$/', $values['id']);
$appIdHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $appIdHidden));
$formWeb->add(new TrFormElement('', $appIdHidden));
$formIntent->add(new TrFormElement('', $appIdHidden));

// --- App form ---
$appTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'app');
$appTypeHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $appTypeHidden));
$formApp->add(new TrFormElement('', $sep));

// Hidden field for versionCode
$versionCodeHidden = new InputTpl('versioncode', '/^[0-9]*$/', $values['versioncode'] ?? '');
$versionCodeHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $versionCodeHidden));

// Hidden field for usedVersionId (current HMDM version tracking)
$usedVersionHidden = new InputTpl('usedVersionId', '/^.{0,255}$/', $values['usedVersionId'] ?? '');
$usedVersionHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $usedVersionHidden));

// Hidden field for filePath (tmp path from upload)
$filePathHidden = new InputTpl('filePath', '/^.{0,255}$/', $values['filePath'] ?? '');
$filePathHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $filePathHidden));

$formApp->add(new TrFormElement(_T('Application name', 'mobile'), new InputTpl('name', '/^.{1,255}$/', $values['name'])));
$formApp->add(new TrFormElement('', $sep));
$formApp->add(new TrFormElement(_T('Package ID', 'mobile'), new InputTpl('pkg', '/^.{0,255}$/', $values['pkg'])));
$formApp->add(new TrFormElement('', $sep));
$versionHidden = new InputTpl('version', '/^.{0,255}$/', $values['version']);
$versionHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $versionHidden));
$versionDisplay = new SpanElement('<div style="padding: 5px 0; color: #555;">' . htmlspecialchars($values['version']) . '</div>');
$formApp->add(new TrFormElement(_T('Version', 'mobile'), $versionDisplay));
$formApp->add(new TrFormElement('', $sep));

// System checkbox
$checkboxSystem = new InputTpl('system', '/^.{0,1}$/', $values['system'] ? '1' : '');
$checkboxSystem->fieldType = 'checkbox';
$checkboxSystem->setAttributCustom('class="system-checkbox"');
if ($values['system']) $checkboxSystem->setAttributCustom('checked class="system-checkbox"');
$formApp->add(new TrFormElement(_T('System application', 'mobile'), $checkboxSystem));
$formApp->add(new TrFormElement('', $sep));

// Run options
$checkboxRunAfterInstall = new InputTpl('runAfterInstall', '/^.{0,1}$/', $values['runAfterInstall'] ? '1' : '');
$checkboxRunAfterInstall->fieldType = 'checkbox';
if ($values['runAfterInstall']) $checkboxRunAfterInstall->setAttributCustom('checked');
$formApp->add(new TrFormElement(_T('Run after install', 'mobile'), $checkboxRunAfterInstall));
$formApp->add(new TrFormElement('', $sep));

$checkboxRunAtBoot = new InputTpl('runAtBoot', '/^.{0,1}$/', $values['runAtBoot'] ? '1' : '');
$checkboxRunAtBoot->fieldType = 'checkbox';
if ($values['runAtBoot']) $checkboxRunAtBoot->setAttributCustom('checked');
$formApp->add(new TrFormElement(_T('Run at boot', 'mobile'), $checkboxRunAtBoot));
$formApp->add(new TrFormElement('', $sep));

// URL
$urlInput = new InputTpl('url', '/^.+$/', $values['url']);
$urlInput->setAttributCustom('class="url-field"');
$formApp->add(new TrFormElement(_T('URL', 'mobile'), $urlInput));
$formApp->add(new TrFormElement('', $sep));

// APK File (read-only display)
$apkFileName = '';
if (!empty($values['url'])) {
    $urlParts = parse_url($values['url']);
    if (isset($urlParts['path'])) {
        $apkFileName = basename($urlParts['path']);
    }
}
if (empty($apkFileName)) {
    $apkFileName = _T('No file', 'mobile');
}
$apkFileDisplay = new SpanElement('<div style="padding: 5px 0; color: #555;">' . htmlspecialchars($apkFileName) . '</div>');
$formApp->add(new TrFormElement(_T('APK file', 'mobile'), $apkFileDisplay));
$formApp->add(new TrFormElement('', $sep));

// Architecture (read-only display)
$archHidden = new InputTpl('arch', '/^.{0,255}$/', $values['arch']);
$archHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $archHidden));

$archLabel = $values['arch'] !== '' ? $values['arch'] : _T('None (Universal APK)', 'mobile');
$archDisplay = new SpanElement('<div style="padding: 5px 0; color: #555;">' . htmlspecialchars($archLabel) . '</div>');
$formApp->add(new TrFormElement(_T('Architecture', 'mobile'), $archDisplay));
$formApp->add(new TrFormElement('', $sep));

// Icons
$checkboxIconA = new InputTpl('showicon', '/^.{0,1}$/', $values['showicon'] ? '1' : '');
$checkboxIconA->fieldType = 'checkbox';
if ($values['showicon']) $checkboxIconA->setAttributCustom('checked');
$formApp->add(new TrFormElement(_T('Show icon', 'mobile'), $checkboxIconA));

$iconSelectA = new SelectItem('icon_id');
$iconSelectA->setElements([_T('Choose an icon', 'mobile')]);
$iconSelectA->setElementsVal(['']);
$iconSelectA->setSelected($values['icon_id']);
$iconSelectA->id = 'icon_select_app';
$iconSelectA->style = 'icon-extra';
$formApp->add(new TrFormElement(_T('Icon', 'mobile'), $iconSelectA));

$newIconBtnA = new buttonTpl('new_icon_btn_app', _T('New icon', 'mobile'));
$newIconBtnA->setClass('icon-extra btnPrimary new-icon-btn');
$formApp->add(new TrFormElement('', $newIconBtnA));

$iconTextA = new InputTpl('icon_text', '/^.{0,255}$/', $values['icon_text'] ?? '');
$iconTextA->setAttributCustom('class="icon-extra"');
$formApp->add(new TrFormElement(_T('Icon text', 'mobile'), $iconTextA));

$formApp->addValidateButton("test");

// --- Web form ---
$webTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'web');
$webTypeHidden->fieldType = 'hidden';
$formWeb->add(new TrFormElement('', $webTypeHidden));

$formWeb->add(new TrFormElement(_T('Application name', 'mobile'), new InputTpl('name', '/^.{1,255}$/', $values['name'])));
$formWeb->add(new TrFormElement('', $sep));
$formWeb->add(new TrFormElement(_T('URL', 'mobile'), new InputTpl('url', '/^.+$/', $values['url'])));
$formWeb->add(new TrFormElement('', $sep));

$useKiosk = new InputTpl('useKiosk', '/^.{0,1}$/', $values['useKiosk'] ? '1' : '');
$useKiosk->fieldType = 'checkbox';
if ($values['useKiosk']) $useKiosk->setAttributCustom('checked');
$formWeb->add(new TrFormElement(_T('Open in Kiosk-Browser', 'mobile'), $useKiosk));
$formWeb->add(new TrFormElement('', $sep));

$checkboxIconW = new InputTpl('showicon', '/^.{0,1}$/', $values['showicon'] ? '1' : '');
$checkboxIconW->fieldType = 'checkbox';
if ($values['showicon']) $checkboxIconW->setAttributCustom('checked');
$formWeb->add(new TrFormElement(_T('Show icon', 'mobile'), $checkboxIconW));

$iconSelectW = new SelectItem('icon_id');
$iconSelectW->setElements([_T('Choose an icon', 'mobile')]);
$iconSelectW->setElementsVal(['']);
$iconSelectW->setSelected($values['icon_id']);
$iconSelectW->id = 'icon_select_web';
$iconSelectW->style = 'icon-extra';
$formWeb->add(new TrFormElement(_T('Icon', 'mobile'), $iconSelectW));

$newIconBtnW = new buttonTpl('new_icon_btn_web', _T('New icon', 'mobile'));
$newIconBtnW->setClass('icon-extra btnPrimary new-icon-btn');
$formWeb->add(new TrFormElement('', $newIconBtnW));

$iconTextW = new InputTpl('icon_text', '/^.{0,255}$/', $values['icon_text'] ?? '');
$iconTextW->setAttributCustom('class="icon-extra"');
$formWeb->add(new TrFormElement(_T('Icon text', 'mobile'), $iconTextW));

$formWeb->addValidateButton("test");

// --- Intent form ---
$intentTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'intent');
$intentTypeHidden->fieldType = 'hidden';
$formIntent->add(new TrFormElement('', $intentTypeHidden));

$formIntent->add(new TrFormElement(_T('Application name', 'mobile'), new InputTpl('name', '/^.{1,255}$/', $values['name'])));
$formIntent->add(new TrFormElement('', $sep));
$formIntent->add(new TrFormElement(_T('Action', 'mobile'), new InputTpl('action', '/^.{1,255}$/', $values['action'])));
$formIntent->add(new TrFormElement('', $sep));

$checkboxIconI = new InputTpl('showicon', '/^.{0,1}$/', $values['showicon'] ? '1' : '');
$checkboxIconI->fieldType = 'checkbox';
if ($values['showicon']) $checkboxIconI->setAttributCustom('checked');
$formIntent->add(new TrFormElement(_T('Show icon', 'mobile'), $checkboxIconI));

$iconSelectI = new SelectItem('icon_id');
$iconSelectI->setElements([_T('Choose an icon', 'mobile')]);
$iconSelectI->setElementsVal(['']);
$iconSelectI->setSelected($values['icon_id']);
$iconSelectI->id = 'icon_select_intent';
$iconSelectI->style = 'icon-extra';
$formIntent->add(new TrFormElement(_T('Icon', 'mobile'), $iconSelectI));

$newIconBtnI = new buttonTpl('new_icon_btn_intent', _T('New icon', 'mobile'));
$newIconBtnI->setClass('icon-extra btnPrimary new-icon-btn');
$formIntent->add(new TrFormElement('', $newIconBtnI));

$iconTextI = new InputTpl('icon_text', '/^.{0,255}$/', $values['icon_text'] ?? '');
$iconTextI->setAttributCustom('class="icon-extra"');
$formIntent->add(new TrFormElement(_T('Icon text', 'mobile'), $iconTextI));

$formIntent->addValidateButton("test");

// Type selector (read-only in edit mode)
?>

<div>
    <h3><?php echo _T("Application Type", "mobile"); ?></h3>
    <input type="hidden" id="type" name="type" value="<?php echo htmlspecialchars($values['type']); ?>" />
    <p style="font-size: 12px; color: #555;">
        <?php 
        $typeLabel = '';
        switch ($values['type']) {
            case 'app': $typeLabel = _T("Android Application", "mobile"); break;
            case 'web': $typeLabel = _T("Web Link", "mobile"); break;
            case 'intent': $typeLabel = _T("System Action (Intent)", "mobile"); break;
            default: $typeLabel = $values['type'];
        }
        echo htmlspecialchars($typeLabel);
        ?>
    </p>
</div>

<?php
$formApp->display();
$formWeb->display();
$formIntent->display();
?>

<!-- New Icon Modal -->
<div id="newIconModal">
    <div class="modal-content">
        <h3><?php echo _T("Create New Icon", "mobile"); ?></h3>
        <label><?php echo _T("Icon Name", "mobile"); ?>:</label>
        <input type="text" id="modal_icon_name" style="width: 100%; margin-bottom: 10px;" />
        <label><?php echo _T("Select File", "mobile"); ?>:</label>
        <select id="modal_file_id" style="width: 100%; margin-bottom: 10px;">
            <option value=""><?php echo _T("-- Choose a file --", "mobile"); ?></option>
            <?php
            if (is_array($availableFiles)) {
                foreach ($availableFiles as $f) {
                    $fid = $f['id'] ?? '';
                    $fname = $f['filePath'] ?? 'Unknown';
                    echo '<option value="' . htmlspecialchars($fid) . '">' . htmlspecialchars($fname) . '</option>';
                }
            }
            ?>
        </select>
        <button id="modal_save" class="btnPrimary"><?php echo _T("Create", "mobile"); ?></button>
        <button id="modal_cancel" class="btn"><?php echo _T("Cancel", "mobile"); ?></button>
    </div>
</div>

<script type="text/javascript">
jQuery(function($) {
    // Reuse the same JavaScript logic from addApplication.php
    function clog() {
        if (window.console && console.log) {
            console.log.apply(console, arguments);
        }
    }

    function showFormForType(t) {
        $('.form-container').removeClass('active').hide();
        if (t === 'app') {
            $('#formApp').addClass('active').show();
        } else if (t === 'web') {
            $('#formWeb').addClass('active').show();
        } else if (t === 'intent') {
            $('#formIntent').addClass('active').show();
        }
    }

    function updateApkVisibility() {
        try {
            var isSystem = $('.system-checkbox').is(':checked');
            clog('updateApkVisibility: isSystem =', isSystem);
            $('.apk-field, .url-field').closest('tr').toggle(!isSystem);
        } catch (e) {
            clog('ERROR in updateApkVisibility:', e);
        }
    }

    function updateIconVisibility() {
        try {
            var showIcon = $('input[name="showicon"]:checked').length > 0;
            clog('updateIconVisibility: showIcon =', showIcon);
            $('.icon-extra').each(function() {
                var $field = $(this);
                var $tr = $field.closest('tr');
                if ($tr.length) {
                    showIcon ? $tr.show() : $tr.hide();
                } else {
                    showIcon ? $field.show() : $field.hide();
                }
            });
        } catch (e) {
            clog('ERROR in updateIconVisibility:', e);
        }
    }

    function getIcons(selectedIcon, selector) {
        selectedIcon = selectedIcon || '';
        selector = selector || '#icon_select';
        return $.ajax({
            url: 'modules/mobile/mobile/ajaxGetIcons.php',
            method: 'GET',
            dataType: 'json'
        }).done(function(resp) {
            clog('getIcons response', resp, selector);
            var $sel = $(selector);
            if (!$sel.length) return;
            $sel.empty();
            $sel.append($('<option>').attr('value','').text('<?php echo _T('Choose an icon', 'mobile'); ?>'));
            if (resp && resp.success && Array.isArray(resp.data)) {
                resp.data.forEach(function(it) {
                    var $opt = $('<option>').attr('value', it.id).text(it.name);
                    if (String(it.id) === String(selectedIcon)) $opt.prop('selected', true);
                    $sel.append($opt);
                });
            } else {
                clog('No icons returned or error:', resp && resp.error);
            }
            setTimeout(updateIconVisibility, 20);
        }).fail(function(xhr, status, err) {
            clog('Failed to load icons:', status, err);
        });
    }

    function refreshAllIconSelects(selected) {
        selected = selected || '<?php echo htmlspecialchars($values['icon_id'], ENT_QUOTES); ?>';
        getIcons(selected, '#icon_select_app');
        getIcons(selected, '#icon_select_web');
        getIcons(selected, '#icon_select_intent');
    }

    function openNewIconModal() {
        $('#newIconModal').fadeIn();
    }

    function closeNewIconModal() {
        $('#newIconModal').fadeOut();
        $('#modal_icon_name').val('');
        $('#modal_file_id').val('');
    }

    function saveNewIcon() {
        var iconName = $('#modal_icon_name').val().trim();
        var fileId = $('#modal_file_id').val();
        var fileName = $('#modal_file_id option:selected').text();

        if (!iconName) {
            alert('<?php echo _T("Please enter an icon name", "mobile"); ?>');
            return;
        }
        if (!fileId) {
            alert('<?php echo _T("Please select a file", "mobile"); ?>');
            return;
        }

        clog('Creating icon:', iconName, 'with file ID:', fileId, 'fileName:', fileName);

        $.ajax({
            url: 'modules/mobile/mobile/ajaxCreateIcon.php',
            method: 'POST',
            dataType: 'json',
            data: {
                name: iconName,
                fileId: fileId,
                fileName: fileName
            },
            success: function(response) {
                clog('Icon created:', response);
                if (response.success) {
                    alert('<?php echo _T("Icon created successfully", "mobile"); ?>');
                    closeNewIconModal();
                    var newId = (response.data && response.data.id) ? response.data.id : '';
                    if (typeof refreshAllIconSelects === 'function') refreshAllIconSelects(newId);
                } else {
                    alert('<?php echo _T("Error creating icon", "mobile"); ?>: ' + (response.error || '<?php echo _T("Unknown error", "mobile"); ?>'));
                }
            },
            error: function(xhr, status, error) {
                clog('AJAX error:', status, error);
                alert('<?php echo _T("Error creating icon", "mobile"); ?>: ' + error);
            }
        });
    }

    function validateApkFile(file) {
        if (!file) return false;
        var ext = file.name.split('.').pop().toLowerCase();
        return (ext === 'apk' || ext === 'xapk');
    }

    function handleApkFileSelect(e) {
        clog('DEBUG: handleApkFileSelect triggered');
        var file = e.target.files && e.target.files[0];
        if (!file) {
            clog('No file selected');
            return;
        }
        clog('File selected:', file.name);
        if (!validateApkFile(file)) {
            alert('<?php echo _T("Please select a valid APK or XAPK file", "mobile"); ?>');
            e.target.value = '';
            return;
        }
        uploadApkFileAjax(file);
    }

    function uploadApkFileAjax(file) {
        $('#apk_upload_status').html('<span style="color:orange;">⏳ Uploading ' + file.name + '...</span>');
        clog('Starting Ajax upload of:', file.name);

        var formData = new FormData();
        formData.append('action', 'upload_apk');
        formData.append('apk_file', file);

        $.ajax({
            url: 'modules/mobile/mobile/ajaxUploadApk.php',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                clog('Upload response:', response);
                if (response.status === 'success' && response.data) {
                    var fileDetails = response.data.fileDetails || {};
                    var version = fileDetails.version || '';
                    var pkg = fileDetails.pkg || '';
                    var versionCode = fileDetails.versionCode || '';
                    var appName = fileDetails.name || '';
                    var fileName = response.data.fileName || file.name;
                    var serverPath = response.data.serverPath || response.data.tmpPath || '';

                    // Build HMDM file URL using current domain but force HTTP
                    var hostname = window.location.hostname || '';
                    var fileUrl = hostname ? 'http://' + hostname + ':8080/hmdm/files/' + fileName : '';

                    // Fill form fields
                    $('input[name="version"]').val(version);
                    $('input[name="pkg"]').val(pkg);
                    $('input[name="versioncode"]').val(versionCode);
                    $('input[name="name"]').val(appName);
                    if (fileUrl) {
                        $('input[name="url"]').val(fileUrl);
                        clog('File URL set to:', fileUrl);
                    }
                    if (serverPath) {
                        $('input[name="filePath"]').val(serverPath);
                        clog('filePath set to:', serverPath);
                    }

                    $('#apk_upload_status').html('<span style="color:green;">✓ Upload successful</span>');
                } else {
                    $('#apk_upload_status').html('<span style="color:red;">Upload failed: ' + (response.error || 'Unknown error') + '</span>');
                }
            },
            error: function(xhr, status, err) {
                clog('Upload error:', status, err);
                $('#apk_upload_status').html('<span style="color:red;">Error uploading file: ' + err + '</span>');
            }
        });
    }

    function attachEventHandlers() {
        clog('DEBUG: Attaching event handlers');

        $(document).on('change', '#type', function(){
            var t = $(this).val();
            showFormForType(t);
            updateApkVisibility();
            updateIconVisibility();
            refreshAllIconSelects();
        });

        $(document).on('change', '.system-checkbox', updateApkVisibility);
        $(document).on('change', 'input[name="showicon"]', updateIconVisibility);

        $(document).on('click', '.new-icon-btn', openNewIconModal);
        $('#modal_cancel').on('click', closeNewIconModal);
        $('#modal_save').on('click', saveNewIcon);

        $('#newIconModal').on('click', function(e) {
            if (e.target.id === 'newIconModal') {
                closeNewIconModal();
            }
        });

        $(document).on('change', 'input[name="apk_file"]', handleApkFileSelect);
        clog('DEBUG: Bound delegated change handler to input[name=apk_file]');
    }

    function initializePage() {
        clog('DEBUG: Initializing page');
        var currentType = $('#type').val() || '<?php echo $values['type']; ?>';
        clog('Current type:', currentType);
        
        showFormForType(currentType);
        updateApkVisibility();
        updateIconVisibility();
        refreshAllIconSelects();
        attachEventHandlers();

        clog('DEBUG: Page initialized');
    }

    initializePage();
});
</script>