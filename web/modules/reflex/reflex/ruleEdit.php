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
 * Reflex Module - Notification rule creation and modification
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$ruleId = isset($_GET['rule_id']) ? intval($_GET['rule_id']) : 0;
if ($ruleId <= 0 && isset($_POST['rule_id'])) {
    $ruleId = intval($_POST['rule_id']);
}
$isNew = ($ruleId <= 0);
$login = reflex_current_login();

$severityOptions = ReflexHelper::severityOptions();

$channels = xmlrpc_reflex_get_channels($login);
if (!is_array($channels)) {
    $channels = array();
}

// The whole catalog keeps the select short and meaningful for notifications.
$probesResult = xmlrpc_reflex_get_probes($login, 0, 500, '', 'all');
$probes = (is_array($probesResult) && isset($probesResult['data']) && is_array($probesResult['data']))
    ? $probesResult['data'] : array();

$rule = array(
    'channel_id' => 0,
    'probe_id' => 0,
    'min_severity' => 'high',
    'recipients' => '',
    'target_filter' => '',
    'cooldown_minutes' => 60,
    'escalation_minutes' => '',
    'enabled' => 1
);

if (!$isNew) {
    $rules = xmlrpc_reflex_get_notification_rules($login);
    $found = null;
    if (is_array($rules)) {
        foreach ($rules as $row) {
            if (intval($row['id'] ?? 0) === $ruleId) {
                $found = $row;
                break;
            }
        }
    }
    if ($found === null) {
        $rule = null;
    } else {
        $rule = array_merge($rule, $found);
    }
}

// Read after the rule itself, so a directory that answers badly cannot cost
// the page the row it edits. Only a value of this list is accepted.
$targetFilterOptions = ReflexTargets::ruleFilterOptions();
$storedFilter = is_array($rule) ? trim((string) ($rule['target_filter'] ?? '')) : '';

if (isset($_POST['bsave'])) {
    verifyCSRFToken($_POST);

    // With nothing to offer the field is not rendered, so the rule keeps the
    // restriction it carries instead of losing it on save.
    $targetFilter = empty($targetFilterOptions)
        ? $storedFilter
        : trim((string) ($_POST['target_filter'] ?? ''));

    $escalation = trim((string) ($_POST['escalation_minutes'] ?? ''));
    $payload = array(
        'channel_id' => intval($_POST['channel_id'] ?? 0),
        'probe_id' => intval($_POST['probe_id'] ?? 0) ?: null,
        'min_severity' => (string) ($_POST['min_severity'] ?? 'high'),
        'recipients' => trim((string) ($_POST['recipients'] ?? '')),
        'target_filter' => $targetFilter,
        'cooldown_minutes' => intval($_POST['cooldown_minutes'] ?? 60),
        'escalation_minutes' => ($escalation === '') ? null : intval($escalation),
        'enabled' => isset($_POST['enabled']) ? 1 : 0
    );

    $error = '';
    if ($payload['channel_id'] <= 0) {
        $error = _T("Please select a notification channel", "reflex");
    } elseif (!isset($severityOptions[$payload['min_severity']])) {
        $error = _T("Unknown severity", "reflex");
    } elseif ($payload['cooldown_minutes'] < 0) {
        $error = _T("The cooldown must not be negative", "reflex");
    } elseif (!empty($targetFilterOptions) && $targetFilter !== ''
              && !isset($targetFilterOptions[$targetFilter])) {
        $error = _T("Please pick a target restriction in the list", "reflex");
    }

    $refusedField = '';
    if ($error !== '') {
        new NotifyWidgetFailure($error);
    } else {
        if ($isNew) {
            $created = xmlrpc_reflex_create_notification_rule($login, $payload);
            // A refusal answers a structure, which is true in PHP: only the identifier
            // says the rule exists.
            if (ReflexHelper::createdId($created) > 0) {
                new NotifyWidgetSuccess(_T("Notification rule created", "reflex"));
                header("Location: " . urlStrRedirect("reflex/reflex/settings", array("tab" => "tabrules")));
                exit;
            }
            $refusal = ReflexHelper::callRefusal($created);
            $refusedField = $refusal['field'];
            new NotifyWidgetFailure(ReflexHelper::refusalMessage(
                $refusal, _T("Failed to create the notification rule", "reflex")));
        } else {
            $result = xmlrpc_reflex_update_notification_rule($ruleId, $payload, $login);
            if ($result === true || $result === 1) {
                new NotifyWidgetSuccess(_T("Notification rule updated", "reflex"));
                header("Location: " . urlStrRedirect("reflex/reflex/settings", array("tab" => "tabrules")));
                exit;
            }
            $refusal = ReflexHelper::callRefusal($result);
            $refusedField = $refusal['field'];
            new NotifyWidgetFailure(ReflexHelper::refusalMessage(
                $refusal, _T("Failed to update the notification rule", "reflex")));
        }
    }
    // What was typed stays on screen, an imported list included.
    if (is_array($rule)) {
        $rule = array_merge($rule, $payload);
    }
}

