<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * Reflex Module - Settings Tab: Data Retention
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$login = reflex_current_login();
$retentionFields = array(
    'measures_days' => array(_T("Measures", "reflex"), array(7, 15, 30, 60, 90, 180, 365)),
    'alerts_resolved_days' => array(_T("Resolved alerts", "reflex"), array(30, 90, 180, 365, 730, 1095)),
    'notification_history_days' => array(_T("Sending history", "reflex"), array(30, 90, 180, 365, 730, 1095))
);
$retentionRefused = '';

$retention = xmlrpc_reflex_get_retention_settings($login);
if (!is_array($retention)) {
    $retention = array();
}

if (isset($_POST['bsave'])) {
    verifyCSRFToken($_POST);
    $retentionValues = array();
    foreach (array_keys($retentionFields) as $retentionKey) {
        $retentionValues[$retentionKey] = intval($_POST[$retentionKey] ?? 0);
    }
    $refusal = ReflexHelper::callRefusal(xmlrpc_reflex_set_retention_settings($login, $retentionValues));
    if ($refusal === null) {
        new NotifyWidgetSuccess(_T("Retention saved", "reflex"));
    } else {
        new NotifyWidgetFailure(ReflexHelper::refusalMessage(
            $refusal, _T("Failed to save the retention", "reflex")));
        $retentionRefused = $refusal['field'];
    }
    $retention = array_merge($retention, $retentionValues);
}

$form = new ValidatingForm(array(
    'method' => 'POST',
    'action' => urlStrRedirect('reflex/reflex/settings', array('tab' => 'tabretention'))
));
$form->add(new SpanElement(_T("Retention", "reflex"), "section-title"));
$form->add(new SpanElement(htmlspecialchars(_T("Older data is deleted every night.", "reflex")), "reflex-help"));
$form->push(new Table());
foreach ($retentionFields as $retentionKey => $retentionField) {
    $retentionCurrent = intval($retention[$retentionKey] ?? 0);
    $retentionSelect = new SelectItem($retentionKey, null,
        ($retentionRefused === $retentionKey) ? 'reflex-invalid-field' : null);
    $retentionChoices = ReflexHelper::retentionChoices($retentionField[1], $retentionCurrent);
    $retentionSelect->setElements(array_map('htmlspecialchars', array_values($retentionChoices)));
    $retentionSelect->setElementsVal(array_map('strval', array_keys($retentionChoices)));
    $retentionSelect->setSelected((string) $retentionCurrent);
    $form->add(new TrFormElement(htmlspecialchars($retentionField[0]), $retentionSelect));
}
$form->pop();
$form->addValidateButtonWithValue('bsave', _T("Save", "reflex"));
$form->display();
?>
