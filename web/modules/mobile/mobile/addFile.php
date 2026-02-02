<?php

/**
 * Mobile Module - Add File Interface
 * Medulla Management Console (MMC)
 * 
 * Allows users to add files to mobile devices via:
 * - Direct upload from web interface
 * - External URL specification
 */

require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");
require_once("modules/mobile/includes/HtmlClasses.php");

$p = new PageGenerator(_T("Add File", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_POST['bconfirm'])) {
    // Process form submission
    $fileSource = $_POST['file-source'];
    $description = isset($_POST['description']) ? trim($_POST['description']) : '';
    $pathOnDevice = isset($_POST['path_device']) ? trim($_POST['path_device']) : '';
    $variableContent = isset($_POST['variable_content']) ? 1 : 0;

    // Extract selected configurations
    $configIds = array();
    foreach ($_POST as $key => $value) {
        if (strpos($key, 'config_') === 0) {
            $configId = substr($key, 7); // Remove 'config_' prefix
            if ($value) {
                $configIds[] = intval($configId);
            }
        }
    }

    // Validate required fields
    $errors = array();

    if ($fileSource == "upload") {
        // Handle file upload
        if (!isset($_FILES['file_upload']) || $_FILES['file_upload']['error'] !== UPLOAD_ERR_OK) {
            $errors[] = _T("Please select a file to upload", "mobile");
        }

        $fileName = isset($_POST['file_name']) ? trim($_POST['file_name']) : '';
        if (empty($fileName)) {
            $errors[] = _T("File name is required", "mobile");
        }

        if (empty($errors)) {
            // Process upload
            $uploadedFilePath = $_FILES['file_upload']['tmp_name'];
            $uploadedFileName = $_FILES['file_upload']['name'];
            $result = xmlrpc_add_hmdm_file($uploadedFilePath, $uploadedFileName, null, $fileName, $pathOnDevice, $description, $variableContent, $configIds);

            if ($result === true || (is_array($result) && isset($result['id']))) {
                new NotifyWidgetSuccess(sprintf(_T("File '%s' successfully added", "mobile"), $fileName));
                header("Location: " . urlStrRedirect("mobile/mobile/files"));
                exit;
            } else {
                $errorMsg = _T("Failed to add file", "mobile");
                if (is_array($result) && isset($result['message'])) {
                    if ($result['message'] === 'error.duplicate.file') {
                        $errorMsg = _T("A file with the same name already exists", "mobile");
                    } else {
                        $errorMsg = $result['message'];
                    }
                }
                new NotifyWidgetFailure($errorMsg);
            }
        }
    } elseif ($fileSource == "external") {
        // Handle external URL
        $fileUrl = isset($_POST['file_url']) ? trim($_POST['file_url']) : '';

        if (empty($fileUrl)) {
            $errors[] = _T("File URL is required", "mobile");
        } elseif (!filter_var($fileUrl, FILTER_VALIDATE_URL)) {
            $errors[] = _T("Please enter a valid URL", "mobile");
        }

        if (empty($errors)) {
            // Process external URL
            $result = xmlrpc_add_hmdm_file(null, null, $fileUrl, basename($fileUrl), $pathOnDevice, $description, $variableContent, $configIds);

            if ($result === true || (is_array($result) && isset($result['id']))) {
                new NotifyWidgetSuccess(sprintf(_T("External file '%s' successfully added", "mobile"), basename($fileUrl)));
                header("Location: " . urlStrRedirect("mobile/mobile/files"));
                exit;
            } else {
                $errorMsg = _T("Failed to add file", "mobile");
                if (is_array($result) && isset($result['message'])) {
                    if ($result['message'] === 'error.duplicate.file') {
                        $errorMsg = _T("A file with the same name already exists", "mobile");
                    } else {
                        $errorMsg = $result['message'];
                    }
                }
                new NotifyWidgetFailure($errorMsg);
            }
        }
    }

    // Display errors
    if (!empty($errors)) {
        foreach ($errors as $error) {
            new NotifyWidgetFailure($error);
        }
    }
}

// Display form
$f = new ValidatingForm([
    "id" => "Form",
    "method" => "post",
    "enctype" => "multipart/form-data"
]);
$f->push(new Table());

// Section title
$span = new SpanElement(_T("File Source", "mobile"), "mobile-title");
$f->add(new TrFormElement("", $span));

// File source radio buttons
$r = new RadioTpl("file-source");
$vals = array("upload", "external");
$keys = array(
    _T("Upload from this web page", "mobile"),
    _T("External file (URL)", "mobile")
);
$r->setValues($vals);
$r->setChoices($keys);
$r->setSelected("upload");
$f->add(new TrFormElement(_T("Source", "mobile"), $r), array());

