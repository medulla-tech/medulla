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
 * Reflex Module - Change Probe Visibility Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$login = reflex_current_login();
$visibilityOptions = ReflexHelper::visibilityOptions();

$detail = xmlrpc_reflex_get_probe($login, $probeId);
$probe = (is_array($detail) && isset($detail['probe']) && is_array($detail['probe']))
    ? $detail['probe'] : array();
$current = (string) ($probe['visibility'] ?? 'private');
// A visibility no longer offered must not preselect the first option and turn
// the probe private on a simple confirmation.
if (!isset($visibilityOptions[$current])) {
    $current = ReflexHelper::DEFAULT_VISIBILITY;
}
// probes.entity_id NULL reaches this page as false, as an empty string or not
// at all, never as a number. The root entity holds '0', a real entity: read
// with intval() the two collapse onto 0. null is what says "no entity" here.
$probeEntity = ReflexTargets::identifier($probe['entity_id'] ?? null);

// The entity is only asked for when the probe carries none.
$entityOptions = ($probeEntity !== null) ? array() : ReflexTargets::userEntityOptions($login);
$entityChoice = (count($entityOptions) > 1);
$entityIds = array_keys($entityOptions);
$selectedEntity = $entityChoice ? null : ReflexTargets::identifier(reset($entityIds));

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $visibility = (string) ($_POST['visibility'] ?? '');
    if ($entityChoice) {
        $selectedEntity = ReflexTargets::identifier($_POST['entity_id'] ?? '');
        if ($selectedEntity === null || !isset($entityOptions[$selectedEntity])) {
            $selectedEntity = null;
        }
    }
    $entityId = ($probeEntity !== null) ? $probeEntity : $selectedEntity;

    if (!isset($visibilityOptions[$visibility])) {
        new NotifyWidgetFailure(_T("Unknown visibility", "reflex"));
    } elseif ($visibility === 'entity' && $entityId === null) {
        new NotifyWidgetFailure(_T("Choose the entity the probe belongs to", "reflex"));
    } else {
        $result = xmlrpc_reflex_set_probe_visibility($login, $probeId, $visibility, $entityId);
        ReflexHelper::notifyOutcome($result,
            _T("Probe visibility updated", "reflex"),
            _T("Failed to update the probe visibility", "reflex"));
    }

    header("Location: " . urlStrRedirect("reflex/reflex/probeDetail", array("probe_id" => $probeId)));
    exit;
}

$visibilitySelect = new SelectItem('visibility');
$visibilitySelect->setElements(array_values($visibilityOptions));
$visibilitySelect->setElementsVal(array_keys($visibilityOptions));
$visibilitySelect->setSelected($current);

$f = new PopupForm(_T("Change visibility", "reflex"));
// Carries fields: a confirmation is capped at 450 px and would clip the selects.
$f->setPopupClass('reflex-popup-form');
$f->addText('<em>' . htmlspecialchars(_T("Private: only you. Shared: the users of its entity.", "reflex")) . '</em>');
$f->push(new Table());
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->add(new TrFormElement(_T("Visibility", "reflex"), $visibilitySelect));
if ($entityChoice) {
    // SelectItem prints its options verbatim, and entity names come from GLPI.
    $entitySelect = new SelectItem('entity_id');
    $entitySelect->setElements(array_map(array('ReflexDynamicForm', 'escapeForWidget'),
        array_values($entityOptions)));
    $entitySelect->setElementsVal(array_keys($entityOptions));
    $f->add(new TrFormElement(_T("Entity", "reflex"), $entitySelect));
}
$f->pop();
$f->addValidateButtonWithValue("bconfirm", _T("Apply", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
