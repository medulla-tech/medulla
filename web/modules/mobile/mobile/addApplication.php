<?php
// Temporary debug: enable error display and log page load
// error_reporting(E_ALL);
// ini_set('display_errors', '1');
// error_log('[mobile] addApplication.php loaded');
// echo "<!-- DEBUG: addApplication.php loaded -->\n";

// AJAX icon creation is handled by modules/mobile/mobile/ajaxCreateIcon.php

require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Fetch files for the "New icon" modal dropdown. Icons themselves are loaded via AJAX.
$availableFiles = xmlrpc_get_hmdm_files();

$errors = [];
$values = [
    'type' => '',
    'name' => '',
    'pkg' => '',
    'version' => '',
    'url' => '',
    'system' => false,
    'arch' => '',
    'filePath' => '',
    'showicon' => false,
    'runAfterInstall' => false,
    'runAtBoot' => false,
    'action' => '',
    'icon_id' => '',
    'icon_text' => ''
];

// POST handler
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['bconfirm'])) {
    $values['type'] = trim($_POST['type'] ?? '');
    $values['name'] = trim($_POST['name'] ?? '');
    $values['pkg'] = trim($_POST['pkg'] ?? '');
    $values['version'] = trim($_POST['version'] ?? '');
    $values['url'] = trim($_POST['url'] ?? '');
    $values['system'] = isset($_POST['system']) ? true : false;
    $values['arch'] = trim($_POST['arch'] ?? '');
    $values['filePath'] = trim($_POST['filePath'] ?? '');
    // checkbox to indicate that an icon should be shown
    $values['showicon'] = isset($_POST['showicon']) ? true : false;
    // run options
    $values['runAfterInstall'] = isset($_POST['runAfterInstall']) ? true : false;
    $values['runAtBoot'] = isset($_POST['runAtBoot']) ? true : false;
    // intent action (for type 'intent')
    $values['action'] = trim($_POST['action'] ?? '');
    // web-specific option: open in kiosk browser
    $values['useKiosk'] = isset($_POST['useKiosk']) ? true : false;
    $values['icon_id'] = trim($_POST['icon_id'] ?? '');
    $values['icon_text'] = trim($_POST['icon_text'] ?? '');
    
    error_log('[mobile] Parsed values: ' . json_encode($values));

    // Validation
    error_log('[mobile] Starting validation...');
    if ($values['name'] === '') {
        $errors['name'] = _T("Application name is required.", "mobile");
        error_log('[mobile] ERROR: name is empty');
    }
    if ($values['type'] === '') {
        $errors['type'] = _T("Application type is required.", "mobile");
        error_log('[mobile] ERROR: type is empty');
    }

    // Type-specific validation
    if ($values['type'] === 'app') {
        if ($values['pkg'] === '') {
            $errors['pkg'] = _T("Package name is required (ex: com.example.app).", "mobile");
            error_log('[mobile] ERROR: pkg is empty');
        } elseif (!preg_match('/^[a-zA-Z0-9_.]+$/', $values['pkg'])) {
            $errors['pkg'] = _T("Package name contains invalid characters.", "mobile");
            error_log('[mobile] ERROR: pkg invalid format: ' . $values['pkg']);
        }
        // Accept full URLs or relative paths (starting with /)
        if ($values['url'] !== '' && !filter_var($values['url'], FILTER_VALIDATE_URL) && !preg_match('#^/#', $values['url'])) {
            $errors['url'] = _T("APK URL is not valid.", "mobile");
            error_log('[mobile] ERROR: invalid URL: ' . $values['url']);
        }
    } elseif ($values['type'] === 'web') {
        // web requires an URL
        if ($values['url'] === '') {
            $errors['url'] = _T("URL is required for web applications.", "mobile");
            error_log('[mobile] ERROR: url is empty for web type');
        } elseif (!filter_var($values['url'], FILTER_VALIDATE_URL) && !preg_match('#^/#', $values['url'])) {
            $errors['url'] = _T("URL is not valid.", "mobile");
            error_log('[mobile] ERROR: invalid URL: ' . $values['url']);
        }
    } elseif ($values['type'] === 'intent') {
        if (trim($values['action']) === '') {
            $errors['action'] = _T("Action is required for intent applications.", "mobile");
            error_log('[mobile] ERROR: intent action is empty');
        }
    }

    error_log('[mobile] Validation complete. Errors count: ' . count($errors));

    if (empty($errors)) {
        error_log('[mobile] No validation errors, proceeding with application creation');

        // Base payload: always include name and type
        $app = array('name' => $values['name']);
        if (!empty($values['type'])) {
            $app['type'] = $values['type'];
            error_log('[mobile] type set in payload: ' . $values['type']);
        }

        // Type-specific fields
        if ($values['type'] === 'app') {
            // Required/app-specific
            $app['pkg'] = $values['pkg'];
            if ($values['version'] !== '') {
                $app['version'] = $values['version'];
            }
            if ($values['system']) {
                $app['system'] = true;
            }
            if ($values['arch'] !== '') {
                $app['arch'] = $values['arch'];
            }
            // URL only for non-system apps
            if (!$values['system'] && $values['url'] !== '') {
                $app['url'] = $values['url'];
            }
            if (!empty($values['filePath'])) {
                $app['filePath'] = $values['filePath'];
            }
            // Run options
            if (!empty($values['runAfterInstall'])) {
                $app['runAfterInstall'] = true;
            }
            if (!empty($values['runAtBoot'])) {
                $app['runAtBoot'] = true;
            }
            // VersionCode from APK upload
            if (!empty($_POST['versioncode'])) {
                $app['versionCode'] = $_POST['versioncode'];
                error_log('[mobile] versionCode set from Ajax upload: ' . $_POST['versioncode']);
            }
        } elseif ($values['type'] === 'web') {
            // Web-specific
            if ($values['url'] !== '') {
                $app['url'] = $values['url'];
            }
            if (!empty($values['useKiosk'])) {
                $app['useKiosk'] = true;
                error_log('[mobile] useKiosk set in payload');
            }
        } elseif ($values['type'] === 'intent') {
            // Intent/System Action
            if (trim($values['action']) !== '') {
                $app['action'] = $values['action'];
                error_log('[mobile] intent action set in payload');
            }
        }

        // Common optional icon fields
        if (!empty($values['showicon'])) {
            $app['showIcon'] = true;
            error_log('[mobile] showIcon set in payload');
        }
        if (!empty($values['icon_id'])) {
            $app['iconId'] = $values['icon_id'];
            error_log('[mobile] iconId set in payload: ' . $values['icon_id']);
        }
        if (isset($_POST['icon_text']) && trim($_POST['icon_text']) !== '') {
            $app['iconText'] = trim($_POST['icon_text']);
        }

        // Create application
        error_log('[mobile] Creating application via addHmdmApplication');
        $resp = xmlrpc_add_hmdm_application($app);

        if ($resp === false || $resp === null) {
            $errors['global'] = _T("Error while adding the application.", "mobile");
            error_log('[mobile] ERROR: Application creation failed');
            error_log('[mobile] === POST HANDLER FAILED ===');
        } else {
            error_log('[mobile] SUCCESS: Application created');
            error_log('[mobile] === POST HANDLER SUCCESS ===');
            header("Location: /mmc/main.php?module=mobile&submod=mobile&action=applications");
            exit;
        }
    }
}
$p = new PageGenerator(_T("Add an application", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

// Build three separate forms: app, web, intent (app uses multipart for file upload)
$formApp = new ValidatingForm(array("method" => "post", "enctype" => "multipart/form-data", "id" => "FormApp"));
$formWeb = new ValidatingForm(array("method" => "post", "id" => "FormWeb"));
$formIntent = new ValidatingForm(array("method" => "post", "id" => "FormIntent"));

function showError($field, $errors) {
    if (isset($errors[$field])) {
        return '<div class="error-message">' . htmlspecialchars($errors[$field]) . '</div>';
    }
    return '';
}

// --- App form ---
$formApp->push(new Table());

// hidden type field
$appTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'app');
$appTypeHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $appTypeHidden));
// Name
$formApp->add(new TrFormElement(
    _T('Application name', 'mobile'),
    new InputTpl('name', '/^.{1,255}$/', $values['name'])
));
// Package
$pkgInputA = new InputTpl('pkg', '/^[a-zA-Z0-9_.]+$/', $values['pkg']);
$formApp->add(new TrFormElement(
    _T('Package name', 'mobile'),
    $pkgInputA
));
// Version
$formApp->add(new TrFormElement(
    _T('Version', 'mobile'),
    new InputTpl('version', '/^.{0,50}$/', $values['version'])
));
// Version Code (hidden, filled by Ajax)
$versionCodeHidden = new InputTpl('versioncode', '/^.{0,50}$/', '');
$versionCodeHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $versionCodeHidden));

