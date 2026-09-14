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
 * Reflex Module - Probe creation and modification
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : 0;
if ($probeId <= 0 && isset($_POST['probe_id'])) {
    $probeId = intval($_POST['probe_id']);
}
$login = reflex_current_login();
$isNew = ($probeId <= 0);
// Box a refusal points at, empty on every other rendering of the form.
$errorField = '';

$categoryOptions = ReflexHelper::categoryOptions();
$valueTypeOptions = ReflexHelper::valueTypeOptions();
$visibilityOptions = ReflexHelper::visibilityOptions();
$severityOptions = ReflexHelper::severityOptions();
// Asked for only when there are several: a single entity is sent silently,
// and an update keeps the one already stored.
$entityOptions = $isNew ? ReflexTargets::userEntityOptions($login) : array();
$entityChoice = (count($entityOptions) > 1);
$entityIds = array_keys($entityOptions);
$selectedEntity = $entityChoice ? '' : (string) reset($entityIds);

$probe = array(
    'label' => '',
    'description' => '',
    'category' => 'system',
    'unit' => '',
    'value_type' => 'numeric',
    'probe_type' => 'script',
    'command_unix' => '',
    'command_windows' => '',
    'visibility' => ReflexHelper::DEFAULT_VISIBILITY
);
$conditions = array();

if (!$isNew) {
    $detail = xmlrpc_reflex_get_probe($login, $probeId);
    if (is_array($detail) && isset($detail['probe']) && is_array($detail['probe'])) {
        $probe = array_merge($probe, $detail['probe']);
        $conditions = (isset($detail['conditions']) && is_array($detail['conditions'])) ? $detail['conditions'] : array();
    } else {
        $probe = null;
    }
}

// A visibility no longer offered would render as the first option and turn
// the probe private without saying so.
if (is_array($probe) && !isset($visibilityOptions[(string) $probe['visibility']])) {
    $probe['visibility'] = ReflexHelper::DEFAULT_VISIBILITY;
}

// A duplicated shipped probe keeps its native measure: it has no command.
$isScript = !is_array($probe) || (string) ($probe['probe_type'] ?? 'script') !== 'builtin';
// One condition fits the "Alert if" line; several keep the condition rows.
$rowsMode = !$isScript || (isset($_POST['bsave'])
    ? (($_POST['condition_mode'] ?? '') === 'rows')
    : count($conditions) > 1);
$storedValueType = is_array($probe) ? (string) $probe['value_type'] : 'numeric';

$alert = array('choice' => 'gt', 'value' => '', 'value2' => '', 'severity' => 'medium',
               'duration' => 0, 'message' => '', 'enabled' => 1, 'id' => 0);
if (!$rowsMode && count($conditions) === 1) {
    $alert = ReflexDynamicForm::alertFromCondition(reset($conditions), $storedValueType);
}

