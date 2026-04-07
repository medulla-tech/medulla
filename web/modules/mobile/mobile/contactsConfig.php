<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$configId = isset($_GET['id']) ? intval($_GET['id']) : 0;
if ($configId <= 0) {
    new NotifyWidgetFailure(_T("Invalid configuration ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/contactsList"));
    exit;
}

$configurations = xmlrpc_get_hmdm_configurations();
$configName = '';
if (is_array($configurations)) {
    foreach ($configurations as $cfg) {
        if (isset($cfg['id']) && $cfg['id'] == $configId) {
            $configName = $cfg['name'] ?? '';
            break;
        }
    }
}

$notifyMessage = null;
$notifyError = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['bcancel'])) {
        header("Location: " . urlStrRedirect("mobile/mobile/contactsList"));
        exit;
    }

    if (isset($_POST['bsave'])) {
        $contactsData = array(
            'configurationId' => $configId,
            'url'             => isset($_POST['contacts_url']) ? trim($_POST['contacts_url']) : '',
            'login'           => isset($_POST['contacts_login']) ? trim($_POST['contacts_login']) : '',
            'password'        => isset($_POST['contacts_password']) ? $_POST['contacts_password'] : '',
            'accountType'     => isset($_POST['contacts_account_type']) ? trim($_POST['contacts_account_type']) : 'com.android.contacts',
            'syncInterval'    => isset($_POST['contacts_sync_interval']) ? intval($_POST['contacts_sync_interval']) : 60,
            'wipeContacts'    => isset($_POST['contacts_wipe']),
        );


        if (isset($_POST['contacts_id']) && $_POST['contacts_id'] !== '') {
            $contactsData['id'] = intval($_POST['contacts_id']);
        }

        $result = xmlrpc_save_hmdm_contacts_config($contactsData);
        if ($result !== null && isset($result['status']) && strtoupper($result['status']) === 'OK') {
            $notifyMessage = _T("Contacts configuration saved successfully", "mobile");
        } else {
            $notifyError = _T("Failed to save contacts configuration", "mobile");
        }
    }
}

$contactsConfig = xmlrpc_get_hmdm_contacts_config($configId);
if (!is_array($contactsConfig)) {
    $contactsConfig = array(
        'configurationId' => $configId,
        'url'             => '',
        'login'           => '',
        'password'        => '',
        'accountType'     => 'com.android.contacts',
        'syncInterval'    => 60,
        'wipeContacts'    => false,
    );
}

$p = new PageGenerator(sprintf(_T("Contacts sync — %s", "mobile"), htmlspecialchars($configName)));
$p->setSideMenu($sidemenu);
$p->display();
?>

<?php if (!empty($notifyMessage)) { new NotifyWidgetSuccess($notifyMessage); } ?>
<?php if (!empty($notifyError))   { new NotifyWidgetFailure($notifyError); } ?>

<?php
$form = new ValidatingForm();
$form->push(new Table());

$idTpl = new HiddenTpl("contacts_id");
$form->add($idTpl, array("value" => isset($contactsConfig['id']) ? $contactsConfig['id'] : '', "hide" => true));

$form->add(new TrFormElement(
    _T("VCF URL", "mobile"),
    new InputTpl("contacts_url", '/^.*$/', isset($contactsConfig['url']) ? $contactsConfig['url'] : '')
), array(
    "value"       => isset($contactsConfig['url']) ? $contactsConfig['url'] : '',
    "placeholder" => _T("https://example.com/contacts.vcf", "mobile"),
    "tooltip"     => _T("URL of a VCF file the device will download and import as contacts", "mobile")
));

$form->add(new TrFormElement(
    _T("HTTP login", "mobile"),
    new InputTpl("contacts_login", '/^.*$/', isset($contactsConfig['login']) ? $contactsConfig['login'] : '')
), array(
    "value"       => isset($contactsConfig['login']) ? $contactsConfig['login'] : '',
    "placeholder" => _T("Optional — leave empty if not required", "mobile")
));

$form->add(new TrFormElement(
    _T("HTTP password", "mobile"),
    new InputTpl("contacts_password", '/^.*$/', '')
), array(
    "value"       => '',
    "placeholder" => _T("Optional — leave empty to keep existing password", "mobile")
));

$form->add(new TrFormElement(
    _T("Account type", "mobile"),
    new InputTpl("contacts_account_type", '/^.*$/', isset($contactsConfig['accountType']) ? $contactsConfig['accountType'] : 'com.android.contacts')
), array(
    "value"   => isset($contactsConfig['accountType']) ? $contactsConfig['accountType'] : 'com.android.contacts',
    "tooltip" => _T("Android contacts account type — usually com.android.contacts", "mobile")
));

$form->add(new TrFormElement(
    _T("Sync interval (minutes)", "mobile"),
    new InputTpl("contacts_sync_interval", '/^\d+$/', isset($contactsConfig['syncInterval']) ? $contactsConfig['syncInterval'] : 60)
), array(
    "value"   => isset($contactsConfig['syncInterval']) ? $contactsConfig['syncInterval'] : 60,
    "tooltip" => _T("How often the device re-syncs, in minutes. 0 = manual only.", "mobile")
));

$form->add(new TrFormElement(
    _T("Wipe contacts before import", "mobile"),
    new CheckboxTpl("contacts_wipe"),
    array("tooltip" => _T("If checked, the device will wipe all existing contacts before importing from the VCF URL", "mobile"))
), array("value" => (isset($contactsConfig['wipeContacts']) && $contactsConfig['wipeContacts']) ? 'checked' : ''));

$form->pop();

$form->addButton("bsave",   _T("Save", "mobile"));
$form->addButton("bcancel", _T("Cancel", "mobile"));
$form->display();
?>