// FilePath (hidden, filled by Ajax upload response)
$filePathHidden = new InputTpl('filePath', '/^.{0,255}$/', '');
$filePathHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $filePathHidden));
// Run options
$runAfterA = new InputTpl('runAfterInstall', '/^.{0,1}$/', !empty($values['runAfterInstall']) ? '1' : '');
$runAfterA->fieldType = 'checkbox';
$formApp->add(new TrFormElement(_T('Run after install', 'mobile'), $runAfterA));

$runBootA = new InputTpl('runAtBoot', '/^.{0,1}$/', !empty($values['runAtBoot']) ? '1' : '');
$runBootA->fieldType = 'checkbox';
$formApp->add(new TrFormElement(_T('Run at boot', 'mobile'), $runBootA));
// System
$checkboxA = new InputTpl('system', '/^.{0,1}$/', !empty($values['system']) ? '1' : '');
$checkboxA->fieldType = 'checkbox';
$checkboxA->setAttributCustom('class="system-checkbox"');
$formApp->add(new TrFormElement(_T('System', 'mobile'), $checkboxA));
// APK URL
$formApp->add(new TrFormElement(_T('APK URL', 'mobile'), new InputTpl('url', '/^https?:\/\//', $values['url'])));
// APK File Upload for app type
$apkFileInput = new InputTpl('apk_file', '/^.+$/', '');
$apkFileInput->fieldType = 'file';
$apkFileInput->setAttributCustom('accept=".apk,.xapk" id="apk_file_input" class="apk-field"');
$formApp->add(new TrFormElement(_T('Upload APK file', 'mobile'), $apkFileInput));
// Status div for APK upload
$formApp->add(new TrFormElement('', new SpanElement('<div id="apk_upload_status" style="margin-top: 5px;"></div>')));
// Architecture
$archSelectA = new SelectItem('arch');
$archSelectA->setElements([
    _T('None (Universal APK)', 'mobile'),
    'armeabi-v7a',
    'arm64-v8a',
]);
$archSelectA->setElementsVal(['', 'armeabi-v7a', 'arm64-v8a']);
$formApp->add(new TrFormElement(_T('Architecture', 'mobile'), $archSelectA));
// Icons
$checkboxIconA = new InputTpl('showicon', '/^.{0,1}$/', !empty($values['showicon']) ? '1' : '');
$checkboxIconA->fieldType = 'checkbox';
$formApp->add(new TrFormElement(_T('Show icon', 'mobile'), $checkboxIconA));
$iconSelectA = new SelectItem('icon_id');
$iconSelectA->setElements([_T('Choose an icon', 'mobile')]);
$iconSelectA->setElementsVal(['']);
$iconSelectA->id = 'icon_select_app';
$iconSelectA->style = 'icon-extra';
$formApp->add(new TrFormElement(_T('Icon', 'mobile'), $iconSelectA));
$newIconBtnA = new buttonTpl('new_icon_btn_app', _T('New icon', 'mobile')); 
$newIconBtnA->setClass('icon-extra btnPrimary new-icon-btn'); 
$formApp->add(new TrFormElement('', $newIconBtnA));
$iconTextA = new InputTpl('icon_text', '/^.{0,255}$/', $values['icon_text'] ?? ''); 
$iconTextA->setAttributCustom('class="icon-extra"'); 
$formApp->add(new TrFormElement(_T('Icon text', 'mobile'), $iconTextA));

