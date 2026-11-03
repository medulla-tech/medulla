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
 * Reflex Module - Assign Probe Popup
 *
 * The target is picked from what the console already knows. A type whose list
 * comes back empty is not offered at all.
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$login = reflex_current_login();

// Field carrying the identifier, per target type. 'all' needs none.
$targetFields = array(
    'machine' => 'target_machine',
    'group' => 'target_group',
    'entity' => 'target_entity'
);

// Only machines take several targets; one group or one entity already
// designates a set.
$multiTargetTypes = array('machine' => true);

// A multiple select posts an array, under a name that is not the field name.
$targetInputNames = array();
foreach ($targetFields as $type => $field) {
    $targetInputNames[$type] = isset($multiTargetTypes[$type]) ? $field . '[]' : $field;
}

// Read first: a failed XML-RPC call poisons every later one in the request.
$detail = xmlrpc_reflex_get_probe($login, $probeId);
// Preselected cadence. The probe carries its own; with none, the form opens on
// the shortest cadence the list offers, which is what the column defaults to.
$defaultInterval = ReflexHelper::shortestInterval();
$minInterval = ReflexHelper::shortestInterval();
if (is_array($detail) && isset($detail['probe']) && is_array($detail['probe'])) {
    $defaultInterval = intval($detail['probe']['default_interval_seconds']
        ?? ReflexHelper::shortestInterval());
    $minInterval = intval($detail['probe']['min_interval_seconds']
        ?? ReflexHelper::shortestInterval());
}

// A probe carrying no collector is measured by no agent: the cadence decides
// nothing and is not asked for.
$collectorsResult = xmlrpc_reflex_get_probe_collectors($login, $probeId);
$collectorRows = array();
if (is_array($collectorsResult)) {
    $collectorRows = (isset($collectorsResult['data']) && is_array($collectorsResult['data']))
        ? $collectorsResult['data']
        : $collectorsResult;
}
$serverEvaluated = empty($collectorRows);

$targetOptions = array();
$targetTypeOptions = array();
foreach (ReflexHelper::targetTypeOptions() as $type => $label) {
    if ($type === 'all') {
        $targetTypeOptions[$type] = $label;
        continue;
    }
    $options = ReflexTargets::optionsFor($type);
    if (!empty($options)) {
        $targetOptions[$type] = $options;
        $targetTypeOptions[$type] = $label;
    }
}

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $targetType = (string) ($_POST['target_type'] ?? 'all');
    $targetIds = array();
    $interval = $serverEvaluated
        ? $defaultInterval
        : intval($_POST['interval_seconds'] ?? ReflexHelper::shortestInterval());

    // The alert mail is written in the language of whoever places the probe, read
    // from the session now because it is long gone when the substitute sends it.
    // No value means English to the backend.
    $language = $_SESSION['lang'] ?? null;

    $error = '';
    if (!isset($targetTypeOptions[$targetType])) {
        $error = _T("Unknown target type", "reflex");
    } elseif ($targetType === 'machine') {
        // Without a script the plain select still posts a single value.
        $submitted = $_POST[$targetFields['machine']] ?? array();
        if (!is_array($submitted)) {
            $submitted = array($submitted);
        }
        $wanted = array();
        foreach ($submitted as $raw) {
            $machineId = intval(trim((string) $raw));
            if ($machineId > 0) {
                // Keyed, so the same machine sent twice is placed once.
                $wanted[$machineId] = $machineId;
            }
        }
        if (empty($wanted)) {
            $error = _T("Choose at least one machine", "reflex");
        } else {
            // One registry round trip for the whole batch.
            ReflexTargets::preloadMachineNames($wanted);
            foreach ($wanted as $machineId) {
                // The picker only preloads a window of the estate and the search reaches
                // past it: each identifier is confirmed against the backend, which reapplies
                // the restrictions of the session. A single stranger fails the whole form.
                if (ReflexTargets::assignableMachineName($machineId) === '') {
                    $error = _T("Please pick a target in the list", "reflex");
                    $targetIds = array();
                    break;
                }
                $targetIds[] = (string) $machineId;
            }
        }
    } elseif ($targetType !== 'all') {
        // The root entity is offered under the identifier 0: intval() could not tell
        // it from the neutral first entry, so an empty value answers null here.
        $targetId = ReflexTargets::identifier($_POST[$targetFields[$targetType]] ?? '');
        if ($targetId === null || !isset($targetOptions[$targetType][$targetId])) {
            // Groups and entities are listed in full: a forged value never reaches the
            // backend.
            $error = _T("Please pick a target in the list", "reflex");
        } else {
            $targetIds[] = (string) $targetId;
        }
    }

    if ($serverEvaluated) {
        // Not a choice of the operator: a probe shipped below the floor is still
        // placed, at the value it carries.
        if ($interval <= 0) {
            $interval = ReflexHelper::shortestInterval();
        }
    } elseif ($error === '') {
        $error = ReflexDynamicForm::intervalRefusal($interval);
    }

    if ($error !== '') {
        new NotifyWidgetFailure($error);
    } elseif ($targetType === 'machine') {
        // One call for the batch: a loop could half succeed without saying so.
        $result = xmlrpc_reflex_assign_probe_bulk(
            $login, $probeId, $targetType, $targetIds, $interval, $language);
        $assigned = is_array($result) ? intval($result['assigned'] ?? 0) : 0;
        $rejected = is_array($result) ? intval($result['rejected'] ?? 0) : 0;
        if ($assigned <= 0) {
            // The batch answers its counters on a success and the refusal structure on a
            // refusal.
            new NotifyWidgetFailure(ReflexHelper::refusalMessage(
                ReflexHelper::callRefusal($result),
                _T("Failed to assign the probe", "reflex")));
        } else {
            $placed = ($assigned === 1)
                ? _T("Probe assigned on one machine.", "reflex")
                : sprintf(_T("Probe assigned on %d machines.", "reflex"), $assigned);
            if ($rejected > 0) {
                // A partial result is not a success.
                $refused = ($rejected === 1)
                    ? _T("One machine was refused.", "reflex")
                    : sprintf(_T("%d machines were refused.", "reflex"), $rejected);
                new NotifyWidgetWarning($placed . ' ' . $refused);
            } else {
                new NotifyWidgetSuccess($placed);
            }
        }
    } else {
        $targetId = isset($targetIds[0]) ? $targetIds[0] : '';
        $result = xmlrpc_reflex_assign_probe($login, $probeId, $targetType, $targetId, $interval, $language);
        if ($result === true || $result === 1 || (is_numeric($result) && intval($result) > 0)) {
            new NotifyWidgetSuccess(_T("Probe assigned", "reflex"));
        } else {
            new NotifyWidgetFailure(ReflexHelper::refusalMessage(
                ReflexHelper::callRefusal($result),
                _T("Failed to assign the probe", "reflex")));
        }
    }

    header("Location: " . urlStrRedirect("reflex/reflex/probeDetail", array("probe_id" => $probeId)));
    exit;
}

