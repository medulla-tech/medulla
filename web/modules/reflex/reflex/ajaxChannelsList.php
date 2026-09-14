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
 * Reflex Module - Ajax Notification Channels List
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$login = reflex_current_login();
// Partitioned by the server: nothing is filtered here.
$channels = xmlrpc_reflex_get_channels($login);
if (!is_array($channels)) {
    $channels = array();
}

if ($filter !== "") {
    $channels = array_values(array_filter($channels, function ($channel) use ($filter) {
        return stripos((string) ($channel['name'] ?? ''), $filter) !== false
            || stripos((string) ($channel['channel_type'] ?? ''), $filter) !== false;
    }));
}

$count = count($channels);
$pagedChannels = array_slice($channels, $start, $maxperpage);

// The edition form only offers email, so the type column repeats the same
// word on every row. Counted over the whole list, so browsing keeps the
// columns.
$hasOtherType = false;
foreach ($channels as $channel) {
    if (strtolower((string) ($channel['channel_type'] ?? 'email')) !== 'email') {
        $hasOtherType = true;
        break;
    }
}

// Always shown: a channel whose entity does not match the one of the machine
// in alert sends nothing, silently, the resolution being flat. An entity the
// session cannot list is stated by its identifier.
$entityNames = ReflexTargets::entityOptions();

$names = array();
$entities = array();
$types = array();
$states = array();
$createdBy = array();
$params = array();

foreach ($pagedChannels as $channel) {
    $names[] = ReflexHelper::safe($channel['name'] ?? '');
    $entityId = ReflexTargets::identifier($channel['entity_id'] ?? null);
    if (isset($entityNames[$entityId])) {
        $entities[] = htmlspecialchars((string) $entityNames[$entityId]);
    } else {
        $entities[] = htmlspecialchars(sprintf(_T("Entity %d", "reflex"), (int) $entityId));
    }
    if ($hasOtherType) {
        $types[] = htmlspecialchars(ReflexHelper::channelTypeLabel($channel['channel_type'] ?? ''));
    }
    $states[] = ReflexBadge::enabled($channel['enabled'] ?? 0);
    $createdBy[] = ReflexHelper::authorLabel($channel['created_by'] ?? '');
    $params[] = array(
        'channel_id' => intval($channel['id'] ?? 0),
        'name' => $channel['name'] ?? ''
    );
}

$editAction = new ActionItem(_T("Edit channel", "reflex"), "channelEdit", "edit", "", "reflex", "reflex");
$testAction = new ActionPopupItem(_T("Test channel", "reflex"), "ajaxTestChannel", "scan", "", "reflex", "reflex");
$testAction->setWidth(450);
$deleteAction = new ActionPopupItem(_T("Delete channel", "reflex"), "ajaxDeleteChannel", "delete", "", "reflex", "reflex");
$deleteAction->setWidth(450);

if ($count > 0) {
    $list = new OptimizedListInfos($names, _T("Channel", "reflex"));
    $list->setTableCssClass("reflex-table");
    $list->addExtraInfo(
        $entities,
        _T("Entity", "reflex"),
        "",
        _T("The client the channel belongs to: it only receives the alerts of the machines of that entity, not those of its sub-entities.", "reflex")
    );
    if ($hasOtherType) {
        $list->addExtraInfo($types, _T("Type", "reflex"));
    }
    $list->addExtraInfoCentered($states, _T("State", "reflex"));
    $list->addExtraInfo($createdBy, _T("Created by", "reflex"));
    $list->setName(_T("Elements", "reflex"));
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter));
    $list->setParamInfo($params);
    $list->addActionItem($editAction);
    $list->addActionItem($testAction);
    $list->addActionItem($deleteAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();
} else {
    EmptyStateBox::show(
        _T("No notification channel", "reflex"),
        _T("Create a channel so that alerts can be sent out.", "reflex")
    );
}
?>