$p = new PageGenerator($isNew ? _T("New notification rule", 'reflex') : _T("Edit notification rule", 'reflex'));
$p->setSideMenu($sidemenu);
$p->display();

if (!$isNew && $rule === null) {
    EmptyStateBox::show(
        _T("Notification rule not found", "reflex"),
        _T("This notification rule does not exist any more.", "reflex")
    );
    return;
}

if (empty($channels)) {
    EmptyStateBox::show(
        _T("No notification channel", "reflex"),
        _T("Create a notification channel before adding a rule.", "reflex")
    );
    return;
}

// InputTpl and TextareaTpl print their value attribute verbatim, and
// SelectItem does the same with its option labels: escaped before reaching one.
$safe = function ($value) {
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
};

echo '<a href="' . urlStrRedirect('reflex/reflex/settings', array('tab' => 'tabrules')) . '" class="back-link">&larr; '
   . htmlspecialchars(_T("Back to notification rules", "reflex")) . '</a>';

// --- Selects --------------------------------------------------------------
$channelLabels = array();
$channelValues = array();
foreach ($channels as $row) {
    if (!is_array($row)) {
        continue;
    }
    $channelLabels[] = $safe($row['name'] ?? '');
    $channelValues[] = (string) intval($row['id'] ?? 0);
}
$channelSelect = new SelectItem('channel_id');
$channelSelect->setElements($channelLabels);
$channelSelect->setElementsVal($channelValues);
$channelSelect->setSelected((string) intval($rule['channel_id']));

$probeLabels = array(_T("All probes", "reflex"));
$probeValues = array('0');
foreach ($probes as $row) {
    if (!is_array($row)) {
        continue;
    }
    $probeId = intval($row['id'] ?? 0);
    if ($probeId <= 0) {
        continue;
    }
    // get_probes answers is_builtin: a shipped name is translated, a name typed
    // by an operator is offered as he wrote it.
    $probeLabels[] = $safe(ReflexHelper::productText(
        $row['label'] ?? '', !empty($row['is_builtin'])));
    $probeValues[] = (string) $probeId;
}
$probeSelect = new SelectItem('probe_id');
$probeSelect->setElements($probeLabels);
$probeSelect->setElementsVal($probeValues);
$probeSelect->setSelected((string) intval($rule['probe_id']));

$severityLabels = array();
$severityValues = array();
foreach ($severityOptions as $value => $label) {
    $severityLabels[] = $label;
    $severityValues[] = (string) $value;
}
$severitySelect = new SelectItem('min_severity');
$severitySelect->setElements($severityLabels);
$severitySelect->setElementsVal($severityValues);
$severitySelect->setSelected((string) $rule['min_severity']);

$enabledCb = new CheckboxTpl('enabled');

$form = new ValidatingForm(array('method' => 'POST'));

// --- What triggers the rule ----------------------------------------------
$form->add(new SpanElement(_T("Trigger", "reflex"), "section-title"));
$form->push(new Table());
$form->add(new TrFormElement(_T("Channel", "reflex"), $channelSelect));
$form->add(new TrFormElement(_T("Probe", "reflex"), new multifieldTpl(array(
    $probeSelect,
    new textTpl('<i class="reflex-inherit-hint">'
        . htmlspecialchars(_T("Restrict the rule to a single probe, or leave it on all probes.", "reflex"))
        . '</i>')
))));
$form->add(new TrFormElement(_T("Minimum severity", "reflex"), $severitySelect));
$form->add(
    new TrFormElement(_T("Rule enabled", "reflex"), $enabledCb),
    array("value" => !empty($rule['enabled']) ? "checked" : "")
);
$form->pop();

