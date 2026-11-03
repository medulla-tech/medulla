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
 * Reflex Module - Notification channel creation and modification
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$channelId = isset($_GET['channel_id']) ? intval($_GET['channel_id']) : 0;
if ($channelId <= 0 && isset($_POST['channel_id'])) {
    $channelId = intval($_POST['channel_id']);
}
$isNew = ($channelId <= 0);

$channelTypeOptions = ReflexHelper::channelTypeOptions();

$login = reflex_current_login();
// The list is the one the backend builds for this login: what is offered here
// is never refused on save.
$entityOptions = ReflexTargets::userEntityOptions($login);

$channel = array(
    'name' => '',
    'channel_type' => 'email',
    'config_json' => '',
    'enabled' => 1,
    'entity_id' => null
);

if (!$isNew) {
    $channels = xmlrpc_reflex_get_channels($login);
    $found = null;
    if (is_array($channels)) {
        foreach ($channels as $row) {
            if (intval($row['id'] ?? 0) === $channelId) {
                $found = $row;
                break;
            }
        }
    }
    if ($found === null) {
        $channel = null;
    } else {
        $channel = array_merge($channel, $found);
    }
}

// The root entity of GLPI carries the identifier 0, an entity like any other,
// which intval() would fold onto a value that is simply not there.
$storedEntity = ReflexTargets::identifier(is_array($channel) ? ($channel['entity_id'] ?? null) : null);
// On creation the first entity within reach is preselected: it is what a
// browser submits when nothing is touched.
$reachableEntityIds = array_keys($entityOptions);
$selectedEntity = ($storedEntity !== null)
    ? (string) $storedEntity
    : (empty($reachableEntityIds) ? '' : (string) reset($reachableEntityIds));

if (isset($_POST['bsave'])) {
    verifyCSRFToken($_POST);

    $channelType = (string) ($_POST['channel_type'] ?? 'email');
    // The submitted type decides which input carries the configuration, so a
    // submission made without the script is read the same way.
    $composedConfig = ReflexDynamicForm::collectChannelConfig(
        $channelType,
        (!$isNew && is_array($channel)) ? ($channel['config_json'] ?? '') : ''
    );

    $payload = array(
        'name' => trim((string) ($_POST['name'] ?? '')),
        'channel_type' => $channelType,
        'config_json' => $composedConfig,
        'enabled' => isset($_POST['enabled']) ? 1 : 0
    );

    // Required like the name; the select holds no neutral entry. An array or an
    // empty field is not an identifier: refused here rather than by the server.
    $entityKey = is_scalar($_POST['entity_id'] ?? null)
        ? ReflexTargets::identifier($_POST['entity_id']) : null;
    if ($entityKey !== null) {
        // An integer, never a string that may be empty.
        $payload['entity_id'] = $entityKey;
        $selectedEntity = (string) $entityKey;
    }

    // The password only travels upwards: an empty field keeps the stored one,
    // the checkbox is the only way to remove it.
    $submittedPassword = (string) ($_POST['smtp_password'] ?? '');
    if (isset($_POST['smtp_password_clear'])) {
        $payload['clear_secret'] = 1;
    } elseif ($submittedPassword !== '') {
        $payload['smtp_password'] = $submittedPassword;
    }

    $error = '';
    if ($payload['name'] === '') {
        $error = _T("The channel name is required", "reflex");
    } elseif ($entityKey === null) {
        $error = _T("Choose the entity the channel belongs to", "reflex");
    } elseif (!isset($channelTypeOptions[$payload['channel_type']])) {
        $error = _T("Unknown channel type", "reflex");
    } elseif ($payload['channel_type'] === 'email') {
        $port = trim((string) ($_POST['channel_port'] ?? ''));
        $fromAddress = trim((string) ($_POST['channel_from_address'] ?? ''));
        if ($port !== '' && (intval($port) < 1 || intval($port) > 65535)) {
            $error = _T("The SMTP port must be between 1 and 65535", "reflex");
        } elseif ($fromAddress !== '' && !filter_var($fromAddress, FILTER_VALIDATE_EMAIL)) {
            $error = _T("The sender address is not a valid email address", "reflex");
        }
    }

    if ($error !== '') {
        new NotifyWidgetFailure($error);
        // Redisplay what was typed. The secret is stripped: it must not reach the
        // rendered form.
        $redisplay = $payload;
        unset($redisplay['smtp_password'], $redisplay['clear_secret']);
        $channel = array_merge(is_array($channel) ? $channel : array(), $redisplay);
    } else {
        $saved = false;

        if ($isNew) {
            $created = xmlrpc_reflex_create_channel($login, $payload);
            // A refusal answers a structure, which is true in PHP: only the identifier
            // says the channel exists. An unusable encryption key comes back that way.
            $newId = ReflexHelper::createdId($created);
            if ($newId > 0) {
                $saved = true;
                new NotifyWidgetSuccess(_T("Channel created", "reflex"));
            } else {
                ReflexHelper::notifyRefusal($created,
                    _T("Failed to create the channel", "reflex"));
            }
        } else {
            // The login is the third argument: without it the server writes no entity.
            $result = xmlrpc_reflex_update_channel($channelId, $payload, $login);
            $saved = ReflexHelper::notifyOutcome($result,
                _T("Channel updated", "reflex"),
                _T("Failed to update the channel", "reflex"));
        }

        if ($saved) {
            header("Location: " . urlStrRedirect("reflex/reflex/settings"));
            exit;
        }
    }
}