if (isset($_POST['bsave'])) {
    verifyCSRFToken($_POST);

    $payload = array(
        'label' => trim((string) ($_POST['label'] ?? '')),
        'description' => trim((string) ($_POST['description'] ?? '')),
        'category' => (string) ($_POST['category'] ?? 'system'),
        'unit' => $isScript ? trim((string) ($_POST['unit'] ?? '')) : (string) ($probe['unit'] ?? ''),
        'value_type' => $storedValueType,
        'visibility' => (string) ($_POST['visibility'] ?? ReflexHelper::DEFAULT_VISIBILITY),
        'enabled' => 1
    );
    if ($isScript) {
        // Only the CRLF a browser puts in a textarea is undone: sh would read the
        // carriage return as part of the command.
        foreach (array('command_unix', 'command_windows') as $commandField) {
            $payload[$commandField] = str_replace("\r\n", "\n", (string) ($_POST[$commandField] ?? ''));
        }
    }

    $alertBuilt = null;
    if (!$rowsMode) {
        $alert = ReflexDynamicForm::alertFromPost();
        $alertBuilt = ReflexDynamicForm::alertCondition($alert, $isNew ? null : $storedValueType);
        $payload['value_type'] = $alertBuilt['value_type'];
    }

    $entityKey = null;
    if ($isNew) {
        if ($entityChoice) {
            $selectedEntity = (string) ($_POST['entity_id'] ?? '');
        }
        // The root entity is 0: identifier() answers null for the neutral entry of
        // the select and 0 for the root, which intval() could not tell apart.
        $entityKey = ReflexTargets::identifier($selectedEntity);
        if ($entityKey !== null) {
            $payload['entity_id'] = $entityKey;
        }
    }

    // Same convention as a condition the server refuses.
    $error = '';
    if ($payload['label'] === '') {
        $error = _T("The probe name is required", "reflex");
        $errorField = 'label';
    } elseif ($isScript && trim($payload['command_unix']) === '' && trim($payload['command_windows']) === '') {
        $error = _T("Enter a command for at least one system", "reflex");
        $errorField = 'command_unix';
    } elseif ($alertBuilt !== null && $alertBuilt['error'] !== '') {
        $error = $alertBuilt['error'];
        $errorField = $alertBuilt['field'];
    } elseif (!isset($categoryOptions[$payload['category']])) {
        $error = _T("Unknown category", "reflex");
        $errorField = 'category';
    } elseif (!isset($valueTypeOptions[$payload['value_type']])) {
        $error = _T("Unknown value type", "reflex");
        $errorField = $rowsMode ? '' : 'alert_when';
    } elseif (!isset($visibilityOptions[$payload['visibility']])) {
        $error = _T("Unknown visibility", "reflex");
        $errorField = 'visibility';
    } elseif ($isNew && $entityChoice
            && ($entityKey === null || !isset($entityOptions[$entityKey]))) {
        $error = _T("Choose the entity the probe belongs to", "reflex");
        $errorField = 'entity_id';
    }

    $collectedConditions = $rowsMode
        ? ReflexDynamicForm::collectConditions($payload['value_type'])
        : (($alertBuilt !== null && $alertBuilt['condition'] !== null) ? array($alertBuilt['condition']) : array());

    // A refused condition is pointed at on the alert line, which has no rank.
    $conditionFailure = function ($refusal, $fallback) use ($rowsMode, &$errorField) {
        if (!$rowsMode && is_array($refusal)) {
            $errorField = ReflexDynamicForm::alertField($refusal['field']);
            $refusal['condition'] = 0;
        }
        return ReflexHelper::refusalMessage($refusal, $fallback);
    };

    if ($error !== '') {
        // Same naming as a refusal answered by the server.
        $message = htmlspecialchars($error, ENT_QUOTES, 'UTF-8');
        if ($errorField !== '') {
            $message .= '<br/>' . sprintf(
                htmlspecialchars(_T("Field concerned: %s", "reflex"), ENT_QUOTES, 'UTF-8'),
                htmlspecialchars(ReflexHelper::refusalFieldLabel($errorField), ENT_QUOTES, 'UTF-8'));
        }
        new NotifyWidgetFailure($message);
        // What was typed stays on screen.
        if (is_array($probe)) {
            $probe = array_merge($probe, $payload);
            $conditions = $collectedConditions;
        }
    } else {
        // Sentence used when the server refused without saying why.
        $refusedFallback = _T("The server refused these alert conditions.", "reflex");

        // $sent is what actually left: the create call carries the conditions
        // in a payload of its own, the update one in $payload itself.
        $applyRefusal = function ($answer, $fallback, $sent) use (
            $conditionFailure, $refusedFallback, $rowsMode, $collectedConditions,
            &$errorField, &$probe, &$conditions
        ) {
            $refusal = ReflexHelper::callRefusal($answer);
            if (intval($refusal['condition']) > 0) {
                new NotifyWidgetFailure($conditionFailure($refusal, $refusedFallback));
            } else {
                new NotifyWidgetFailure(ReflexHelper::refusalMessage($refusal, $fallback));
                $errorField = ($refusal['field'] === 'value_type' && !$rowsMode) ? 'alert_when' : $refusal['field'];
                $refusal = null;
            }
            if (is_array($probe)) {
                $probe = array_merge($probe, $sent);
                $conditions = $collectedConditions;
            }
            return $refusal;
        };

        if ($isNew) {
            // Written in one call, all or nothing.
            $createPayload = $payload;
            if (!empty($collectedConditions)) {
                $createPayload['conditions'] = $collectedConditions;
            }
            $created = xmlrpc_reflex_create_probe($login, $createPayload);
            // A refusal answers a structure, which is true in PHP: only the identifier
            // says the probe exists.
            $probeId = ReflexHelper::createdId($created);
            if ($probeId > 0) {
                new NotifyWidgetSuccess(_T("Probe created", "reflex"));
                header("Location: " . urlStrRedirect("reflex/reflex/probeDetail", array("probe_id" => $probeId)));
                exit;
            }
            $onCondition = $applyRefusal(
                $created, _T("Failed to create the probe", "reflex"), $payload);
            if ($onCondition !== null) {
                $conditionRefusal = $onCondition;
            }
        } else {
            // Written in one call, all or nothing.
            $payload['conditions'] = $collectedConditions;
            $result = xmlrpc_reflex_update_probe($login, $probeId, $payload);
            if ($result === true || $result === 1) {
                new NotifyWidgetSuccess(_T("Probe updated", "reflex"));
                header("Location: " . urlStrRedirect("reflex/reflex/probeDetail", array("probe_id" => $probeId)));
                exit;
            }
            $onCondition = $applyRefusal(
                $result, _T("Failed to update the probe", "reflex"), $payload);
            if ($onCondition !== null) {
                $conditionRefusal = $onCondition;
            }
        }
    }
}