$formApp->pop();
$formApp->addButton("bconfirm", _T("Add Application", "mobile"));

// --- Web form ---
$formWeb->push(new Table());

$webTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'web');
$webTypeHidden->fieldType = 'hidden';
$formWeb->add(new TrFormElement('', $webTypeHidden));

$formWeb->add(new TrFormElement(_T('Application name', 'mobile'), new InputTpl('name', '/^.{1,255}$/', $values['name'])));

$formWeb->add(new TrFormElement(_T('URL', 'mobile'), new InputTpl('url', '/^https?:\/\//', $values['url'])));

// Open in Kiosk-Browser checkbox (web only)
$useKiosk = new InputTpl('useKiosk', '/^.{0,1}$/', !empty($values['useKiosk']) ? '1' : '');
$useKiosk->fieldType = 'checkbox';
if (!empty($values['useKiosk'])) $useKiosk->setAttributCustom('checked');
$formWeb->add(new TrFormElement(
    _T('Open in Kiosk-Browser', 'mobile'),
    $useKiosk
));

$checkboxIconW = new InputTpl('showicon', '/^.{0,1}$/', !empty($values['showicon']) ? '1' : '');
$checkboxIconW->fieldType = 'checkbox';
$formWeb->add(new TrFormElement(_T('Show icon', 'mobile'), $checkboxIconW));
$iconSelectW = new SelectItem('icon_id');
$iconSelectW->setElements([_T('Choose an icon', 'mobile')]);
$iconSelectW->setElementsVal(['']);
$iconSelectW->id = 'icon_select_web';
$iconSelectW->style = 'icon-extra';
$formWeb->add(new TrFormElement(_T('Icon', 'mobile'), $iconSelectW));
$newIconBtnW = new buttonTpl('new_icon_btn_web', _T('New icon', 'mobile'));
$newIconBtnW->setClass('icon-extra btnPrimary new-icon-btn');
$newIconBtnW->infobulle = _T('Créer une nouvelle icône','mobile');
$formWeb->add(new TrFormElement('', $newIconBtnW));

