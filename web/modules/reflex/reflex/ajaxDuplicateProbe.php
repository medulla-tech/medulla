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
 * Reflex Module - Duplicate Probe Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$label = isset($_GET['label']) ? (string) $_GET['label'] : (string) ($_POST['label'] ?? '');
$login = reflex_current_login();

// Without a label the backend suffixes the source one in English. The copy is
// named from what is on screen: a shipped name is read in the language of the
// session, and the catalog answers for whether the source is shipped.
$sourceLabel = ReflexHelper::productText($label, null);
$suggested = ($sourceLabel === '') ? '' : sprintf(_T("%s (copy)", "reflex"), $sourceLabel);

// Asked for when the user works on several entities, sent silently otherwise.
$entityOptions = ReflexTargets::userEntityOptions($login);
$entityChoice = (count($entityOptions) > 1);
$entityIds = array_keys($entityOptions);
// null, not 0: the root entity is 0, and a copy attached to no entity has to
// stay distinguishable from one attached to the root.
$selectedEntity = $entityChoice ? null : ReflexTargets::identifier(reset($entityIds));

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $newLabel = trim((string) ($_POST['new_label'] ?? ''));
    if ($newLabel === '') {
        $newLabel = $suggested;
    }

    if ($entityChoice) {
        $selectedEntity = ReflexTargets::identifier($_POST['entity_id'] ?? '');
        if ($selectedEntity === null || !isset($entityOptions[$selectedEntity])) {
            new NotifyWidgetFailure(_T("Choose the entity the probe belongs to", "reflex"));
            header("Location: " . urlStrRedirect("reflex/reflex/probes"));
            exit;
        }
    }

    $created = xmlrpc_reflex_duplicate_probe($login, $probeId, $newLabel, $selectedEntity);
    // A refusal answers a structure, which is true in PHP: only the identifier
    // says the copy exists.
    $newId = ReflexHelper::createdId($created);
    if ($newId > 0) {
        new NotifyWidgetSuccess(sprintf(_T("Probe '%s' duplicated", "reflex"), htmlspecialchars($label)));
        header("Location: " . urlStrRedirect("reflex/reflex/probeEdit", array("probe_id" => $newId)));
        exit;
    }

    ReflexHelper::notifyRefusal($created,
        _T("Failed to duplicate the probe", "reflex"));
    header("Location: " . urlStrRedirect("reflex/reflex/probes"));
    exit;
}

// The rank the backend appends is kept out of the 255 character budget by
// the backend itself.
$labelTpl = new InputTpl("new_label");
$labelTpl->setSize(40);
$labelTpl->setAttributCustom('maxlength="255"');

$f = new PopupForm(_T("Duplicate Probe", "reflex"));
// Carries fields: a confirmation is capped at 450 px and would clip the label.
$f->setPopupClass('reflex-popup-form');
$f->addText(sprintf(_T("Duplicate the probe '%s'?", "reflex"), htmlspecialchars($sourceLabel)));
// The visibility is stated, not offered: duplicate_probe takes an entity and
// no visibility. The copy lands on its own form, carrying no assignment.
$f->addText('<em>' . (empty($entityOptions)
    ? _T("The copy is yours and private, with the same conditions. Assignments are not copied.", "reflex")
    : _T("The copy is yours and visible to your entity, with the same conditions. Assignments are not copied.", "reflex"))
    . '</em>');
$f->push(new Table());
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->add(new HiddenTpl("label"), array("value" => htmlspecialchars($label), "hide" => True));
$f->add(
    new TrFormElement(_T("Label of the copy", "reflex"), $labelTpl),
    array("value" => htmlspecialchars($suggested))
);
if ($entityChoice) {
    // SelectItem prints its options verbatim, and entity names come from GLPI.
    $entitySelect = new SelectItem('entity_id');
    $entitySelect->setElements(array_map(array('ReflexDynamicForm', 'escapeForWidget'),
        array_values($entityOptions)));
    $entitySelect->setElementsVal(array_keys($entityOptions));
    $f->add(new TrFormElement(_T("Entity", "reflex"), $entitySelect));
}
$f->pop();
$f->addValidateButtonWithValue("bconfirm", _T("Duplicate", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