// Upload-specific fields container
$f->add(
    new TrFormElement(
        _T("File", "mobile"),
        new FileTpl("file_upload"),
        array("class" => "upload-field")
    ),
    array("value" => '')
);

$f->add(
    new TrFormElement(
        _T("File Name", "mobile"),
        new AsciiInputTpl("file_name"),
        array("class" => "upload-field", "id" => "file_name")
    ),
    array("value" => '', "placeholder" => _T("Auto-filled from upload", "mobile"))
);

// External URL field (hidden by default)
$f->add(
    new TrFormElement(
        _T("File URL", "mobile"),
        new InputTpl("file_url"),
        array("class" => "external-field", "style" => "display:none;")
    ),
    array("value" => '', "placeholder" => _T("https://example.com/file.apk", "mobile"))
);

// Always-visible fields section
$span = new SpanElement(_T("File Details", "mobile"), "mobile-title");
$f->add(new TrFormElement("", $span));

$f->add(
    new TrFormElement(
        _T("Description", "mobile"),
        new InputTpl("description")
    ),
    array("value" => '', "placeholder" => _T("Optional description", "mobile"))
);

$f->add(
    new TrFormElement(
        _T("Path on Device", "mobile"),
        new AsciiInputTpl("path_device")
    ),
    array(
        "value" => '',
        "placeholder" => _T("Path relative to /storage/emulated/0", "mobile")
    )
);

$f->add(
    new TrFormElement(
        _T("Variable Content", "mobile"),
        new CheckboxTpl("variable_content")
    ),
    array("value" => '', "help" => _T("Mark if file content will be processed on device", "mobile"))
);

// Configurations section
$span = new SpanElement(_T("Link to Configurations", "mobile"), "mobile-title");
$f->add(new TrFormElement("", $span));

$configs = xmlrpc_get_hmdm_configurations();
if ($configs && is_array($configs)) {
    foreach ($configs as $config) {
        $f->add(
            new TrFormElement(
                $config['name'],
                new CheckboxTpl("config_" . $config['id'])
            ),
            array("value" => '', "help" => $config['description'] ?? '')
        );
    }
} else {
    $f->add(new TrFormElement("", new SpanElement(_T("No configurations available", "mobile"), "info-text")));
}

$f->pop();
$f->addValidateButton("bconfirm", _T("Add File", "mobile"));
$f->display();
?>

<style>
    .mobile-title {
        font-weight: bold;
        font-size: 1.1em;
        color: #333;
        display: block;
        margin: 15px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 2px solid #e0e0e0;
    }
</style>

<script type="text/javascript">
    jQuery(function() {
        // Remove 'active' class from radio buttons on page load
        jQuery('input[name="file-source"]').removeClass('active');

        // Auto-fill file name when file is selected
        jQuery('#file_upload').on('change', function() {
            var fileName = this.files && this.files[0] ? this.files[0].name : '';
            if (fileName) {
                jQuery('#file_name').val(fileName);
            }
        });

        // Toggle field visibility based on file source selection
        function updateFieldVisibility() {
            var selectedSource = jQuery('input:checked[type="radio"][name="file-source"]').val();

            console.log("Selected source:", selectedSource); // Debug

            if (selectedSource == "upload") {
                // Show upload fields, hide URL field
                jQuery('.upload-field').closest('tr').show();
                jQuery('.external-field').closest('tr').hide();

                // Set required attributes
                jQuery('#file_upload').prop('required', true);
                jQuery('#file_name').prop('required', true);
                jQuery('#file_url').removeAttr('required');

            } else if (selectedSource == "external") {
                // Hide upload fields, show URL field
                jQuery('.upload-field').closest('tr').hide();
                jQuery('.external-field').closest('tr').show();

                // Set required attributes
                jQuery('#file_upload').removeAttr('required');
                jQuery('#file_name').removeAttr('required');
                jQuery('#file_url').prop('required', true);
            }
        }

        // Initialize visibility on page load
        setTimeout(function() {
            updateFieldVisibility();
        }, 100);

        // Update visibility when radio selection changes
        jQuery('input[name="file-source"]').change(function() {
            updateFieldVisibility();
        });

        // Validate description field (no special characters)
        jQuery("#description").on("change blur", function() {
            var description = jQuery(this).val();
            var validPattern = /^[A-Za-z0-9\.\-\!\?\ \#%@\*\+_\/]*$/;
        });
    });
</script>