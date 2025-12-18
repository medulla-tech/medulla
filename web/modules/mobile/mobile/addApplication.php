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
    $values['icon_id'] = trim($_POST['icon_id'] ?? '');
    $values['icon_text'] = trim($_POST['icon_text'] ?? '');
    
    error_log('[mobile] Parsed values: ' . json_encode($values));

    // Validation
    error_log('[mobile] Starting validation...');
    if ($values['name'] === '') {
        $errors['name'] = _T("Application name is required.", "mobile");
        error_log('[mobile] ERROR: name is empty');
    }
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
    error_log('[mobile] Validation complete. Errors count: ' . count($errors));

        if (empty($errors)) {
            error_log('[mobile] No validation errors, proceeding with application creation');
            // include iconText from form if present
            if (isset($_POST['icon_text']) && trim($_POST['icon_text']) !== '') {
                $app['iconText'] = trim($_POST['icon_text']);
            }
        $app = array(
            'name' => $values['name'],
            'pkg' => $values['pkg'],
            'version' => $values['version']
        );
        error_log('[mobile] Base app array created');
        // include url only when not marked as system
        if (!$values['system'] && $values['url'] !== '') {
            $app['url'] = $values['url'];
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

$formAddApplication = new Form();
$sep = new SepTpl();

function showError($field, $errors) {
    if (isset($errors[$field])) {
        return '<div class="error-message">' . htmlspecialchars($errors[$field]) . '</div>';
    }
    return '';
}

// --- Type 
$typeSelect = new SelectItem('type');
$typeSelect->setElements([
    _T('Choose your type', 'mobile'),
    'Application',
    'Web Page',
    'System Action',
]);
$typeSelect->setElementsVal([
    '',
    'Application',
    'Web Page',
    'System Action',
]);
$typeSelect->style = 'type-field';
$formAddApplication->add(new TrFormElement(
    _T('Type', 'mobile'),
    $typeSelect
));
$formAddApplication->add(new TrFormElement('', $sep));

// --- Name
$formAddApplication->add(new TrFormElement(
    _T('Application name', 'mobile'),
    new InputTpl('name', '/^.{1,255}$/', $values['name'])
));
$formAddApplication->add(new TrFormElement('', $sep));
echo showError('name', $errors);

// --- Package
$formAddApplication->add(new TrFormElement(
    _T('Package name', 'mobile'),
    new InputTpl('pkg', '/^[a-zA-Z0-9_.]+$/', $values['pkg'])
));
$formAddApplication->add(new TrFormElement('', $sep));
echo showError('pkg', $errors);

// --- Version
$formAddApplication->add(new TrFormElement(
    _T('Version', 'mobile'),
    new InputTpl('version', '/^.{0,50}$/', $values['version'])
));
$formAddApplication->add(new TrFormElement('', $sep));

// --- System checkbox
$checkbox = new InputTpl('system', '/^.{0,1}$/', !empty($values['system']) ? '1' : '');
$checkbox->fieldType = 'checkbox';
$checkbox->setAttributCustom('id="system" class="system-checkbox"');
if (!empty($values['system'])) {
    $checkbox->setAttributCustom('checked');
}
$formAddApplication->add(new TrFormElement(
    _T('System', 'mobile'),
    $checkbox
));
$formAddApplication->add(new TrFormElement('', $sep));

// --- APK URL
$apkInput = new InputTpl('url', '/^https?:\/\//', $values['url']);
$apkInput->setAttributCustom('id="url" class="apk-field"');

$formAddApplication->add(new TrFormElement(
    _T('APK URL', 'mobile'),
    $apkInput
));
$formAddApplication->add(new TrFormElement('', $sep));
echo showError('url', $errors);

// --- Architecture (dropdown list)
$archSelect = new SelectItem('arch');
$archSelect->setElements([
    _T('Choose your architecture', 'mobile'),
    'armeabi-v7a',
    'arm64-v8a',
]);
$archSelect->setElementsVal([
    '',
    'armeabi-v7a',
    'arm64-v8a',
]);
$archSelect->style = 'arch-field';
$formAddApplication->add(new TrFormElement(
    _T('Architecture', 'mobile'),
    $archSelect
));
$formAddApplication->add(new TrFormElement('', $sep));
echo showError('arch', $errors);

// --- Show icon checkbox
$checkboxIcon = new InputTpl('showicon', '/^.{0,1}$/', !empty($values['showicon']) ? '1' : '');
$checkboxIcon->fieldType = 'checkbox';
$checkboxIcon->setAttributCustom('id="showicon" class="icon-checkbox"');
if (!empty($values['showicon'])) {
    $checkboxIcon->setAttributCustom('checked');
}
$formAddApplication->add(new TrFormElement(
    _T('Show icon', 'mobile'),
    $checkboxIcon
));

// --- Icon dropdown (initially empty; populated by AJAX)
$iconSelect = new SelectItem('icon_id');
$iconSelect->setElements([_T('Choose an icon', 'mobile')]);
$iconSelect->setElementsVal(['']);
$iconSelect->setSelected('');
// `SelectItem` doesn't implement setAttributCustom; set id and class via properties
$iconSelect->id = 'icon_select';
$iconSelect->style = 'icon-extra';
$formAddApplication->add(new TrFormElement(
    _T('Icon', 'mobile'),
    $iconSelect
));

// --- New icon button (will trigger modal)
$newIconButton = new buttonTpl('new_icon_btn', _T('New icon', 'mobile'));
$newIconButton->setClass('icon-extra btnPrimary');
$formAddApplication->add(new TrFormElement('', $newIconButton));

// --- Icon text input
$iconText = new InputTpl('icon_text', '/^.{0,255}$/', $values['icon_text'] ?? '');
$iconText->setAttributCustom('class="icon-extra"');
$formAddApplication->add(new TrFormElement(
    _T('Icon text', 'mobile'),
    $iconText
));

// Icon file upload removed (no server-side upload processing). Keep icon text input only.

// Validation button
$formAddApplication->addValidateButton("test");

// Form display
$formAddApplication->display();

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
            let isSystem = $('.system-checkbox').is(':checked');
            clog('DEBUG: isSystem=', isSystem);

            let $apk = $('.apk-field');
            if (!$apk.length) { 
                clog('DEBUG: apk-field NOT found'); 
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
        let showIcon = $('#showicon').is(':checked');
        clog('DEBUG: showIcon=', showIcon);

        $('.icon-extra').each(function () {
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
                    // Reload page to update dropdown
                    window.location.reload();
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
        setTimeout(updateApkVisibility, 100);
        setTimeout(updateIconVisibility, 100);
        $(document).on('change', '.system-checkbox', updateApkVisibility);
        $(document).on('change', '#showicon', updateIconVisibility);
        
        // Modal event handlers
        $('#new_icon_btn').on('click', openNewIconModal);
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
        function getIcons(selectedIcon) {
            selectedIcon = selectedIcon || '';
            return $.ajax({
                url: 'modules/mobile/mobile/ajaxGetIcons.php',
                method: 'GET',
                dataType: 'json'
            }).done(function(resp) {
                clog('getIcons response', resp);
                var $sel = $('#icon_select');
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

        // Immediately load icons, preserving selected value from server-side
        var selectedIcon = '<?php echo htmlspecialchars($values['icon_id'], ENT_QUOTES); ?>';
        getIcons(selectedIcon);
    });
})(jQuery);
</script>