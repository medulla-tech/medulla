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
 * Reflex Module - Adapt one alert condition
 *
 * The operator is shown but never submitted: changing it changes the nature
 * of the condition, and duplicating the probe is the way to obtain another.
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

$conditionId = isset($_GET['condition_id'])
    ? intval($_GET['condition_id'])
    : intval($_POST['condition_id'] ?? 0);
$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$login = reflex_current_login();
// The root entity is 0: identifier() keeps it apart from an absent choice.
$entityId = ReflexTargets::identifier($_GET['entity_id'] ?? ($_POST['entity_id'] ?? null));
$entityParam = ($entityId === null) ? '' : (string) $entityId;

$detail = ($probeId > 0) ? xmlrpc_reflex_get_probe($login, $probeId, $entityParam) : null;
$probe = (is_array($detail) && isset($detail['probe']) && is_array($detail['probe']))
    ? $detail['probe'] : array();
$conditions = (is_array($detail) && isset($detail['conditions']) && is_array($detail['conditions']))
    ? $detail['conditions'] : array();

$condition = null;
foreach ($conditions as $row) {
    if (is_array($row) && intval($row['id'] ?? 0) === $conditionId && $conditionId > 0) {
        $condition = $row;
        break;
    }
}

if (empty($probe) || $condition === null) {
    $f = new PopupForm(_T("Adapt Condition", "reflex"));
    $f->addText(htmlspecialchars(_T("This condition does not exist any more, or the probe is not shared with you.", "reflex")));
    $f->addCancelButton("bback");
    $f->display();
    return;
}

$unitText = ReflexHelper::unitLabel($probe['unit'] ?? '');
// Only a probe of the catalog ships values to compare with or go back to.
$isBuiltin = !empty($probe['is_builtin']);
$valueType = strtolower((string) ($probe['value_type'] ?? 'numeric'));
$operator = strtolower((string) ($condition['operator'] ?? ''));
$severityOptions = ReflexHelper::severityOptions();

// Restoring clears the setting of the level this account writes, and nothing
// else: it is named as unavailable on any other level.
$canRestore = ($isBuiltin && ReflexHelper::conditionIsCustomized($condition));

$needsThreshold = !in_array($operator, ReflexDynamicForm::thresholdlessOperators(), true);
$needsUpperBound = $needsThreshold && ($valueType === 'numeric')
    && in_array($operator, ReflexDynamicForm::rangeOperators(), true);

// Same decision as the probe form, so a condition reads back as written.
$thresholdField = '';
if ($needsThreshold) {
    if ($valueType === 'text') {
        $thresholdField = 'threshold_text';
    } else {
        $thresholdField = 'threshold_value';
    }
}

// Empty when the condition compares to nothing. The script reads it to catch
// an empty box before the round trip.
$thresholdInput = '';
if ($thresholdField === 'threshold_text') {
    $thresholdInput = 'condition_threshold_text';
} elseif ($thresholdField === 'threshold_value') {
    $thresholdInput = ($valueType === 'boolean')
        ? 'condition_threshold_bool' : 'condition_threshold_value';
}

// An empty box is never a value: left out of the payload it would silently
// restore the shipped threshold. One sentence for the script and the POST
// handler, so one mistake never reads as two refusals.
$emptyThresholdSentence = '';
if ($thresholdField === 'threshold_text') {
    $emptyThresholdSentence = _T("This condition compares a text: the value cannot be left empty.", "reflex");
} elseif ($thresholdField === 'threshold_value') {
    $emptyThresholdSentence = ($valueType === 'boolean')
        ? _T("This condition compares a state: choose the one it alerts on.", "reflex")
        : _T("This condition compares a threshold: the value cannot be left empty.", "reflex");
}
if ($emptyThresholdSentence !== '' && $canRestore) {
    $emptyThresholdSentence .= ' ' . sprintf(
        _T("To go back to the shipped value, use the %s button.", "reflex"),
        _T("Restore shipped values", "reflex"));
}