$p = new PageGenerator($isNew ? _T("New probe", 'reflex') : _T("Edit probe", 'reflex'));
$p->setSideMenu($sidemenu);
$p->display();

if (!$isNew && $probe === null) {
    EmptyStateBox::show(
        _T("Probe not found", "reflex"),
        _T("This probe does not exist any more or you are not allowed to edit it.", "reflex")
    );
    return;
}

if (!$isNew && !empty($probe['is_builtin'])) {
    EmptyStateBox::show(
        _T("Built-in probe", "reflex"),
        _T("Duplicate this probe to obtain an editable variant.", "reflex")
    );
    return;
}

// Mark of the refused box: the notification says what is wrong, the outline
// says where.
$invalidMark = function ($field) use ($errorField) {
    return ($field === $errorField)
        ? ' style="' . ReflexDynamicForm::INVALID_MARK_STYLE . '"' : '';
};
$invalidAttrs = function ($field) use ($errorField) {
    return ($field === $errorField)
        ? array('style' => ReflexDynamicForm::INVALID_MARK_STYLE) : array();
};

$alertChoices = ReflexDynamicForm::alertChoices();
$alertValues = isset($alertChoices[$alert['choice']]) ? $alertChoices[$alert['choice']][1] : 1;

// Options are folded, but never over something filled or refused.
$optionFields = array('category', 'description', 'unit', 'visibility',
                      'alert_severity', 'alert_duration', 'alert_message');
$optionsOpen = in_array($errorField, $optionFields, true)
    || (string) $probe['category'] !== 'system'
    || trim((string) ($probe['description'] ?? '')) !== ''
    || trim((string) ($probe['unit'] ?? '')) !== ''
    || (string) $probe['visibility'] !== (string) ReflexHelper::DEFAULT_VISIBILITY
    || (!$rowsMode && ($alert['severity'] !== 'medium' || intval($alert['duration']) !== 0
                       || $alert['message'] !== ''));
?>

<a href="<?php echo urlStrRedirect('reflex/reflex/probes'); ?>" class="back-link">
    &larr; <?php echo _T("Back to probes list", "reflex"); ?>
</a>

<?php ReflexDynamicForm::catalog(); ?>

