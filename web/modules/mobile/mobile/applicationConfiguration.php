<?php
/**
 * Attach a configuration to an application
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");
require_once("modules/imaging/includes/class_form.php");

$appId = isset($_GET['id']) ? intval($_GET['id']) : 0;
$appName = isset($_GET['name']) ? htmlentities($_GET['name']) : '';

if (!$appId) {
    new NotifyWidgetFailure(_T("Application ID is required", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/applications"));
    exit;
}

$configs = xmlrpc_get_configuration_names();
$selectedConfigId = null;

// If the application already has a configuration, preselect it
if ($_SERVER['REQUEST_METHOD'] !== 'POST' && is_array($configs)) {
    foreach ($configs as $cfg) {
        $cid = isset($cfg['id']) ? intval($cfg['id']) : 0;
        if ($cid <= 0) continue;

        // Fetch applications linked to this configuration and see if current app is present
        $cfgApps = xmlrpc_get_hmdm_configuration_applications($cid);
        if (!is_array($cfgApps) || empty($cfgApps)) {
            continue;
        }

        foreach ($cfgApps as $appEntry) {
            $appEntryId = null;
            if (is_array($appEntry)) {
                if (isset($appEntry['id'])) {
                    $appEntryId = intval($appEntry['id']);
                } elseif (isset($appEntry['applicationId'])) {
                    $appEntryId = intval($appEntry['applicationId']);
                }
            }

            if ($appEntryId !== null && $appEntryId === $appId) {
                $selectedConfigId = $cid;
                break 2;
            }
        }
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $selectedConfigId = intval($_POST['configuration_id'] ?? 0);
    $configName = '';

    if (is_array($configs)) {
        foreach ($configs as $cfg) {
            $cid = isset($cfg['id']) ? intval($cfg['id']) : 0;
            if ($cid === $selectedConfigId) {
                $configName = $cfg['name'] ?? '';
                break;
            }
        }
    }

    if ($selectedConfigId <= 0) {
        new NotifyWidgetFailure(_T("Please select a configuration", "mobile"));
    } else {
        $result = xmlrpc_update_application_configurations($appId, $selectedConfigId, $configName);
        $status = is_array($result) ? ($result['status'] ?? '') : '';
        $success = false;
        if (is_array($result)) {
            if (isset($result['success']) && $result['success'] === true) {
                $success = true;
            } elseif (is_string($status) && strtoupper($status) === 'OK') {
                $success = true;
            }
        }

        if ($success) {
            new NotifyWidgetSuccess(_T("Configuration added successfully", "mobile"));
        } else {
            $msg = '';
            if (is_array($result) && isset($result['message'])) {
                $msg = $result['message'];
            }
            if (!$msg) {
                $msg = _T("Error adding configuration", "mobile");
            }
            new NotifyWidgetFailure($msg);
        }
    }
}

$p = new PageGenerator(sprintf(_T("Configuration for %s", "mobile"), $appName));
$p->setSideMenu($sidemenu);
$p->display();

if (!is_array($configs) || empty($configs)) {
    echo '<div class="alert alert-info">' . _T("No configurations available", "mobile") . '</div>';
    echo '<div style="margin-top: 15px;">';
    echo '<a href="' . urlStrRedirect("mobile/mobile/applications") . '" class="btn btn-primary">' . _T("Back to Applications", "mobile") . '</a>';
    echo '</div>';
    exit;
}

$sep = new SpanElement('<hr/>');

$form = new ValidatingForm(['id' => 'formConfig', 'class' => '']);

$hiddenAppId = new InputTpl('id', '/^.{0,255}$/', $appId);
$hiddenAppId->fieldType = 'hidden';
$form->add(new TrFormElement('', $hiddenAppId));

$labels = [];
$vals = [];
foreach ($configs as $cfg) {
    $vals[] = isset($cfg['id']) ? intval($cfg['id']) : 0;
    $labels[] = $cfg['name'] ?? '';
}

$select = new SelectItem('configuration_id');
$select->setElements($labels);
$select->setElementsVal($vals);
$select->setSelected($selectedConfigId);

$form->add(new TrFormElement(_T('Select a configuration', 'mobile'), $select));

$form->addValidateButton('test');

$backHtml = '<a href="' . urlStrRedirect("mobile/mobile/applications") . '" class="btn" style="margin-left: 8px;">' . _T("Back to Applications", "mobile") . '</a>';
$form->add(new TrFormElement('', new SpanElement($backHtml)));

$form->display();

?>