// Back on the entity whose condition was just adapted, and not on another:
// the sheet reads the settings of one entity at a time.
$redirectParams = array("probe_id" => $probeId);
if ($entityParam !== '') {
    $redirectParams["entity_id"] = $entityParam;
}
$redirect = urlStrRedirect("reflex/reflex/probeDetail", $redirectParams);

// The popup posts itself through the script below, so a refusal comes back
// inside it. Without the script it posts the ordinary way and the refusal
// lands on the sheet behind.
$isScripted = isset($_SERVER['HTTP_X_REQUESTED_WITH'])
    && strtolower((string) $_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest';

// Set when a write was refused: the form is rebuilt from the POST.
$refusalText = '';
$refusedField = '';
$replay = false;

// A redirect answered to the script would pull a whole page into the popup,
// so the address travels as a header and the browser leaves on its own.
$leave = function ($url) use ($isScripted) {
    if ($isScripted) {
        header("X-Reflex-Redirect: " . $url);
        header("Content-Type: text/plain; charset=UTF-8");
        exit;
    }
    header("Location: " . $url);
    exit;
};

// A box the framework renders read only posts a hidden field holding 'off':
// the presence of the field is not the state, the value is.
$checkboxOn = function ($name) {
    if (!isset($_POST[$name])) {
        return false;
    }
    $value = strtolower(trim((string) $_POST[$name]));
    return !in_array($value, array('', '0', 'off', 'false', 'no'), true);
};

// Shaped like a refusal answered by the server, so the same mistake does not
// read differently depending on which side judged it.
$fieldRefusal = function ($sentence, $field) {
    $message = htmlspecialchars($sentence, ENT_QUOTES, 'UTF-8');
    if ($field !== '') {
        $message .= '<br/>' . sprintf(
            htmlspecialchars(_T("Field concerned: %s", "reflex"), ENT_QUOTES, 'UTF-8'),
            htmlspecialchars(ReflexHelper::refusalFieldLabel($field), ENT_QUOTES, 'UTF-8'));
    }
    return $message;
};

// -----------------------------------------------------------------------------
// Back to what the product ships
// -----------------------------------------------------------------------------
if (isset($_POST['breset'])) {
    verifyCSRFToken($_POST);

    if ($canRestore) {
        $refusal = ReflexHelper::callRefusal(
            xmlrpc_reflex_reset_condition_override($login, $conditionId, $entityParam));
        if ($refusal === null) {
            new NotifyWidgetSuccess(_T("Condition back to the shipped values", "reflex"));
            $leave($redirect);
        }

        $refusalText = ReflexHelper::refusalMessage(
            $refusal,
            _T("Failed to restore the shipped values of this condition.", "reflex"));
        $refusedField = (string) $refusal['field'];
    }
    if (!$isScripted) {
        new NotifyWidgetFailure($refusalText);
        header("Location: " . $redirect);
        exit;
    }
}

// -----------------------------------------------------------------------------
// Save the adaptation
// -----------------------------------------------------------------------------
if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $submitted = array(
        'duration_seconds' => intval($_POST['condition_duration'] ?? 0),
        'severity' => (string) ($_POST['condition_severity'] ?? 'medium'),
        'message_template' => trim((string) ($_POST['condition_message'] ?? '')),
        'enabled' => $checkboxOn('condition_enabled') ? 1 : 0
    );

    if ($thresholdField === 'threshold_text') {
        $raw = trim((string) ($_POST['condition_threshold_text'] ?? ''));
        $submitted['threshold_text'] = ($raw === '') ? null : $raw;
    } elseif ($thresholdField === 'threshold_value') {
        if ($valueType === 'boolean') {
            $raw = trim((string) ($_POST['condition_threshold_bool'] ?? ''));
            // Text, like every threshold: see ReflexHelper::thresholdText().
            $submitted['threshold_value'] = ($raw === '') ? null : (($raw === '1') ? '1' : '0');
        } else {
            $raw = trim((string) ($_POST['condition_threshold_value'] ?? ''));
            // Never a float on the wire, the locale would decide its decimal separator.
            $submitted['threshold_value'] = ReflexHelper::thresholdText($raw);
        }
        if ($needsUpperBound) {
            $raw2 = trim((string) ($_POST['condition_threshold_value2'] ?? ''));
            $submitted['threshold_value2'] = ReflexHelper::thresholdText($raw2);
        }
    }

    // Every refusal names the box it is about, as the probe form does.
    $error = '';
    $errorField = '';
    if (!isset($severityOptions[$submitted['severity']])) {
        $error = _T("Unknown severity", "reflex");
        $errorField = 'severity';
    } elseif ($submitted['duration_seconds'] < 0) {
        $error = _T("The duration cannot be negative", "reflex");
        $errorField = 'duration_seconds';
    } elseif ((function_exists('mb_strlen')
        ? mb_strlen($submitted['message_template'], 'UTF-8')
        : strlen($submitted['message_template'])) > 512) {
        $error = _T("The alert message is limited to 512 characters", "reflex");
        $errorField = 'message_template';
    } elseif ($thresholdField !== '' && $submitted[$thresholdField] === null) {
        $error = $emptyThresholdSentence;
        $errorField = $thresholdField;
    } elseif ($needsUpperBound
        && (!isset($submitted['threshold_value2']) || $submitted['threshold_value2'] === null)) {
        $error = _T("This condition compares two bounds: the upper one is required", "reflex");
        $errorField = 'threshold_value2';
    } elseif ($needsUpperBound
        && $submitted['threshold_value2'] < $submitted['threshold_value']) {
        $error = _T("The upper bound must not be below the threshold", "reflex");
        $errorField = 'threshold_value2';
    }

    if ($error !== '') {
        $refusalText = $fieldRefusal($error, $errorField);
        $refusedField = $errorField;
        if (!$isScripted) {
            new NotifyWidgetFailure($refusalText);
            header("Location: " . $redirect);
            exit;
        }
        // Put back from the POST: reloading would restore the stored values and the
        // correction would have to be typed twice.
        $replay = true;
    }

    if (!$replay) {
        // Judged against the level just above the one being written: for the instance
        // that is the product, for an entity the setting of the instance. Omitting a
        // field clears it at the level being written.
        $overrides = array();
        foreach ($submitted as $field => $value) {
            if (ReflexHelper::conditionHasDefault($condition, $field)
                && ReflexHelper::sameConditionValue($field, $value,
                                                    ReflexHelper::conditionDefault($condition, $field))) {
                continue;
            }
            if ($value === null && !ReflexHelper::conditionHasDefault($condition, $field)) {
                continue;
            }
            // An empty message follows the product: the server stores NULL anyway.
            if ($field === 'message_template' && $value === ''
                && ReflexHelper::conditionHasDefault($condition, $field)) {
                continue;
            }
            $overrides[$field] = $value;
        }

        $refusal = ReflexHelper::callRefusal(
            xmlrpc_reflex_set_condition_override($login, $conditionId, $overrides, $entityParam));
        if ($refusal === null) {
            if (!$isBuiltin) {
                new NotifyWidgetSuccess(_T("Condition saved", "reflex"));
            } else {
                new NotifyWidgetSuccess(empty($overrides)
                    ? _T("Condition back to the shipped values", "reflex")
                    : _T("Condition adapted", "reflex"));
            }
            $leave($redirect);
        }

        // The backend validates against the real operator and says which field it
        // refused: closing on a success would leave the change believed kept.
        $refusalText = ReflexHelper::refusalMessage(
            $refusal,
            $isBuiltin
                ? _T("The server refused this adaptation.", "reflex")
                : _T("The server refused this change.", "reflex"));
        $refusedField = (string) $refusal['field'];
        if (!$isScripted) {
            new NotifyWidgetFailure($refusalText);
            header("Location: " . $redirect);
            exit;
        }
        $replay = true;
    }
}