// --- Who receives ---------------------------------------------------------
$form->add(new SpanElement(_T("Recipients", "reflex"), "section-title"));
$form->push(new Table());
$recipientsTpl = new TextareaTpl('recipients');
$recipientsTpl->setRows(5);
$recipientsTpl->setCols(40);
$form->add(
    new TrFormElement(_T("Recipients", "reflex"), new multifieldTpl(array(
        $recipientsTpl,
        new textTpl(ReflexDynamicForm::recipientsImport('recipients'))
    )), (($refusedField ?? '') === 'recipients') ? array('class' => 'reflex-invalid-row') : array()),
    // Stored as "a, b": shown one per line, the form the import writes.
    array("value" => array($safe(str_replace(', ', "\n", (string) ($rule['recipients'] ?? '')))),
          "required" => true)
);
$form->add(new TrFormElement('', new textTpl(
    '<i class="reflex-inherit-hint">'
    . htmlspecialchars(_T("One address per line.", "reflex"))
    . '</i>'
)));
// A closed list: with neither dyngroup nor GLPI answering there is nothing to
// restrict to, and the row is left out rather than shown empty.
if (!empty($targetFilterOptions)) {
    $filterChoices = array('' => _T("No restriction", "reflex")) + $targetFilterOptions;
    $filterSelect = new SelectItem('target_filter');
    // SelectItem prints its option labels and values verbatim.
    $filterSelect->setElements(array_map(
        array('ReflexDynamicForm', 'escapeForWidget'), array_values($filterChoices)));
    $filterSelect->setElementsVal(array_map(
        array('ReflexDynamicForm', 'escapeForWidget'), array_keys($filterChoices)));
    // A rule saved when the field was free text holds a value that names no group
    // and no entity: the neutral choice is preselected and the notice says so.
    $filterSelect->setSelected(isset($targetFilterOptions[$storedFilter]) ? $storedFilter : '');

    $filterHint = htmlspecialchars(
        _T("Limits the rule to the machines of one group or entity.", "reflex"));
    if ($storedFilter !== '' && !isset($targetFilterOptions[$storedFilter])) {
        $filterHint = sprintf(
            htmlspecialchars(_T("The restriction saved for this rule, '%s', matches no group and no entity.", "reflex")),
            $safe($storedFilter)
        );
    }
    $form->add(
        new TrFormElement(_T("Target restriction", "reflex"), new multifieldTpl(array(
            $filterSelect,
            new textTpl('<i class="reflex-inherit-hint">' . $filterHint . '</i>')
        )))
    );
}
$form->pop();

// --- How often ------------------------------------------------------------
$form->add(new SpanElement(_T("Sending rhythm", "reflex"), "section-title"));
$form->push(new Table());
$form->add(
    new TrFormElement(_T("Cooldown (minutes)", "reflex"), new multifieldTpl(array(
        new IntegerTpl('cooldown_minutes', '/^[0-9]{1,6}$/'),
        new textTpl('<i class="reflex-inherit-hint">'
            . htmlspecialchars(_T("Minimum delay before the same alert is sent again through this channel.", "reflex"))
            . '</i>')
    ))),
    array("value" => array((string) intval($rule['cooldown_minutes'])))
);
$escalation = ($rule['escalation_minutes'] === null || $rule['escalation_minutes'] === '')
    ? '' : (string) intval($rule['escalation_minutes']);
$form->add(
    new TrFormElement(_T("Escalation (minutes)", "reflex"), new multifieldTpl(array(
        new IntegerTpl('escalation_minutes', '/^([0-9]{1,6})?$/'),
        new textTpl('<i class="reflex-inherit-hint">'
            . htmlspecialchars(_T("Second send if a critical alert is still not acknowledged. Leave empty to disable escalation.", "reflex"))
            . '</i>')
    ))),
    array("value" => array($escalation))
);
$form->pop();

$form->add(new HiddenTpl('rule_id'), array("value" => (string) $ruleId, "hide" => true));

$form->addValidateButtonWithValue('bsave', _T("Save", "reflex"));
$form->addButton(
    'bcancel',
    _T("Cancel", "reflex"),
    "btnSecondary",
    "onclick=\"location.href='" . urlStrRedirect('reflex/reflex/settings', array('tab' => 'tabrules')) . "'; return false;\"",
    "button"
);

$form->display();
echo ReflexHelper::scriptTag('reflex.js', true);
