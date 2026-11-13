<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/settingsWin.php

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

if (!updatesModuleOpen()) {
    updatesClosedPage(_T("Settings", "updates"), $sidemenu);
    return;
}

$entity = updatesWinProductsEntity();

if ($entity && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['bsave'])) {
    verifyCSRFToken($_POST);
    $autoDeploy = isset($_POST['auto_deploy']);
    $startRaw = is_string($_POST['window_start'] ?? null) ? trim($_POST['window_start']) : '';
    $endRaw = is_string($_POST['window_end'] ?? null) ? trim($_POST['window_end']) : '';
    $upgradeStartRaw = is_string($_POST['upgrade_window_start'] ?? null) ? trim($_POST['upgrade_window_start']) : '';
    $upgradeEndRaw = is_string($_POST['upgrade_window_end'] ?? null) ? trim($_POST['upgrade_window_end']) : '';
    $start = updatesWinTimeValue($startRaw);
    $end = updatesWinTimeValue($endRaw);
    $upgradeStart = updatesWinTimeValue($upgradeStartRaw);
    $upgradeEnd = updatesWinTimeValue($upgradeEndRaw);
    $current = xmlrpc_get_windows_settings(updatesEntityId($entity));
    if (($startRaw !== '' && $start === null) || ($endRaw !== '' && $end === null)
        || ($upgradeStartRaw !== '' && $upgradeStart === null) || ($upgradeEndRaw !== '' && $upgradeEnd === null)) {
        new NotifyWidgetFailure(_T("Times must be written HH:MM, for example 22:00.", "updates"));
    } elseif ($autoDeploy && ($start === null || $end === null)) {
        new NotifyWidgetFailure(_T("Give the start and end times to deploy automatically.", "updates"));
    } elseif ($autoDeploy && $start === $end) {
        new NotifyWidgetFailure(_T("The start and end times must differ.", "updates"));
    } elseif (($upgradeStart === null) !== ($upgradeEnd === null)) {
        new NotifyWidgetFailure(_T("Give both times of the upgrade range, or none.", "updates"));
    } elseif ($upgradeStart !== null && $upgradeStart === $upgradeEnd) {
        new NotifyWidgetFailure(_T("The start and end times of the upgrade range must differ.", "updates"));
    } elseif (updatesReadFailed($current)) {
        new NotifyWidgetFailure(_T("The settings could not be saved.", "updates"));
    } elseif (updatesWinInheritedEntity($current['inherited_from'] ?? null) !== null
              && $autoDeploy === (updatesWinTriState($current['auto_deploy'] ?? null) === true)
              && ($start ?? '') === (updatesWinTimeValue($current['window_start'] ?? '') ?? '')
              && ($end ?? '') === (updatesWinTimeValue($current['window_end'] ?? '') ?? '')
              && ($upgradeStart ?? '') === (updatesWinTimeValue($current['upgrade_window_start'] ?? '') ?? '')
              && ($upgradeEnd ?? '') === (updatesWinTimeValue($current['upgrade_window_end'] ?? '') ?? '')) {
        new NotifyWidgetSuccess(_T("No change: the setting stays inherited.", "updates"));
    } elseif (xmlrpc_set_windows_settings(updatesEntityId($entity), $autoDeploy, $start ?? '', $end ?? '',
                                          $upgradeStart ?? '', $upgradeEnd ?? '') === true) {
        new NotifyWidgetSuccess(_T("Settings saved.", "updates"));
    } else {
        new NotifyWidgetFailure(_T("The settings could not be saved.", "updates"));
    }
    header("Location: " . urlStrRedirect("updates/updates/settingsWin", array('location' => $entity['uuid'])));
    exit;
}

$p = new PageGenerator(_T("Settings", "updates"));
$p->setSideMenu($sidemenu);
$p->display();
updatesCatalogSection();

if (!$entity) {
    EmptyStateBox::show(_T("No entity available for this user.", "updates"));
    return;
}

$settings = xmlrpc_get_windows_settings(updatesEntityId($entity));
if (updatesReadFailed($settings)) {
    updatesReadFailedBox();
    return;
}
$autoDeploy = updatesWinTriState($settings['auto_deploy'] ?? null) === true;
$start = updatesWinTimeValue($settings['window_start'] ?? '') ?? '';
$end = updatesWinTimeValue($settings['window_end'] ?? '') ?? '';
$upgradeStart = updatesWinTimeValue($settings['upgrade_window_start'] ?? '') ?? '';
$upgradeEnd = updatesWinTimeValue($settings['upgrade_window_end'] ?? '') ?? '';

$timeRegexp = '/^([01][0-9]|2[0-3]):[0-5][0-9]$/';
$startTpl = new InputTpl('window_start', $timeRegexp);
$startTpl->setSize(5);
$startTpl->setAttributCustom('maxlength="5"');
$endTpl = new InputTpl('window_end', $timeRegexp);
$endTpl->setSize(5);
$endTpl->setAttributCustom('maxlength="5"');
$upgradeStartTpl = new InputTpl('upgrade_window_start', $timeRegexp);
$upgradeStartTpl->setSize(5);
$upgradeStartTpl->setAttributCustom('maxlength="5"');
$upgradeEndTpl = new InputTpl('upgrade_window_end', $timeRegexp);
$upgradeEndTpl->setSize(5);
$upgradeEndTpl->setAttributCustom('maxlength="5"');

echo '<div class="updates-settings-form">';
$form = new ValidatingForm(array('method' => 'POST'));
$form->add(new SpanElement(_T("Entity", "updates"), "section-title"));
$form->push(new Table());
$form->add(new TrFormElement("", new UpdatesEntitySelectTpl()),
           array("entity" => $entity, "allowAll" => false,
                 "aside" => updatesWinInheritanceLine($entity, 'settings', $settings)));
$form->pop();
$form->add(new SpanElement(_T("Automatic deployment", "updates"), "section-title"));
$form->push(new Table());
$form->add(new TrFormElement(_T("Enable", "updates"), new CheckboxTpl('auto_deploy')),
           array("value" => $autoDeploy ? "checked" : ""));
$form->add(new TrFormElement(_T("Time range", "updates"), new UpdatesTimeRangeTpl($startTpl, $endTpl)),
           array("start" => htmlspecialchars($start, ENT_QUOTES, 'UTF-8'),
                 "end" => htmlspecialchars($end, ENT_QUOTES, 'UTF-8'),
                 "placeholder" => "HH:MM"));
$form->pop();
$form->add(new ParaElement(htmlspecialchars(_T("Approved updates are sent on their own to the machines during this time range. Servers stay on manual deployment.", "updates"), ENT_QUOTES, 'UTF-8'), "updates-settings-note"));
$form->add(new SpanElement(_T("Upgrades", "updates"), "section-title"));
$form->push(new Table());
$form->add(new TrFormElement(_T("Time range", "updates"), new UpdatesTimeRangeTpl($upgradeStartTpl, $upgradeEndTpl)),
           array("start" => htmlspecialchars($upgradeStart, ENT_QUOTES, 'UTF-8'),
                 "end" => htmlspecialchars($upgradeEnd, ENT_QUOTES, 'UTF-8'),
                 "placeholder" => "HH:MM"));
$form->pop();
$form->add(new ParaElement(htmlspecialchars(_T("The steps of the launched upgrades only start during this time range. Without a range, they start right away.", "updates"), ENT_QUOTES, 'UTF-8'), "updates-settings-note"));
$form->addValidateButtonWithValue('bsave', _T("Save", "updates"));
$form->display();
echo '</div>';
?>