// -----------------------------------------------------------------------------
// Form
// -----------------------------------------------------------------------------
$effective = ReflexHelper::conditionEffectiveRow($condition);

// What was just typed when a refusal brought the popup back, what the
// condition holds otherwise.
$startValue = function ($name, $stored) use ($replay) {
    $value = ($replay && isset($_POST[$name])) ? trim((string) $_POST[$name]) : $stored;
    return ReflexDynamicForm::escapeForWidget($value);
};

$addRow = function ($form, $label, $tpl, $field, $value = null) use ($refusedField) {
    // InputTpl prints its own class attribute, so the mark is inline there;
    // SelectItem takes it through the class its style argument appends.
    $rowInfo = array();
    if ($field !== '' && $field === $refusedField) {
        if ($tpl instanceof TextareaTpl) {
            $rowInfo['class'] = 'reflex-invalid-row';
        } elseif ($tpl instanceof InputTpl) {
            $tpl->setAttributCustom(trim($tpl->getAttributCustom()
                . ' style="' . ReflexDynamicForm::INVALID_MARK_STYLE . '"'));
        } elseif ($tpl instanceof SelectItem) {
            $tpl->style = trim((string) $tpl->style . ' reflex-invalid-field');
        }
    }
    $form->add(
        new TrFormElement($label, $tpl, $rowInfo),
        ($value === null) ? array() : array("value" => $value)
    );
};