$p = new PageGenerator($isNew ? _T("New channel", 'reflex') : _T("Edit channel", 'reflex'));
$p->setSideMenu($sidemenu);
$p->display();

if (!$isNew && $channel === null) {
    EmptyStateBox::show(
        _T("Channel not found", "reflex"),
        _T("This notification channel does not exist any more.", "reflex")
    );
    return;
}

// A channel belongs to an entity without exception: with none within reach
// the reason is named here rather than after the whole form has been filled.
if (empty($entityOptions) && $storedEntity === null) {
    EmptyStateBox::show(
        _T("No entity within your reach", "reflex"),
        _T("A channel belongs to an entity, and your account reaches none. Ask an administrator for access to an entity before creating a channel.", "reflex")
    );
    return;
}

$channelConfig = ReflexDynamicForm::decodeChannelConfig((string) ($channel['config_json'] ?? ''));
// The backend reports whether a password exists, never the password itself.
$secretConfigured = !empty($channel['secret_configured']);

// SelectItem has no per option disabling, so the list is reduced to what can
// be used. A row stored with another type keeps its value offered, so opening
// it does not silently rewrite it.
$storedType = (string) ($channel['channel_type'] ?? 'email');
$typeLabels = array($channelTypeOptions['email']);
$typeValues = array('email');
if ($storedType !== 'email' && isset($channelTypeOptions[$storedType])) {
    $typeLabels[] = $channelTypeOptions[$storedType];
    $typeValues[] = $storedType;
}
$typeSelect = new SelectItem('channel_type');
$typeSelect->setElements($typeLabels);
$typeSelect->setElementsVal($typeValues);
$typeSelect->setSelected($storedType);

// SelectItem prints its option values and labels verbatim, and an entity name
// comes from the database. An entity the session can no longer list stays
// offered so that opening the channel does not rewrite it.
$entityLabels = array();
$entityValues = array();
foreach ($entityOptions as $entityId => $entityName) {
    $entityLabels[] = ReflexDynamicForm::escapeForWidget($entityName);
    $entityValues[] = ReflexDynamicForm::escapeForWidget($entityId);
}
if ($storedEntity !== null && !isset($entityOptions[$storedEntity])) {
    $knownEntities = ReflexTargets::entityOptions();
    $entityLabels[] = ReflexDynamicForm::escapeForWidget(
        isset($knownEntities[$storedEntity])
            ? $knownEntities[$storedEntity]
            : sprintf(_T("Entity %d", "reflex"), $storedEntity));
    $entityValues[] = ReflexDynamicForm::escapeForWidget($storedEntity);
}
// A single possible entity is stated, not offered. The hidden field carries
// it, so the submission holds an entity whatever the user does.
$singleEntity = (count($entityValues) === 1);
if (!$singleEntity) {
    $entitySelect = new SelectItem('entity_id');
    $entitySelect->setElements($entityLabels);
    $entitySelect->setElementsVal($entityValues);
    $entitySelect->setSelected($selectedEntity);
}

$enabledCb = new CheckboxTpl('enabled');

echo '<a href="' . urlStrRedirect('reflex/reflex/settings') . '" class="back-link">&larr; '
   . htmlspecialchars(_T("Back to channels list", "reflex")) . '</a>';

$form = new ValidatingForm(array('method' => 'POST'));

// --- Channel --------------------------------------------------------------
$form->add(new SpanElement(_T("Channel", "reflex"), "section-title"));
$form->push(new Table());
$form->add(
    new TrFormElement(_T("Name", "reflex"), new InputTpl('name', '/^.+$/')),
    array("value" => htmlspecialchars((string) ($channel['name'] ?? ''), ENT_QUOTES, 'UTF-8'), "required" => true)
);
// Always stated, and required like the name.
if ($singleEntity) {
    // The label is already escaped; the hidden field prints its value verbatim.
    $form->add(
        new TrFormElement(_T("Entity", "reflex"), new multifieldTpl(array(
            new textTpl($entityLabels[0]),
            new HiddenTpl('entity_id')
        ))),
        array("value" => array(1 => $entityValues[0]), "hide" => array(1 => true))
    );
} else {
    $form->add(new TrFormElement(_T("Entity", "reflex"), $entitySelect),
               array("required" => true));
}
$form->add(
    new TrFormElement(_T("Type", "reflex"), new multifieldTpl(array(
        $typeSelect,
        new textTpl('<i class="reflex-inherit-hint">'
            . htmlspecialchars(_T("Only the email channel is delivered in this version. The other types are planned.", "reflex"))
            . '</i>')
    )))
);
$form->add(
    new TrFormElement(_T("Channel enabled", "reflex"), $enabledCb),
    array("value" => !empty($channel['enabled']) ? "checked" : "")
);
$form->pop();

// --- Server / Authentication / Sender --------------------------------------
ReflexDynamicForm::addEmailChannelSections($form, $channelConfig, $secretConfigured, $isNew);

$form->add(new HiddenTpl('channel_id'), array("value" => (string) $channelId, "hide" => true));

$form->addValidateButtonWithValue('bsave', _T("Save", "reflex"));
$form->addButton(
    'bcancel',
    _T("Cancel", "reflex"),
    "btnSecondary",
    "onclick=\"location.href='" . urlStrRedirect('reflex/reflex/settings') . "'; return false;\"",
    "button"
);

$form->display();
echo ReflexHelper::scriptTag('reflex.js', true);
