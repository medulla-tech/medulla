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
    'usedVersionId' => $app['usedVersionId'] ?? '',
    'versioncode' => $app['versionCode'] ?? '',
];

// POST handler (update)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['bconfirm'])) {
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
?>

<form action="<?php echo htmlspecialchars($_SERVER["REQUEST_URI"]); ?>" method="post">
<input type="hidden" name="id"           value="<?php echo htmlspecialchars($values['id']); ?>" />
<input type="hidden" name="type"         value="<?php echo htmlspecialchars($values['type']); ?>" />
<input type="hidden" name="version"      value="<?php echo htmlspecialchars($values['version']); ?>" />
<input type="hidden" name="arch"         value="<?php echo htmlspecialchars($values['arch']); ?>" />
<input type="hidden" name="filePath"     value="<?php echo htmlspecialchars($values['filePath']); ?>" />
<input type="hidden" name="versioncode"  value="<?php echo htmlspecialchars($values['versioncode']); ?>" />
<input type="hidden" name="usedVersionId" value="<?php echo htmlspecialchars($values['usedVersionId']); ?>" />
<input type="hidden" name="showicon"     value="<?php echo $values['showicon'] ? '1' : ''; ?>" />
<input type="hidden" name="icon_id"      value="<?php echo htmlspecialchars($values['icon_id']); ?>" />
<input type="hidden" name="icon_text"    value="<?php echo htmlspecialchars($values['icon_text']); ?>" />
<?php

require_once("modules/imaging/includes/class_form.php");

$f = new ValidatingForm();
$f->push(new Table());

$f->add(new TrFormElement(_T("Application name", "mobile"), new InputTpl("name", '/^.{1,255}$/', $values['name'])),
    array("value" => $values['name']));

if ($values['type'] === 'app') {
    $f->add(new TrFormElement(_T("Package ID", "mobile"), new InputTpl("pkg", '/^.{0,255}$/', $values['pkg'])),
        array("value" => $values['pkg']));

    $versionLabel = $values['version'] !== '' ? $values['version'] : '-';
    $f->add(new TrFormElement(_T("Version", "mobile"),
        new SpanElement('<div style="padding:5px 0;color:#555;">' . htmlspecialchars($versionLabel) . '</div>')));

    $checkboxSystem = new InputTpl('system', '/^.{0,1}$/', '');
    $checkboxSystem->fieldType = 'checkbox';
    if ($values['system']) $checkboxSystem->setAttributCustom('checked');
    $f->add(new TrFormElement(_T("System application", "mobile"), $checkboxSystem));

    $checkboxRunAfterInstall = new InputTpl('runAfterInstall', '/^.{0,1}$/', '');
    $checkboxRunAfterInstall->fieldType = 'checkbox';
    if ($values['runAfterInstall']) $checkboxRunAfterInstall->setAttributCustom('checked');
    $f->add(new TrFormElement(_T("Run after install", "mobile"), $checkboxRunAfterInstall));

    $checkboxRunAtBoot = new InputTpl('runAtBoot', '/^.{0,1}$/', '');
    $checkboxRunAtBoot->fieldType = 'checkbox';
    if ($values['runAtBoot']) $checkboxRunAtBoot->setAttributCustom('checked');
    $f->add(new TrFormElement(_T("Run at boot", "mobile"), $checkboxRunAtBoot));

    if ($values['url'] !== '') {
        $apkFileName = basename(parse_url($values['url'], PHP_URL_PATH) ?? '');
        if ($apkFileName === '') $apkFileName = '-';
        $f->add(new TrFormElement(_T("APK file", "mobile"),
            new SpanElement('<div style="padding:5px 0;color:#555;">' . htmlspecialchars($apkFileName) . '</div>')));
    }

    if ($values['url'] !== '') {
        $f->add(new TrFormElement(_T("URL", "mobile"), new InputTpl("url", '/^.*$/', $values['url'])),
            array("value" => $values['url']));
    }

} elseif ($values['type'] === 'web') {
    $f->add(new TrFormElement(_T("URL", "mobile"), new InputTpl("url", '/^.+$/', $values['url'])),
        array("value" => $values['url']));

    $checkboxKiosk = new InputTpl('useKiosk', '/^.{0,1}$/', '');
    $checkboxKiosk->fieldType = 'checkbox';
    if ($values['useKiosk']) $checkboxKiosk->setAttributCustom('checked');
    $f->add(new TrFormElement(_T("Open in Kiosk-Browser", "mobile"), $checkboxKiosk));

} elseif ($values['type'] === 'intent') {
    $f->add(new TrFormElement(_T("Action", "mobile"), new InputTpl("action", '/^.{1,255}$/', $values['action'])),
        array("value" => $values['action']));
}

$f->pop();
foreach ($f->elements as $element) {
    $element->display();
}

?>

<div style="margin-top: 20px;">
    <input name="bconfirm" type="submit" class="btnPrimary" value="<?php echo _T("Save", "mobile"); ?>" />
    <input type="button" class="btnSecondary" style="margin-left:8px;" value="<?php echo _T("Cancel", "mobile"); ?>" onclick="location.href='main.php?module=mobile&submod=mobile&action=applications';" />
</div>
</form>