$f = new PopupForm($isBuiltin
    ? _T("Adapt Condition", "reflex")
    : _T("Edit Condition", "reflex"));
// Widened by the module stylesheet.
$f->setPopupClass('reflex-popup-form reflex-condition-popup');
$f->addText('<strong>' . ReflexHelper::safeProduct($probe['label'] ?? '', $isBuiltin) . '</strong>');

// Always emitted, even empty: the script writes into it, and its presence is
// how a refused write is told apart from a whole page. $refusalText is
// already escaped, by $fieldRefusal() or by refusalMessage().
$f->addText('<span class="reflex-popup-error" id="reflex-condition-error"'
    . (($refusalText === '') ? ' hidden' : '') . '>' . $refusalText . '</span>');

$f->add(new HiddenTpl("condition_id"), array("value" => $conditionId, "hide" => True));
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->add(new HiddenTpl("entity_id"), array("value" => $entityParam, "hide" => True));

$f->push(new Table());

$entityOptions = ReflexTargets::userEntityOptions($login);
if ($entityId !== null && count($entityOptions) > 1) {
    $entityName = isset($entityOptions[$entityId])
        ? $entityOptions[$entityId]
        : sprintf(_T("Entity %d", "reflex"), $entityId);
    $f->add(new TrFormElement(_T("Entity", "reflex"),
                              new textTpl(htmlspecialchars($entityName, ENT_QUOTES, 'UTF-8'))));
}

if ($thresholdField === 'threshold_text') {
    $addRow(
        $f,
        _T("Text value", "reflex"),
        new InputTpl('condition_threshold_text', '/^.*$/'),
        'threshold_text',
        $startValue('condition_threshold_text', $effective['threshold_text'] ?? '')
    );
} elseif ($thresholdField === 'threshold_value' && $valueType === 'boolean') {
    $boolValue = '';
    if (isset($effective['threshold_value']) && $effective['threshold_value'] !== null
        && $effective['threshold_value'] !== '') {
        $boolValue = (floatval($effective['threshold_value']) != 0) ? '1' : '0';
    }
    if ($replay) {
        $boolValue = (string) ($_POST['condition_threshold_bool'] ?? '');
        if (!in_array($boolValue, array('', '0', '1'), true)) {
            $boolValue = '';
        }
    }
    $boolSelect = new SelectItem('condition_threshold_bool');
    $boolSelect->setElements(array(
        _T("Not set", "reflex"),
        _T("Yes", "reflex"),
        _T("No", "reflex")
    ));
    $boolSelect->setElementsVal(array('', '1', '0'));
    $boolSelect->setSelected($boolValue);
    $addRow($f, _T("Threshold", "reflex"), $boolSelect, 'threshold_value');
} elseif ($thresholdField === 'threshold_value') {
    $thresholdLabel = ($unitText !== '')
        ? sprintf(_T("Threshold (%s)", "reflex"), htmlspecialchars($unitText))
        : _T("Threshold", "reflex");
    $addRow(
        $f,
        htmlspecialchars($thresholdLabel),
        new InputTpl('condition_threshold_value', '/^-?[0-9]*[.,]?[0-9]*$/'),
        'threshold_value',
        $startValue('condition_threshold_value',
                    ReflexHelper::plainNumber($effective['threshold_value'] ?? ''))
    );

    if ($needsUpperBound) {
        $addRow(
            $f,
            _T("Upper bound", "reflex"),
            new InputTpl('condition_threshold_value2', '/^-?[0-9]*[.,]?[0-9]*$/'),
            'threshold_value2',
            $startValue('condition_threshold_value2',
                        ReflexHelper::plainNumber($effective['threshold_value2'] ?? ''))
        );
    }
}