$iconTextW = new InputTpl('icon_text', '/^.{0,255}$/', $values['icon_text'] ?? '');
$iconTextW->setAttributCustom('class="icon-extra"');
$formWeb->add(new TrFormElement(_T('Icon text', 'mobile'), $iconTextW));

$formWeb->pop();
$formWeb->addButton("bconfirm", _T("Add Application", "mobile"));

// --- Intent form ---
$formIntent->push(new Table());

$intentTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'intent');
$intentTypeHidden->fieldType = 'hidden';
$formIntent->add(new TrFormElement('', $intentTypeHidden));
$formIntent->add(new TrFormElement(_T('Application name', 'mobile'), new InputTpl('name', '/^.{1,255}$/', $values['name'])));

$formIntent->add(new TrFormElement(_T('Action', 'mobile'), new InputTpl('action', '/^.{1,255}$/', $values['action'])));

$checkboxIconI = new InputTpl('showicon', '/^.{0,1}$/', !empty($values['showicon']) ? '1' : '');
$checkboxIconI->fieldType = 'checkbox';
$formIntent->add(new TrFormElement(_T('Show icon', 'mobile'), $checkboxIconI));

$iconSelectI = new SelectItem('icon_id');
$iconSelectI->setElements([_T('Choose an icon', 'mobile')]);
$iconSelectI->setElementsVal(['']);
$iconSelectI->id = 'icon_select_intent';
$iconSelectI->style = 'icon-extra';
$formIntent->add(new TrFormElement(_T('Icon', 'mobile'), $iconSelectI));

$newIconBtnI = new buttonTpl('new_icon_btn_intent', _T('New icon', 'mobile'));
$newIconBtnI->setClass('icon-extra btnPrimary new-icon-btn');
$formIntent->add(new TrFormElement('', $newIconBtnI));