<div class="reflex-probe-layout">
<form class="mmc-form reflex-form reflex-probe-form" method="post" action="">
    <input type="hidden" name="auth_token" value="<?php echo htmlspecialchars($_SESSION['auth_token'] ?? ''); ?>" />
    <input type="hidden" name="probe_id" value="<?php echo $probeId; ?>" />
    <input type="hidden" name="condition_mode" value="<?php echo $rowsMode ? 'rows' : 'simple'; ?>" />

    <span class="section-title"><?php echo _T("Probe", "reflex"); ?></span>
    <div class="reflex-field">
        <label for="label"><?php echo _T("Name", "reflex"); ?> *</label>
        <input type="text" id="label" name="label" maxlength="255"<?php echo $invalidMark('label'); ?>
               value="<?php echo htmlspecialchars($probe['label']); ?>" />
    </div>
    <?php if ($isNew && $entityChoice): ?>
    <div class="reflex-field">
        <label for="entity_id"><?php echo _T("Entity", "reflex"); ?></label>
        <?php ReflexDynamicForm::optionSelect('entity_id', $entityOptions, $selectedEntity,
            $invalidAttrs('entity_id')); ?>
    </div>
    <?php endif; ?>

    <span class="section-title"><?php echo _T("Command", "reflex"); ?></span>
    <?php if ($isScript):
        $commandsMark = in_array($errorField, array('command_unix', 'command_windows'), true)
            ? ' style="' . ReflexDynamicForm::INVALID_MARK_STYLE . '"' : '';
    ?>
    <div class="reflex-commands"<?php echo $commandsMark; ?>>
        <div class="reflex-field">
            <label for="command_unix"><?php echo _T("Linux and macOS", "reflex"); ?></label>
            <textarea id="command_unix" name="command_unix" rows="4" class="reflex-command" wrap="soft"
                      spellcheck="false" autocomplete="off"><?php echo htmlspecialchars((string) ($probe['command_unix'] ?? ''), ENT_QUOTES, 'UTF-8'); ?></textarea>
            <?php echo ReflexDynamicForm::commandImport('command_unix', _T("Linux and macOS", "reflex")); ?>
        </div>
        <div class="reflex-field">
            <label for="command_windows"><?php echo _T("Windows", "reflex"); ?></label>
            <textarea id="command_windows" name="command_windows" rows="4" class="reflex-command" wrap="soft"
                      spellcheck="false" autocomplete="off"><?php echo htmlspecialchars((string) ($probe['command_windows'] ?? ''), ENT_QUOTES, 'UTF-8'); ?></textarea>
            <?php echo ReflexDynamicForm::commandImport('command_windows', _T("Windows", "reflex")); ?>
        </div>
    </div>
    <?php else: ?>
    <div class="reflex-field">
        <span class="reflex-field-caption"><?php echo _T("Measure", "reflex"); ?></span>
        <span><?php echo _T("native Medulla", "reflex"); ?></span>
    </div>
    <?php endif; ?>

    <span class="section-title"><?php echo _T("Alert", "reflex"); ?></span>
    <?php if (!$rowsMode): ?>
    <div class="reflex-field">
        <label for="alert_when"><?php echo _T("Alert if the result", "reflex"); ?></label>
        <div class="reflex-alert-line">
            <input type="hidden" name="alert_condition_id" value="<?php echo intval($alert['id']); ?>" />
            <input type="hidden" name="alert_enabled" value="<?php echo empty($alert['enabled']) ? '0' : '1'; ?>" />
            <select class="mmc-select" id="alert_when" name="alert_when" data-reflex-alert<?php echo $invalidMark('alert_when'); ?>>
                <?php foreach ($alertChoices as $choiceKey => $choice): ?>
                <option value="<?php echo htmlspecialchars($choiceKey); ?>"
                        data-reflex-values="<?php echo intval($choice[1]); ?>"
                        data-reflex-numeric="<?php echo $choice[2] ? '1' : '0'; ?>"
                        <?php echo ($alert['choice'] === $choiceKey) ? 'selected="selected"' : ''; ?>><?php echo htmlspecialchars($choice[0]); ?></option>
                <?php endforeach; ?>
            </select>
            <span class="reflex-alert-value<?php echo ($alertValues < 1) ? ' reflex-hidden' : ''; ?>" data-reflex-alert-value>
                <input type="text" name="alert_value" aria-label="<?php echo htmlspecialchars(_T("Alert if the result", "reflex")); ?>"<?php echo $invalidMark('alert_value'); ?>
                       value="<?php echo htmlspecialchars((string) $alert['value']); ?>" />
            </span>
            <span class="reflex-alert-value<?php echo ($alertValues < 2) ? ' reflex-hidden' : ''; ?>" data-reflex-alert-value2>
                <span class="reflex-alert-and"><?php echo _T("and", "reflex"); ?></span>
                <input type="text" name="alert_value2" aria-label="<?php echo htmlspecialchars(_T("and", "reflex")); ?>"<?php echo $invalidMark('alert_value2'); ?>
                       value="<?php echo htmlspecialchars((string) $alert['value2']); ?>" />
            </span>
        </div>
    </div>
    <?php else:
        ReflexDynamicForm::conditionRows($conditions, array(
            'containerId' => 'reflex-conditions',
            'valueType' => $probe['value_type'],
            'unit' => $probe['unit'] ?? '',
            'invalid' => isset($conditionRefusal) ? $conditionRefusal : array()
        ));
    endif; ?>

    <details class="reflex-options"<?php echo $optionsOpen ? ' open' : ''; ?>>
        <summary><span class="section-title"><?php echo _T("Options", "reflex"); ?></span></summary>
        <div class="reflex-form-grid">
            <div class="reflex-field">
                <label for="category"><?php echo _T("Category", "reflex"); ?></label>
                <?php ReflexDynamicForm::optionSelect('category', $categoryOptions, $probe['category'],
                    $invalidAttrs('category')); ?>
            </div>
            <?php if ($isScript): ?>
            <div class="reflex-field" data-reflex-numeric-only>
                <label for="unit"><?php echo _T("Unit", "reflex"); ?></label>
                <input type="text" id="unit" name="unit" maxlength="32" data-reflex-unit-field<?php echo $invalidMark('unit'); ?>
                       value="<?php echo htmlspecialchars($probe['unit'] ?? ''); ?>" />
                <span class="reflex-help"><?php echo _T("Optional, for a number", "reflex"); ?></span>
            </div>
            <?php endif; ?>
            <?php if (!$rowsMode): ?>
            <div class="reflex-field">
                <label for="alert_severity"><?php echo _T("Severity", "reflex"); ?></label>
                <?php ReflexDynamicForm::optionSelect('alert_severity', $severityOptions, $alert['severity'],
                    $invalidAttrs('alert_severity')); ?>
            </div>
            <div class="reflex-field">
                <label for="alert_duration"><?php echo _T("Duration", "reflex"); ?></label>
                <?php ReflexDynamicForm::optionSelect('alert_duration',
                    ReflexDynamicForm::durationChoices($alert['duration']), $alert['duration'],
                    $invalidAttrs('alert_duration')); ?>
            </div>
            <div class="reflex-field reflex-field-wide">
                <label for="alert_message"><?php echo _T("Alert message", "reflex"); ?></label>
                <input type="text" id="alert_message" name="alert_message" maxlength="512"<?php echo $invalidMark('alert_message'); ?>
                       value="<?php echo htmlspecialchars((string) $alert['message']); ?>" />
            </div>
            <?php endif; ?>
            <div class="reflex-field reflex-field-wide">
                <label for="description"><?php echo _T("Description", "reflex"); ?></label>
                <textarea id="description" name="description" rows="2"<?php echo $invalidMark('description'); ?>><?php echo htmlspecialchars($probe['description'] ?? ''); ?></textarea>
            </div>
            <div class="reflex-field">
                <label for="visibility"><?php echo _T("Visibility", "reflex"); ?></label>
                <?php ReflexDynamicForm::optionSelect('visibility', $visibilityOptions, $probe['visibility'],
                    $invalidAttrs('visibility'));
                // Passed raw: entity 0 is the root and null is no entity, a difference
                // intval() would flatten.
                $hintEntity = $isNew ? $selectedEntity : ($probe['entity_id'] ?? null);
                foreach (array_keys($visibilityOptions) as $visibilityValue) {
                    $hint = ReflexHelper::visibilityHint($visibilityValue, $hintEntity);
                    if ($hint === '') {
                        continue;
                    }
                    $hidden = ((string) $visibilityValue !== (string) $probe['visibility']) ? ' reflex-hidden' : '';
                    echo '<span class="reflex-help' . $hidden . '" data-reflex-hint-for="#visibility"'
                        . ' data-reflex-hint-value="' . htmlspecialchars((string) $visibilityValue, ENT_QUOTES, 'UTF-8') . '">'
                        . htmlspecialchars($hint, ENT_QUOTES, 'UTF-8') . '</span>';
                }
                ?>
            </div>
        </div>
    </details>

    <div class="reflex-toolbar">
        <input type="submit" name="bsave" class="btnPrimary" value="<?php echo _T("Save", "reflex"); ?>" />
        <input type="button" class="btnSecondary" value="<?php echo _T("Cancel", "reflex"); ?>"
               onclick="location.href='<?php echo urlStrRedirect('reflex/reflex/probes'); ?>';" />
    </div>