$addRow(
    $f,
    _T("Duration before alerting (seconds)", "reflex"),
    new IntegerTpl('condition_duration', '/^[0-9]*$/'),
    'duration_seconds',
    $startValue('condition_duration', intval($effective['duration_seconds'] ?? 0))
);

$severitySelect = new SelectItem('condition_severity');
$severitySelect->setElements(array_map(
    array('ReflexDynamicForm', 'escapeForWidget'), array_values($severityOptions)));
$severitySelect->setElementsVal(array_map(
    array('ReflexDynamicForm', 'escapeForWidget'), array_keys($severityOptions)));
$severityValue = (string) ($effective['severity'] ?? 'medium');
if ($replay && isset($severityOptions[(string) ($_POST['condition_severity'] ?? '')])) {
    $severityValue = (string) $_POST['condition_severity'];
}
$severitySelect->setSelected($severityValue);
$addRow($f, _T("Severity", "reflex"), $severitySelect, 'severity');

// Filled with the stored text, the box showed a sentence the operator never
// typed, in a language other than the hint.
$messageStored = (string) ($effective['message_template'] ?? '');
if (ReflexHelper::conditionHasDefault($condition, 'message_template')
    && ReflexHelper::sameConditionValue('message_template', $messageStored,
        ReflexHelper::conditionDefault($condition, 'message_template'))
    && $isBuiltin) {
    $messageStored = '';
}
$messageTpl = new TextareaTpl('condition_message');
$messageTpl->setRows(3);
$addRow(
    $f,
    _T("Alert message", "reflex"),
    $messageTpl,
    'message_template',
    $startValue('condition_message', $messageStored)
);

$enabledCb = new CheckboxTpl('condition_enabled');
$enabledCb->check($replay ? $checkboxOn('condition_enabled') : !empty($effective['enabled']));
$addRow(
    $f,
    _T("Condition active", "reflex"),
    new multifieldTpl(array(
        $enabledCb,
        new textTpl('<i class="reflex-inherit-hint">' . htmlspecialchars(
            _T("Switched off, this condition raises no alert any more. The probe goes on measuring.", "reflex"),
            ENT_QUOTES, 'UTF-8') . '</i>')
    )),
    'enabled'
);

$f->pop();


