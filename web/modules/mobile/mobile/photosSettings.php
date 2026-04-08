<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$notifyMessage = null;
$notifyError = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['bcancel'])) {
        header("Location: " . urlStrRedirect("mobile/mobile/photosList"));
        exit;
    }

    if (isset($_POST['bsave'])) {
        $settingsData = array(
            'transferPhotos'       => isset($_POST['transfer_photos']),
            'imagePaths'           => isset($_POST['image_paths']) ? trim($_POST['image_paths']) : '',
            'excludePaths'         => isset($_POST['exclude_paths']) ? trim($_POST['exclude_paths']) : '',
            'includeStandardPaths' => isset($_POST['include_standard_paths']),
            'directoryStructure'   => isset($_POST['directory_structure']) ? trim($_POST['directory_structure']) : 'DEVICE/YEAR/MONTH/',
            'fileNameTemplate'     => isset($_POST['file_name_template']) ? trim($_POST['file_name_template']) : 'img_YEAR_MONTH_DAY_HOUR_MIN_SEC_NAME',
            'removeOldFiles'       => isset($_POST['remove_old_files']) ? intval($_POST['remove_old_files']) : 0,
            'imageLocation'        => isset($_POST['image_location']),
        );

        $result = xmlrpc_save_photos_settings($settingsData);
        if ($result !== null && isset($result['status']) && strtoupper($result['status']) === 'OK') {
            $notifyMessage = _T("Photos settings saved successfully", "mobile");
        } else {
            $notifyError = _T("Failed to save photos settings", "mobile");
        }
    }
}

$settings = xmlrpc_get_photos_settings();
if (!is_array($settings)) {
    $settings = array(
        'transferPhotos'       => false,
        'imagePaths'           => '/sdcard/DCIM/Camera',
        'excludePaths'         => '',
        'includeStandardPaths' => true,
        'directoryStructure'   => 'DEVICE/YEAR/MONTH/',
        'fileNameTemplate'     => 'img_YEAR_MONTH_DAY_HOUR_MIN_SEC_NAME',
        'removeOldFiles'       => 30,
        'imageLocation'        => true,
    );
}

$p = new PageGenerator(_T("Photos Settings", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();
?>

<?php if (!empty($notifyMessage)) { new NotifyWidgetSuccess($notifyMessage); } ?>
<?php if (!empty($notifyError))   { new NotifyWidgetFailure($notifyError); } ?>

<?php
$form = new ValidatingForm();
$form->push(new Table());

$form->add(new TrFormElement(
    _T("Enable photo upload", "mobile"),
    new CheckboxTpl("transfer_photos"),
    array("tooltip" => _T("Allow devices to upload photos to the server", "mobile"))
), array("value" => (isset($settings['transferPhotos']) && $settings['transferPhotos']) ? 'checked' : ''));

$form->add(new TrFormElement(
    _T("Image paths", "mobile"),
    new InputTpl("image_paths", '/^.*$/', isset($settings['imagePaths']) ? $settings['imagePaths'] : '')
), array(
    "value"       => isset($settings['imagePaths']) ? $settings['imagePaths'] : '',
    "placeholder" => _T("/sdcard/DCIM/Camera,/sdcard/Pictures", "mobile"),
    "tooltip"     => _T("Comma-separated list of directories to scan for photos on devices", "mobile")
));

$form->add(new TrFormElement(
    _T("Exclude paths", "mobile"),
    new InputTpl("exclude_paths", '/^.*$/', isset($settings['excludePaths']) ? $settings['excludePaths'] : '')
), array(
    "value"       => isset($settings['excludePaths']) ? $settings['excludePaths'] : '',
    "placeholder" => _T("/sdcard/DCIM/.thumbnails", "mobile"),
    "tooltip"     => _T("Comma-separated list of directories to exclude", "mobile")
));

$form->add(new TrFormElement(
    _T("Include standard paths", "mobile"),
    new CheckboxTpl("include_standard_paths"),
    array("tooltip" => _T("Automatically include standard Android camera paths", "mobile"))
), array("value" => (isset($settings['includeStandardPaths']) && $settings['includeStandardPaths']) ? 'checked' : ''));

$form->add(new TrFormElement(
    _T("Directory structure", "mobile"),
    new InputTpl("directory_structure", '/^.*$/', isset($settings['directoryStructure']) ? $settings['directoryStructure'] : '')
), array(
    "value"       => isset($settings['directoryStructure']) ? $settings['directoryStructure'] : '',
    "placeholder" => _T("DEVICE/YEAR/MONTH/", "mobile"),
    "tooltip"     => _T("Template for server directory structure. Available: DEVICE, YEAR, MONTH, DAY", "mobile")
));

$form->add(new TrFormElement(
    _T("File name template", "mobile"),
    new InputTpl("file_name_template", '/^.*$/', isset($settings['fileNameTemplate']) ? $settings['fileNameTemplate'] : '')
), array(
    "value"       => isset($settings['fileNameTemplate']) ? $settings['fileNameTemplate'] : '',
    "placeholder" => _T("img_YEAR_MONTH_DAY_HOUR_MIN_SEC_NAME", "mobile"),
    "tooltip"     => _T("Template for file names. Available: YEAR, MONTH, DAY, HOUR, MIN, SEC, NAME", "mobile")
));

$form->add(new TrFormElement(
    _T("Delete photos older than (days)", "mobile"),
    new InputTpl("remove_old_files", '/^\d+$/', isset($settings['removeOldFiles']) ? $settings['removeOldFiles'] : 0)
), array(
    "value"   => isset($settings['removeOldFiles']) ? $settings['removeOldFiles'] : 0,
    "tooltip" => _T("Automatically delete photos older than this many days. 0 = never delete", "mobile")
));

$form->add(new TrFormElement(
    _T("Store location metadata", "mobile"),
    new CheckboxTpl("image_location"),
    array("tooltip" => _T("Save GPS coordinates and address with photos", "mobile"))
), array("value" => (isset($settings['imageLocation']) && $settings['imageLocation']) ? 'checked' : ''));

$form->pop();

$form->addButton("bsave",   _T("Save", "mobile"));
$form->addButton("bcancel", _T("Cancel", "mobile"));
$form->display();
?>
