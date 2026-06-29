<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$notifyMessage = null;
$notifyError   = null;

$settings = xmlrpc_get_photos_settings();
if (!is_array($settings)) {
    $settings = array(
        'transferPhotos'        => false,
        'imagePaths'            => '/sdcard/DCIM/Camera',
        'excludePaths'          => '',
        'includeStandardPaths'  => true,
        'directoryStructure'    => 'DEVICE/YEAR/MONTH/',
        'fileNameTemplate'      => 'img_YEAR_MONTH_DAY_HOUR_MIN_SEC_NAME',
        'removeOldFiles'        => 30,
        'deleteImagesOnDevices' => '',
        'imageLocation'         => true,
    );
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['bcancel'])) {
        header("Location: " . urlStrRedirect("mobile/mobile/photosList"));
        exit;
    }

    if (isset($_POST['bsave']) || isset($_POST['bsaveexit'])) {
        $transferOn = (($_POST['transfer_photos'] ?? '0') === '1');
        $settings['transferPhotos']        = $transferOn;
        $settings['imageLocation']         = $transferOn ? (($_POST['image_location'] ?? '0') === '1') : false;
        $settings['deleteImagesOnDevices'] = (($_POST['delete_images_on_devices'] ?? '0') === '1') ? 'always' : '';

        $result = xmlrpc_save_photos_settings($settings);
        if ($result !== null && isset($result['status']) && strtoupper($result['status']) === 'OK') {
            if (isset($_POST['bsaveexit'])) {
                header("Location: " . urlStrRedirect("mobile/mobile/photosList", array("saved" => "1")));
                exit;
            }
            $notifyMessage = _T("Photos settings saved successfully", "mobile");
        } else {
            $notifyError = _T("Failed to save photos settings", "mobile");
        }
    }
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

$transferTpl = new RadioTpl("transfer_photos");
$transferTpl->setChoices(array(_T("Enabled", "mobile"), _T("Disabled", "mobile")));
$transferTpl->setValues(array("1", "0"));
$transferTpl->setSelected((isset($settings['transferPhotos']) && $settings['transferPhotos']) ? '1' : '0');
$form->add(new TrFormElement(_T("Transfer photos to server", "mobile"), $transferTpl, array('class' => 'radio-inline')));

$locationTpl = new RadioTpl("image_location");
$locationTpl->setChoices(array(_T("Enabled", "mobile"), _T("Disabled", "mobile")));
$locationTpl->setValues(array("1", "0"));
$locationTpl->setSelected((isset($settings['imageLocation']) && $settings['imageLocation']) ? '1' : '0');
$form->add(new TrFormElement(_T("Image location", "mobile"), $locationTpl, array('class' => 'radio-inline')));

$deleteTpl = new RadioTpl("delete_images_on_devices");
$deleteTpl->setChoices(array(_T("Yes", "mobile"), _T("No", "mobile")));
$deleteTpl->setValues(array("1", "0"));
$deleteTpl->setSelected(!empty($settings['deleteImagesOnDevices']) ? '1' : '0');
$form->add(new TrFormElement(_T("Delete images on devices after upload", "mobile"), $deleteTpl, array('class' => 'radio-inline')));

$form->pop();

$form->addButton("bsave",     _T("Save", "mobile"));
$form->addButton("bsaveexit", _T("Save and exit", "mobile"));
$form->addButton("bcancel",   _T("Cancel", "mobile"));
$form->display();
?>

<script type="text/javascript">
jQuery(function() {
    function updateLocationState() {
        var transferOn = jQuery('input[name="transfer_photos"]:checked').val() === '1';
        jQuery('input[name="image_location"], input[name="delete_images_on_devices"]').prop('disabled', !transferOn);
        jQuery('input[name="image_location"], input[name="delete_images_on_devices"]').closest('tr').css('opacity', transferOn ? '' : '0.5');
    }
    jQuery('input[name="transfer_photos"]').on('change', updateLocationState);
    updateLocationState();
});
</script>

