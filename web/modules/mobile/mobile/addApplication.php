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
    'showicon' => false,
    'runAfterInstall' => false,
    'runAtBoot' => false,
    'action' => '',
    'icon_id' => '',
    'icon_text' => ''
];

// POST handler
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    $values['type'] = trim($_POST['type'] ?? '');
    $values['name'] = trim($_POST['name'] ?? '');
    $values['pkg'] = trim($_POST['pkg'] ?? '');
    $values['version'] = trim($_POST['version'] ?? '');
    $values['url'] = trim($_POST['url'] ?? '');
    $values['system'] = isset($_POST['system']) ? true : false;
    $values['arch'] = trim($_POST['arch'] ?? '');
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
        if ($values['url'] !== '' && !filter_var($values['url'], FILTER_VALIDATE_URL)) {
            $errors['url'] = _T("APK URL is not valid.", "mobile");
            error_log('[mobile] ERROR: invalid URL: ' . $values['url']);
        }
    } elseif ($values['type'] === 'web') {
        // web requires an URL
        if ($values['url'] === '') {
            $errors['url'] = _T("URL is required for web applications.", "mobile");
            error_log('[mobile] ERROR: url is empty for web type');
        } elseif (!filter_var($values['url'], FILTER_VALIDATE_URL)) {
            $errors['url'] = _T("APK URL is not valid.", "mobile");
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
            // include iconText from form if present
            if (isset($_POST['icon_text']) && trim($_POST['icon_text']) !== '') {
                $app['iconText'] = trim($_POST['icon_text']);
            }
        $app = array(
            'name' => $values['name'],
            'version' => $values['version']
        );
        // include type if provided (HMDM expects 'app','web' or 'intent')
        if (!empty($values['type'])) {
            $app['type'] = $values['type'];
            error_log('[mobile] type set in payload: ' . $values['type']);
        }
        // include pkg for app type
        if ($values['type'] === 'app') {
            $app['pkg'] = $values['pkg'];
        }
        error_log('[mobile] Base app array created');
        // include url for web type; for app keep legacy behaviour
        if ($values['type'] === 'web' && $values['url'] !== '') {
            $app['url'] = $values['url'];
        } elseif ($values['type'] === 'app' && !$values['system'] && $values['url'] !== '') {
            $app['url'] = $values['url'];
        }
        // web-specific useKiosk flag
        if ($values['type'] === 'web' && !empty($values['useKiosk'])) {
            $app['useKiosk'] = true;
            error_log('[mobile] useKiosk set in payload');
        }
        // intent action
        if ($values['type'] === 'intent' && trim($values['action']) !== '') {
            $app['action'] = $values['action'];
            error_log('[mobile] intent action set in payload');
        }
        // include explicit system flag when checked
        if ($values['system']) {
            $app['system'] = true;
        }

        if ($values['arch'] !== '') {
            $app['arch'] = $values['arch'];
        }
        // include explicit showIcon flag when requested
        if (!empty($values['showicon'])) {
            $app['showIcon'] = true;
            error_log('[mobile] showIcon set in payload');
        }
        // include icon_id if selected
        if (!empty($values['icon_id'])) {
            $app['iconId'] = $values['icon_id'];
            error_log('[mobile] iconId set in payload: ' . $values['icon_id']);
        }
        // include run flags if requested
        if (!empty($values['runAfterInstall'])) {
            $app['runAfterInstall'] = true;
            error_log('[mobile] runAfterInstall set in payload');
        }
        if (!empty($values['runAtBoot'])) {
            $app['runAtBoot'] = true;
            error_log('[mobile] runAtBoot set in payload');
        }
        // include iconText from form if present
        if (isset($_POST['icon_text']) && trim($_POST['icon_text']) !== '') {
            $app['iconText'] = trim($_POST['icon_text']);
        }

        // Icon upload handling removed (no uploads are processed server-side).

        // Call backend and log minimal response
        $resp = xmlrpc_add_hmdm_application($app);

        if ($resp === false || $resp === null) {
            $errors['global'] = _T("Error while adding the application.", "mobile");
            error_log('[mobile] ERROR: xmlrpc_add_hmdm_application returned false/null');
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

// Build three separate forms: app, web, intent
$formApp = new Form();
$formWeb = new Form();
$formIntent = new Form();
$sep = new SepTpl();

function showError($field, $errors) {
    if (isset($errors[$field])) {
        return '<div class="error-message">' . htmlspecialchars($errors[$field]) . '</div>';
    }
    return '';
}

// --- App form ---
// hidden type field
$appTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'app');
$appTypeHidden->fieldType = 'hidden';
$formApp->add(new TrFormElement('', $appTypeHidden));
// Name
$formApp->add(new TrFormElement(
    _T('Application name', 'mobile'),
    new InputTpl('name', '/^.{1,255}$/', $values['name'])
));
$formApp->add(new TrFormElement('', $sep));
// Package
$pkgInputA = new InputTpl('pkg', '/^[a-zA-Z0-9_.]+$/', $values['pkg']);
$formApp->add(new TrFormElement(
    _T('Package name', 'mobile'),
    $pkgInputA
));
$formApp->add(new TrFormElement('', $sep));
// Version
$formApp->add(new TrFormElement(
    _T('Version', 'mobile'),
    new InputTpl('version', '/^.{0,50}$/', $values['version'])
));
$formApp->add(new TrFormElement('', $sep));
// Run options
$runAfterA = new InputTpl('runAfterInstall', '/^.{0,1}$/', !empty($values['runAfterInstall']) ? '1' : '');
$runAfterA->fieldType = 'checkbox';
$formApp->add(new TrFormElement(_T('Run after install', 'mobile'), $runAfterA));
$formApp->add(new TrFormElement('', $sep));
$runBootA = new InputTpl('runAtBoot', '/^.{0,1}$/', !empty($values['runAtBoot']) ? '1' : '');
$runBootA->fieldType = 'checkbox';
$formApp->add(new TrFormElement(_T('Run at boot', 'mobile'), $runBootA));
$formApp->add(new TrFormElement('', $sep));
// System
$checkboxA = new InputTpl('system', '/^.{0,1}$/', !empty($values['system']) ? '1' : '');
$checkboxA->fieldType = 'checkbox';
$checkboxA->setAttributCustom('class="system-checkbox"');
$formApp->add(new TrFormElement(_T('System', 'mobile'), $checkboxA));
$formApp->add(new TrFormElement('', $sep));
// APK URL
$formApp->add(new TrFormElement(_T('APK URL', 'mobile'), new InputTpl('url', '/^https?:\/\//', $values['url'])));
$formApp->add(new TrFormElement('', $sep));
// Architecture
$archSelectA = new SelectItem('arch');
$archSelectA->setElements([
    _T('Choose your architecture', 'mobile'),
    'armeabi-v7a',
    'arm64-v8a',
]);
$archSelectA->setElementsVal(['', 'armeabi-v7a', 'arm64-v8a']);
$formApp->add(new TrFormElement(_T('Architecture', 'mobile'), $archSelectA));
$formApp->add(new TrFormElement('', $sep));
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
$formApp->addValidateButton("test");

// --- Web form ---
$webTypeHidden = new InputTpl('type', '/^.{0,255}$/', 'web');
$webTypeHidden->fieldType = 'hidden';
$formWeb->add(new TrFormElement('', $webTypeHidden));

$formWeb->add(new TrFormElement(_T('Application name', 'mobile'), new InputTpl('name', '/^.{1,255}$/', $values['name'])));
$formWeb->add(new TrFormElement('', $sep));

$formWeb->add(new TrFormElement(_T('URL', 'mobile'), new InputTpl('url', '/^https?:\/\//', $values['url'])));
$formWeb->add(new TrFormElement('', $sep));

// Open in Kiosk-Browser checkbox (web only)
$useKiosk = new InputTpl('useKiosk', '/^.{0,1}$/', !empty($values['useKiosk']) ? '1' : '');
$useKiosk->fieldType = 'checkbox';
if (!empty($values['useKiosk'])) $useKiosk->setAttributCustom('checked');
$formWeb->add(new TrFormElement(
    _T('Open in Kiosk-Browser', 'mobile'),
    $useKiosk
));
$formWeb->add(new TrFormElement('', $sep));
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
$formIntent->addValidateButton("test");

// Type selector (controls which form is visible)
echo '<div style="margin-bottom:10px;">';
echo '<label for="type">' . _T('Type','mobile') . ':</label> ';
echo '<select id="type" name="type_selector" style="margin-left:8px; padding:6px;">';
$opt = htmlspecialchars($values['type'] ?? '', ENT_QUOTES);
echo '<option value=""' . ($opt === '' ? ' selected' : '') . '>' . _T('Choose your type', 'mobile') . '</option>';
echo '<option value="app"' . ($opt === 'app' ? ' selected' : '') . '>Application</option>';
echo '<option value="web"' . ($opt === 'web' ? ' selected' : '') . '>Web Page</option>';
echo '<option value="intent"' . ($opt === 'intent' ? ' selected' : '') . '>System Action</option>';
echo '</select>';
echo ' ' . showError('type', $errors);
echo '</div>';

// Display forms inside wrappers
echo '<div id="forms_container">';

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
    function clog() {
        if (window.console && console.log) console.log.apply(console, arguments);
    }

    clog('DEBUG: jQuery detected');


    // Function to update APK visibility based on System checkbox
    function updateApkVisibility() {
        try {
            var $visible = $('#forms_container').find('div:visible');
            let isSystem = $visible.find('.system-checkbox').is(':checked');
            clog('DEBUG: isSystem=', isSystem);

            let $apk = $visible.find('.apk-field');
            if (!$apk.length) { 
                clog('DEBUG: apk-field NOT found in visible form'); 
                return; 
            }

            let $parent = $apk.parent();

            clog('DEBUG: Parent tagName:', $parent.prop('tagName'), 'id:', $parent.attr('id'), 'class:', $parent.attr('class'));

            if (isSystem) {
                clog('DEBUG: hiding parent');
                $parent.hide();
            } else {
                clog('DEBUG: showing parent');
                $parent.show();
            }
        } catch (e) {
            clog('ERROR in updateApkVisibility (jQuery):', e);
        }
    }

    // Function to update Icon extra fields visibility based on Show Icon checkbox
    function updateIconVisibility() {
    try {
        var $visible = $('#forms_container').find('div:visible');
        let showIcon = $visible.find('input[name="showicon"]').is(':checked');
        clog('DEBUG: showIcon=', showIcon);

        $visible.find('.icon-extra').each(function () {
            let $field = $(this);
            let $tr = $field.closest('tr');

            if ($tr.length) {
                // Hide/show full row (label + field)
                showIcon ? $tr.show() : $tr.hide();
            } else {
                // Fallback (buttons, inputs outside TR)
                showIcon ? $field.show() : $field.hide();
            }
        });

    } catch (e) {
        clog('ERROR in updateIconVisibility:', e);
    }
}

    


    // Modal handling
    function openNewIconModal() {
        $('#newIconModal').fadeIn();
    }

    function closeNewIconModal() {
        $('#newIconModal').fadeOut();
        $('#modal_icon_name').val('');
        $('#modal_file_id').val('');
    }

    function saveNewIcon() {
        let iconName = $('#modal_icon_name').val().trim();
        let fileId = $('#modal_file_id').val();
        let fileName = $('#modal_file_id option:selected').text();

        if (!iconName) {
            alert('<?php echo _T("Please enter an icon name", "mobile"); ?>');
            return;
        }
        if (!fileId) {
            alert('<?php echo _T("Please select a file", "mobile"); ?>');
            return;
        }

        clog('Creating icon:', iconName, 'with file ID:', fileId, 'fileName:', fileName);

        // AJAX call to create icon (dedicated endpoint)
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
                    // Refresh icon selects; if server returned new id, select it
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
     

    $(function(){
        // initialize field visibility based on selected type first
        function updateFieldsByType() {
            var t = $('#type').length ? $('#type').val() : $('select[name="type"]').val();
            // show/hide elements marked with type classes
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
            // name should always be visible
            $('input[name="name"]').closest('tr').show();
        }
        // Show the correct form wrapper based on type selection
        function showFormForType(t) {
            $('.app-form, .web-form, .intent-form').hide();
            if (t === 'app') $('.app-form').show();
            else if (t === 'web') $('.web-form').show();
            else if (t === 'intent') $('.intent-form').show();
        }
        var currentType = $('#type').val() || '';
        showFormForType(currentType);
        setTimeout(updateApkVisibility, 120);
        setTimeout(updateIconVisibility, 120);
        $(document).on('change', '#type', function(){
            var t = $(this).val();
            showFormForType(t);
            updateApkVisibility();
            updateIconVisibility();
            // refresh icon selects when changing type to ensure they're populated
            refreshAllIconSelects();
        });
        $(document).on('change', '.system-checkbox', updateApkVisibility);
        $(document).on('change', '#showicon', updateIconVisibility);
        
        // Modal event handlers
        $(document).on('click', '.new-icon-btn', openNewIconModal);
        $('#modal_cancel').on('click', closeNewIconModal);
        $('#modal_save').on('click', saveNewIcon);
        
        // Close modal when clicking outside
        $('#newIconModal').on('click', function(e) {
            if (e.target.id === 'newIconModal') {
                closeNewIconModal();
            }
        });
        
        clog('DEBUG: jQuery handler attached');
        // Helper: fetch icons via AJAX and populate the select. Returns jqXHR.
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

        // Immediately load icons for all selects
        refreshAllIconSelects();
    });
})(jQuery);
</script>