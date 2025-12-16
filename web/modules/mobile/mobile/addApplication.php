<?php
// Temporary debug: enable error display and log page load
// error_reporting(E_ALL);
// ini_set('display_errors', '1');
// error_log('[mobile] addApplication.php loaded');
// echo "<!-- DEBUG: addApplication.php loaded -->\n";

// Handle AJAX icon creation request
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'create_icon') {
    require_once("modules/mobile/includes/xmlrpc.php");
    
    header('Content-Type: application/json');
    $response = ['success' => false, 'error' => ''];
    
    $name = trim($_POST['name'] ?? '');
    $fileId = trim($_POST['fileId'] ?? '');
    $fileName = trim($_POST['fileName'] ?? '');
    
    if (empty($name)) {
        $response['error'] = _T('Icon name is required', 'mobile');
        echo json_encode($response);
        exit;
    }
    
    if (empty($fileId)) {
        $response['error'] = _T('File ID is required', 'mobile');
        echo json_encode($response);
        exit;
    }
    
    $iconData = [
        'name' => $name,
        'fileId' => $fileId,
        'fileName' => $fileName
    ];
    
    try {
        $result = xmlrpc_add_hmdm_icon($iconData);
        
        if ($result !== false && $result !== null) {
            $response['success'] = true;
            $response['data'] = $result;
        } else {
            $response['error'] = _T('Failed to create icon', 'mobile');
        }
    } catch (Exception $e) {
        $response['error'] = $e->getMessage();
    }
    
    echo json_encode($response);
    exit;
}

require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Fetch icons and files for dropdowns
$availableIcons = xmlrpc_get_hmdm_icons();
$availableFiles = xmlrpc_get_hmdm_files();

$errors = [];
$values = [
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
            error_log('[mobile] ERROR: xmlrpc_add_application returned false/null');
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

// --- Icon dropdown
$iconSelect = new SelectItem('icon_id');
$iconNames = [_T('Choose an icon', 'mobile')];
$iconValues = [''];
if (is_array($availableIcons)) {
    foreach ($availableIcons as $icon) {
        $iconNames[] = $icon['name'];
        $iconValues[] = $icon['id'];
    }
}
$iconSelect->setElements($iconNames);
$iconSelect->setElementsVal($iconValues);
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


    // Function to update Icon extra fields visibility based on Icon checkbox
    function updateIconFields() {
        try {
            let isIconEnabled = $('#showicon').is(':checked') || $('.icon-checkbox').is(':checked');
            clog('DEBUG: isIconEnabled=', isIconEnabled);

            let $fields = $('.icon-extra');

            if (!$fields.length) {
                clog('DEBUG: no icon-extra fields found');
                return;
            }

            $fields.each(function() {
                let $elem = $(this);
                let $parent = $elem.closest('tr');
                
                if (isIconEnabled) {
                    clog('DEBUG: showing icon field');
                    $parent.show();
                } else {
                    clog('DEBUG: hiding icon field');
                    $parent.hide();
                }
            });

        } catch (e) {
            clog('ERROR in updateIconFields:', e);
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

        // AJAX call to create icon
        $.ajax({
            url: window.location.pathname + window.location.search,
            method: 'POST',
            dataType: 'json',
            data: {
                action: 'create_icon',
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
        $(document).on('change', '.system-checkbox', updateApkVisibility);
        setTimeout(updateIconFields, 100);
        $(document).on('change', '.icon-checkbox, #showicon', updateIconFields);
        
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
    });
})(jQuery);
</script>