$f->addValidateButtonWithValue("bconfirm", _T("Save", "reflex"));
// Drawn as unavailable rather than dropped when the setting belongs to
// another level. Without the disabled attribute, which would swallow the
// reason: Chrome shows no title on a disabled control. Greyed inline so the
// hover rule cannot light it up again.
if ($canRestore) {
    $f->addButton("breset", _T("Restore shipped values", "reflex"), "btnSecondary");
}
$f->addCancelButton("bback");
$f->display();
?>
<script type="text/javascript">
// The popup posts itself instead of navigating away, so a refusal comes back
// as the form to correct with every value typed still in place. Without this
// script it posts the ordinary way and reads the refusal on the sheet behind.
(function () {
    var container = document.getElementById("__popup_container");
    var form = container ? container.querySelector("form") : null;
    var notice = document.getElementById("reflex-condition-error");
    if (!form || !notice || !window.jQuery) {
        return;
    }

    // Written as html, escaped server side by the same helper as a refusal
    // answered by the backend.
    var words = <?php echo json_encode(array(
        'saving' => _T("Saving...", "reflex"),
        'unreachable' => htmlspecialchars(
            _T("The server did not answer: nothing has been saved.", "reflex"),
            ENT_QUOTES, 'UTF-8'),
        'threshold' => ($emptyThresholdSentence === '')
            ? '' : $fieldRefusal($emptyThresholdSentence, $thresholdField)
    ), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;
    var thresholdName = <?php echo json_encode($thresholdInput,
        JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;

    var $form = jQuery(form);
    // A button an ACL already closed must not come back enabled.
    var buttons = $form.find("input[type=submit]").not("[disabled]");
    var save = buttons.filter("[name=bconfirm]");
    var saveLabel = save.val();
    var threshold = thresholdName ? form.elements[thresholdName] : null;
    // TextareaTpl carries no attribute of its own.
    if (form.elements.condition_message) {
        form.elements.condition_message.maxLength = 512;
    }
    var busy = false;
    // Submitting with the keyboard means the first button: the form carries a
    // verb either way.
    var pressed = "bconfirm";

    buttons.on("click", function () {
        pressed = this.name || pressed;
    });

    // The popup is the box that scrolls and it is placed fixed: scrollIntoView
    // would move the page behind it instead.
    function reveal(node) {
        var box = jQuery(node).closest(".popup")[0];
        if (!box) {
            return;
        }
        var boxRect = box.getBoundingClientRect();
        var nodeRect = node.getBoundingClientRect();
        if (nodeRect.top >= boxRect.top && nodeRect.bottom <= boxRect.bottom) {
            return;
        }
        box.scrollTop += nodeRect.top - boxRect.top - 12;
    }

    function report(html) {
        notice.innerHTML = html;
        notice.hidden = false;
        reveal(notice);
    }

    function working(state) {
        busy = state;
        buttons.prop("disabled", state);
        save.val(state ? words.saving : saveLabel);
    }

    // Deferred: the caller places the popup again just after inserting this
    // fragment, and measuring before that would aim at the wrong offset.
    if (!notice.hidden) {
        window.setTimeout(function () {
            reveal(notice);
        }, 0);
    }

    if (threshold) {
        jQuery(threshold).on("input change", function () {
            threshold.classList.remove("reflex-invalid-field");
            notice.hidden = true;
        });
    }

    $form.on("submit", function (event) {
        event.preventDefault();
        if (busy) {
            return false;
        }
        if (pressed === "bconfirm" && threshold
                && String(threshold.value).trim() === "" && words.threshold) {
            // Caught before the round trip; the server says the same sentence.
            report(words.threshold);
            threshold.classList.add("reflex-invalid-field");
            // Focusing scrolls the popup to the box, so the message is brought back last.
            threshold.focus();
            reveal(notice);
            return false;
        }
        notice.hidden = true;
        working(true);
        jQuery.ajax({
            url: form.getAttribute("action"),
            type: "POST",
            dataType: "html",
            data: $form.serialize() + "&" + encodeURIComponent(pressed) + "=1"
        }).done(function (html, status, xhr) {
            var leaving = xhr.getResponseHeader("X-Reflex-Redirect");
            if (leaving) {
                window.location.href = leaving;
                return;
            }
            if (String(html).indexOf("reflex-condition-error") === -1) {
                // Not the form coming back: an expired session, anything answered as a whole
                // page. The window is rebuilt instead.
                window.location.reload();
                return;
            }
            jQuery(container).html(html);
            // The form that comes back is not the height of the one that left.
            if (typeof _defaultPlacement === "function") {
                _defaultPlacement();
            }
        }).fail(function () {
            working(false);
            report(words.unreachable);
        });
        return false;
    });
})();
</script>
<?php
// Emitted with the fragment: a widget bound at load time never sees a popup.
echo ReflexTip::script();
?>