$typeSelect = new SelectItem('target_type');
$typeSelect->setElements(array_values($targetTypeOptions));
$typeSelect->setElementsVal(array_keys($targetTypeOptions));
$typeSelect->setSelected('all');

// Bounded server side; built only when an agent measures the probe.
$intervalSelect = null;
if (!$serverEvaluated) {
    $intervalSelect = ReflexDynamicForm::intervalSelect($minInterval, $defaultInterval);
}

$f = new PopupForm(_T("Assign Probe", "reflex"));
// Widened by the module stylesheet.
$f->setPopupClass('reflex-popup-form');
// Only said when the list is actually bounded, else the notice would be false.
if (isset($targetOptions['machine'])
        && safeCount($targetOptions['machine']) >= ReflexTargets::MACHINE_LIMIT) {
    $f->addText('<em>' . htmlspecialchars(
        _T("The machine list shows a part of the estate: type in the search field to reach any other machine.", "reflex")
    ) . '</em>');
}
if (isset($targetOptions['machine'])) {
    $f->addText('<em>' . htmlspecialchars(
        _T("Several machines can be picked one after the other: no group is needed.", "reflex")
    ) . '</em>');
}
$f->push(new Table());
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->add(new TrFormElement(_T("Target", "reflex"), $typeSelect));

// The script keeps only the relevant row visible; without it every row shows
// and the backend still validates the one that matches the chosen type.
foreach ($targetFields as $type => $field) {
    if (!isset($targetOptions[$type])) {
        continue;
    }
    // A neutral first entry. SelectItem cannot disable an option; the empty value
    // is rejected server side instead.
    $choices = array('' => _T("Choose...", "reflex")) + $targetOptions[$type];
    // The multiple state is set by the script: with none the control stays a
    // plain select.
    $select = new SelectItem($targetInputNames[$type]);
    // SelectItem prints labels and values verbatim.
    $select->setElements(array_map(
        array('ReflexDynamicForm', 'escapeForWidget'), array_values($choices)));
    $select->setElementsVal(array_keys($choices));
    $select->setSelected('');
    $f->add(new TrFormElement($targetTypeOptions[$type], $select));
}