$iconTextI = new InputTpl('icon_text', '/^.{0,255}$/', $values['icon_text'] ?? '');
$iconTextI->setAttributCustom('class="icon-extra"');
$formIntent->add(new TrFormElement(_T('Icon text', 'mobile'), $iconTextI));

$formIntent->pop();
$formIntent->addButton("bconfirm", _T("Add Application", "mobile"));

// Type selector form
$typeForm = new ValidatingForm();
$typeForm->push(new Table());
$typeSelect = new SelectItem('type_selector');
$typeSelect->setElements([
    _T('Choose your type', 'mobile'),
    'Application',
    'Web Page',
    'System Action'
]);
$typeSelect->setElementsVal(['', 'app', 'web', 'intent']);
$typeSelect->id = 'type';
$typeForm->add(new TrFormElement(_T('Type', 'mobile'), $typeSelect));
$typeForm->pop();

echo '<div id="forms_container">';
echo '<div style="margin-bottom:20px;">';
$typeForm->display();
echo showError('type', $errors);
echo '</div>';

echo '<div class="app-form">';
$formApp->display();
echo '</div>';

echo '<div class="web-form" style="display:none;">';
$formWeb->display();
echo '</div>';

echo '<div class="intent-form" style="display:none;">';
$formIntent->display();
echo '</div>';

echo '</div>';

if (isset($errors['global'])) {
    echo '<div class="error-message">' . htmlspecialchars($errors['global']) . '</div>';
}
?>

<!-- Modal for creating new icon -->
<div id="newIconModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999;">
    <div style="position:relative; width:500px; margin:100px auto; background:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 10px rgba(0,0,0,0.3);">
        <h3><?php echo _T("Create new icon", "mobile"); ?></h3>
        
        <div style="margin:15px 0;">
            <label for="modal_icon_name"><?php echo _T("Icon name", "mobile"); ?>:</label><br/>
            <input type="text" id="modal_icon_name" name="modal_icon_name" style="width:100%; padding:5px;" />
        </div>
        
        <div style="margin:15px 0;">
            <label for="modal_file_id"><?php echo _T("Select file", "mobile"); ?>:</label><br/>
            <select id="modal_file_id" name="modal_file_id" style="width:100%; padding:5px;">
                <option value=""><?php echo _T("Choose a file", "mobile"); ?></option>
                <?php
                if (is_array($availableFiles)) {
                    foreach ($availableFiles as $file) {
                        $displayName = $file['filePath'] ?? $file['name'] ?? _T('Unknown', 'mobile');
                        $fileId = $file['id'];
                        echo '<option value="' . htmlspecialchars($fileId) . '">' . htmlspecialchars($displayName) . '</option>';
                    }
                }
                ?>
            </select>
        </div>
        
        <div style="margin-top:20px; text-align:right;">
            <button type="button" id="modal_cancel" class="btnSecondary"><?php echo _T("Cancel", "mobile"); ?></button>
            <button type="button" id="modal_save" class="btnPrimary"><?php echo _T("Save", "mobile"); ?></button>
        </div>
    </div>
</div>

