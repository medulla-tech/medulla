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
 * Reflex Module - Ajax Probe Settings Of One Entity
 *
 * The probe sheet reads the settings of one entity at a time. This endpoint
 * draws the same rows when the reader chooses another one. It reads nothing
 * the sheet does not read: the probe and the entities are asked to the
 * backend under the login of the session, which answers the entities of the
 * account and no other. An entity named in the address is looked up in that
 * answer, so a forged identifier finds nothing.
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : 0;
$login = reflex_current_login();
// The root entity is 0: identifier() keeps it apart from an absent choice.
$requestedEntity = ReflexTargets::identifier($_GET['entity_id'] ?? null);

if ($probeId <= 0) {
    return;
}

$detail = xmlrpc_reflex_get_probe($login, $probeId);
$probe = (is_array($detail) && isset($detail['probe']) && is_array($detail['probe']))
    ? $detail['probe'] : array();
$conditions = (is_array($detail) && isset($detail['conditions']) && is_array($detail['conditions']))
    ? $detail['conditions'] : array();
if (empty($probe) || empty($conditions)
    || !function_exists('xmlrpc_reflex_get_probe_entity_settings')) {
    return;
}

$entitySettings = xmlrpc_reflex_get_probe_entity_settings($login, $probeId);
$settingEntities = ReflexEntitySettings::entities($entitySettings, $login);
$selectedEntity = ReflexEntitySettings::selected($settingEntities, $requestedEntity,
                                                 $entitySettings);
if ($selectedEntity === null) {
    return;
}

ReflexEntitySettings::display($probeId, $probe, $selectedEntity, $login);

// The bubbles of the badges are bound when the sheet is drawn: what arrives
// afterwards binds its own.
echo ReflexTip::script();
?>