if ($intervalSelect !== null) {
    $f->add(new TrFormElement(_T("Cadence", "reflex"), $intervalSelect));
}
$f->pop();
$f->addValidateButtonWithValue("bconfirm", _T("Assign", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
<div class="reflex-popup-error" id="reflex-assign-error" hidden></div>
<script type="text/javascript">
// Caught before the form leaves: submitting navigates away and the popup came
// back empty. The server keeps its own checks, which are the ones that count.
(function () {
    // Scoped to the popup: the page behind it carries its own forms.
    var form = document.querySelector("#__popup_container form");
    var driver = document.getElementsByName("target_type")[0];
    var notice = document.getElementById("reflex-assign-error");
    if (!form || !driver || !notice) {
        return;
    }
    var fields = <?php echo json_encode($targetInputNames, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;
    var messages = <?php echo json_encode(array(
        'machine' => _T("Choose at least one machine", "reflex"),
        'other' => _T("Please pick a target in the list", "reflex")
    ), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;

    function picked(type) {
        var node = document.getElementsByName(fields[type])[0];
        if (!node) {
            return true;
        }
        if (type === "machine") {
            var options = node.options || [];
            for (var i = 0; i < options.length; i++) {
                if (options[i].selected && options[i].value !== "") {
                    return true;
                }
            }
            return false;
        }
        return node.value !== "";
    }

    function satisfied() {
        var type = driver.value;
        return (type === "all" || !fields.hasOwnProperty(type) || picked(type));
    }

    form.addEventListener("submit", function (event) {
        if (satisfied()) {
            notice.hidden = true;
            return;
        }
        var type = driver.value;
        event.preventDefault();
        notice.textContent = (type === "machine") ? messages.machine : messages.other;
        notice.hidden = false;
    });

    // Left on screen it keeps accusing an operator who has already corrected.
    form.addEventListener("change", function () {
        if (satisfied()) {
            notice.hidden = true;
        }
    });

    driver.addEventListener("change", function () {
        // Another type is another field: what was refused is no longer asked.
        notice.hidden = true;
    });
})();
</script>
<script type="text/javascript">
(function () {
    var driver = document.getElementsByName("target_type")[0];
    if (!driver) {
        return;
    }
    var fields = <?php echo json_encode($targetInputNames, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;

    function rowOf(name) {
        var node = document.getElementsByName(name)[0];
        if (!node) {
            return null;
        }
        while (node && node.tagName !== "TR") {
            node = node.parentNode;
        }
        return node;
    }

    function apply() {
        for (var type in fields) {
            if (!fields.hasOwnProperty(type)) {
                continue;
            }
            var row = rowOf(fields[type]);
            if (row) {
                row.style.display = (driver.value === type) ? "" : "none";
            }
        }
    }

    driver.addEventListener("change", apply);
    apply();
})();
</script>
<?php if (isset($targetOptions['machine'])): ?>
<script type="text/javascript">
// One control, not two: the select still carries the submitted values, hidden
// behind a field that lists the preloaded machines and searches the rest
// server side. What is picked shows as removable tokens.
(function () {
    var select = document.getElementsByName(<?php echo json_encode($targetInputNames['machine'], JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>)[0];
    if (!select || typeof jQuery === "undefined" || !jQuery.fn || !jQuery.fn.autocomplete) {
        return;
    }
    var MIN_LENGTH = <?php echo intval(ReflexTargets::SEARCH_MIN_LENGTH); ?>;
    var SEARCH_URL = <?php echo json_encode(urlStrRedirect("reflex/reflex/ajaxSearchMachines"), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;
    var NO_MATCH = <?php echo json_encode(_T("No machine matches", "reflex"), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;
    var REMOVE_LABEL = <?php echo json_encode(_T("Remove this machine", "reflex"), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;

    var picker = jQuery(select);
    var preloaded = [];
    picker.find("option").each(function () {
        if (this.value !== "") {
            preloaded.push({label: jQuery(this).text(), value: this.value});
        }
    });

    var search = jQuery("<input>", {
        type: "text",
        "class": "reflex-machine-search",
        placeholder: <?php echo json_encode(_T("Choose or search a machine", "reflex"), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>
    });
    // Set as an attribute, never through the property map: jQuery calls any key
    // matching a jQuery.fn method, and jQuery UI defines .autocomplete().
    search.attr("autocomplete", "off");
    search.insertBefore(picker);
    picker.hide();
    // Set here rather than server side: with no script the control stays a plain
    // single select whose neutral first entry avoids picking by accident.
    picker.attr("multiple", "multiple");
    picker.find("option").each(function () {
        if (this.value === "") {
            jQuery(this).remove();
        }
    });
    picker.find("option").prop("selected", false);

    // Holds the tokens. They are a view of the select, they carry no data.
    var tokens = jQuery("<div></div>", {"class": "reflex-token-list"});
    tokens.insertAfter(search);

    // Announced natively: jQuery.trigger() only reaches jQuery handlers, and the
    // banner watcher is bound with addEventListener.
    function announce() {
        if (typeof Event === "function") {
            select.dispatchEvent(new Event("change", {bubbles: true}));
        } else {
            picker.trigger("change");
        }
    }

    // The menu of a previously opened popup outlives its input.
    jQuery("ul.reflex-autocomplete").remove();

    function optionFor(value) {
        var found = null;
        picker.find("option").each(function () {
            if (this.value === value) {
                found = this;
            }
        });
        return found;
    }

    function pick(value, label) {
        value = String(value);
        var option = optionFor(value);
        // A machine found by search usually lies outside the preloaded window.
        if (!option) {
            option = jQuery("<option></option>").attr("value", value).text(label);
            picker.append(option);
            option = option[0];
        }
        if (option.selected) {
            // Already picked: no second token for the same machine.
            return;
        }
        option.selected = true;

        var token = jQuery("<span></span>", {"class": "reflex-token"});
        // Hostnames are reported by agents: written as text, never as markup.
        token.append(jQuery("<span></span>").text(jQuery(option).text()));
        var remove = jQuery("<button></button>", {type: "button", "class": "reflex-token-remove"});
        remove.attr("title", REMOVE_LABEL).attr("aria-label", REMOVE_LABEL).text("\u00d7");
        remove.on("click", function (event) {
            event.preventDefault();
            option.selected = false;
            token.remove();
            search.focus();
            announce();
        });
        token.append(remove);
        tokens.append(token);
        announce();
    }

    search.on("keydown", function (event) {
        // Enter belongs to the suggestion list, not to the form submission.
        if (event.keyCode === 13) {
            event.preventDefault();
        }
    });

    search.autocomplete({
        // Zero, so a click lists what is already loaded without asking the server.
        minLength: 0,
        source: function (request, response) {
            var term = jQuery.trim(request.term || "");
            if (term.length < MIN_LENGTH) {
                var matcher = new RegExp(jQuery.ui.autocomplete.escapeRegex(term), "i");
                var local = jQuery.grep(preloaded, function (item) {
                    return !term || matcher.test(item.label);
                });
                response(local.length ? local : [{label: NO_MATCH, value: ""}]);
                return;
            }
            jQuery.getJSON(SEARCH_URL, {term: term}, function (data) {
                var items = jQuery.isArray(data) ? data : [];
                response(items.length ? items : [{label: NO_MATCH, value: ""}]);
            }).fail(function () {
                response([{label: NO_MATCH, value: ""}]);
            });
        },
        select: function (event, ui) {
            if (!ui.item || String(ui.item.value) === "") {
                return false;
            }
            pick(ui.item.value, ui.item.label);
            // Emptied rather than filled: the field is free for the next machine.
            search.val("");
            return false;
        },
        focus: function (event, ui) {
            // Walking the suggestions must not overwrite the typed term.
            return false;
        }
    });

    search.on("click", function () {
        if (!search.autocomplete("widget").is(":visible")) {
            search.autocomplete("search", search.val());
        }
    });

    search.on("blur", function () {
        // Left after the widget has handled the click that caused this blur.
        window.setTimeout(function () {
            // Free text carries no machine: dropped, so what is read is what would be
            // submitted.
            search.val("");
        }, 150);
    });

    // The menu is attached to the body, below the popup in the stacking order.
    var instance = search.autocomplete("instance");
    if (instance && instance.menu) {
        instance.menu.element.addClass("reflex-autocomplete");
    }

    function escapeHtml(value) {
        return jQuery("<div></div>").text(String(value)).html();
    }

    if (instance) {
        instance._renderItem = function (ul, item) {
            var entry = jQuery("<li></li>");
            if (String(item.value) === "") {
                entry.addClass("reflex-no-match");
            }
            // Escaped first, then the typed term is highlighted on the escaped text.
            var text = escapeHtml(item.label);
            var term = jQuery.trim(search.val());
            if (term && String(item.value) !== "") {
                var needle = jQuery.ui.autocomplete.escapeRegex(escapeHtml(term));
                text = text.replace(new RegExp("(" + needle + ")", "i"),
                                    "<span class=\"reflex-match\">$1</span>");
            }
            return entry.append(jQuery("<div></div>").html(text)).appendTo(ul);
        };
    }
})();
</script>
<?php endif; ?>