<script type="text/javascript">
(function($) {
    // ========== LOGGING ==========
    function clog() {
        if (window.console && console.log) console.log.apply(console, arguments);
    }

    clog('DEBUG: jQuery detected');

    // ========== FORM VISIBILITY ==========
    function showFormForType(type) {
        $('.app-form, .web-form, .intent-form').hide();
        if (type === 'app') $('.app-form').show();
        else if (type === 'web') $('.web-form').show();
        else if (type === 'intent') $('.intent-form').show();
    }

    function updateFieldsByType() {
        var t = $('#type').length ? $('#type').val() : $('select[name="type_selector"]').val();
        $('.type-app, .type-web, .type-intent').each(function(){
            var $el = $(this);
            var show = $el.hasClass('type-' + t);
            var $tr = $el.closest('tr');
            if ($tr.length) {
                if (show) $tr.show(); else $tr.hide();
            } else {
                if (show) $el.show(); else $el.hide();
            }
        });
        $('input[name="name"]').closest('tr').show();
    }

    // ========== FIELD VISIBILITY ==========
    function updateApkVisibility() {
        try {
            var $visible = $('#forms_container').find('div:visible');
            var isSystem = $visible.find('.system-checkbox').is(':checked');
            clog('DEBUG: isSystem=', isSystem);

            var $apk = $visible.find('.apk-field');
            if (!$apk.length) {
                // Fallback to id search if class not present
                $apk = $visible.find('#apk_file_input');
            }
            if (!$apk.length) {
                // Fallback to name selector if id not present
                $apk = $visible.find('input[name="apk_file"]');
            }
            if (!$apk.length) { 
                clog('DEBUG: apk-field NOT found in visible form'); 
                return; 
            }

            var $parent = $apk.parent();
            clog('DEBUG: Parent tagName:', $parent.prop('tagName'), 'id:', $parent.attr('id'), 'class:', $parent.attr('class'));

            if (isSystem) {
                clog('DEBUG: hiding parent');
                $parent.hide();
            } else {
                clog('DEBUG: showing parent');
                $parent.show();
            }
        } catch (e) {
            clog('ERROR in updateApkVisibility:', e);
        }
    }

    function updateIconVisibility() {
        try {
            var $visible = $('#forms_container').find('div:visible');
            var showIcon = $visible.find('input[name="showicon"]').is(':checked');
            clog('DEBUG: showIcon=', showIcon);

            $visible.find('.icon-extra').each(function () {
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

    // ========== ICON MANAGEMENT ==========
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

    // ========== APK FILE VALIDATION ==========
    function validateApkFile(file) {
        var ext = file.name.split('.').pop().toLowerCase();
        if (ext !== 'apk' && ext !== 'xapk') {
            return { valid: false, error: 'Only APK and XAPK files are allowed' };
        }
        return { valid: true };
    }

    function handleApkFileSelect() {
        var $input = $(this);
        clog('DEBUG: change event fired on #apk_file_input');
        console.log('[mobile] change on #apk_file_input');
        var file = $input[0].files[0];

        if (!file) {
            clog('DEBUG: No file found in input after change');
            $('#apk_upload_status').html('<span style="color:red;">No file selected</span>');
            return;
        }
        clog('DEBUG: File selected:', file && file.name);
        $('#apk_upload_status').html('<span style="color:#555;">File selected: ' + file.name + '</span>');

        var validation = validateApkFile(file);
        if (!validation.valid) {
            $('#apk_upload_status').html('<span style="color:red;">Error: ' + validation.error + '</span>');
            $input.val('');
            return;
        }

        // Upload immediately via Ajax
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

                    // Build HMDM file URL using current domain but force HTTP (HMDM stores HTTP URLs)
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

    // ========== EVENT HANDLERS ==========
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

        // Bind by name (robust for rendered form fields)
        $(document).on('change', 'input[name="apk_file"]', handleApkFileSelect);
        clog('DEBUG: Bound delegated change handler to input[name=apk_file]');

        // Direct binding no longer needed; server-side field is rendered by PHP classes
    }

    // ========== INITIALIZATION ==========
    function initializePage() {
        clog('DEBUG: Initializing page');
        
        var currentType = $('#type').val() || '';
        if (!currentType) {
            clog('DEBUG: No type selected, defaulting to app');
            $('#type').val('app').trigger('change');
            currentType = 'app';
        }
        showFormForType(currentType);
        
        setTimeout(updateApkVisibility, 120);
        setTimeout(updateIconVisibility, 120);
        
        attachEventHandlers();
        refreshAllIconSelects();

        // Debug presence/visibility of apk input (should exist via PHP form classes)
        var $apk = $('#apk_file_input');
        clog('DEBUG: After init, #apk_file_input exists?', $apk.length, 'visible?', $apk.is(':visible'));
        var $apkByName = $('input[name="apk_file"]');
        clog('DEBUG: After init, input[name=apk_file] exists?', $apkByName.length, 'visible?', $apkByName.is(':visible'));

        clog('DEBUG: Page initialized');
    }

    // ========== DOM READY ==========
    $(function(){
        initializePage();
    });

})(jQuery);
</script>