</form>
<?php if ($isNew):
    $templates = ReflexDynamicForm::probeTemplates();
    $templateFlags = JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT;
?>
<aside class="reflex-templates">
    <div class="reflex-templates-heading"><?php echo _T("Templates", "reflex"); ?></div>
    <?php foreach ($templates as $templateIndex => $template):
        // Written as the "Alert when" column of the probe list writes it.
        $templateAlert = ReflexDynamicForm::alertCondition(array(
            'choice' => $template['alert_when'], 'value' => $template['alert_value'], 'value2' => '',
            'severity' => 'medium', 'duration' => 0, 'message' => '', 'id' => 0));
        $templateSummary = ($templateAlert['condition'] !== null)
            ? ReflexHelper::describeConditionText($templateAlert['condition'], $template['unit'],
                                                  $templateAlert['value_type'], true)
            : '';
    ?>
    <button type="button" class="reflex-template" data-reflex-template="<?php echo intval($templateIndex); ?>">
        <span class="reflex-template-name"><?php echo htmlspecialchars($template['name']); ?></span>
        <span class="reflex-template-alert"><?php echo htmlspecialchars($templateSummary); ?></span>
    </button>
    <?php endforeach; ?>
    <script type="application/json" id="reflex-probe-templates"><?php echo json_encode(array(
        'defaults' => array('category' => 'system'),
        'templates' => $templates
    ), $templateFlags); ?></script>
</aside>
<?php endif; ?>
</div>
