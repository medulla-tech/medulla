<?php
/**
 * (c) 2022-2023 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/kiosk/includes/functions.php");
require_once("includes/UIComponents.php");

kioskRequireAcl("index");

global $conf;
$maxperpage = $conf['global']['maxperpage'];
$start = max(0, intval($_GET['start'] ?? 0));
$filter = isset($_GET['filter']) ? (string) $_GET['filter'] : "";

$result = xmlrpc_kiosk_get_profiles_list(kioskSelectedLocation(), $start, $maxperpage, $filter);
$profiles = (is_array($result) && isset($result['datas']) && is_array($result['datas'])) ? $result['datas'] : array();
$count = is_array($result) ? intval($result['total'] ?? 0) : 0;

if ($count == 0) {
    EmptyStateBox::show(
        _T("No profiles", "kiosk"),
        ($filter === '') ? _T("Use the sidebar menu to create a new profile.", "kiosk") : ''
    );
    return;
}

$entities = kioskEntities();
$canWrite = hasCorrectAcl("kiosk", "kiosk", "edit");

$editAction = new ActionItem(_T("Edit Profile", 'kiosk'), "edit", "edit", "profile", "kiosk", "kiosk");
$deleteAction = new ActionPopupItem(_T("Delete Profile", 'kiosk'), "deleteProfile", "delete", "profile", "kiosk", "kiosk");

$bulkBar = new BulkSelectBar(
    urlStrRedirect("kiosk/kiosk/deleteProfile"),
    '0',
    'profile-select',
    [
        'deleteSelected'    => _T("Delete selected", "kiosk"),
        'cancel'            => _T("Cancel", "kiosk"),
        'selectionMode'     => _T("Selection mode", "kiosk"),
        'confirmDeleteOne'  => _T("Delete this profile?", "kiosk"),
        'confirmDeleteMany' => _T("Delete %d profiles?", "kiosk"),
        'confirm'           => _T("Delete", "kiosk"),
        'partialErrors'     => _T("Some profiles could not be deleted:", "kiosk"),
        'deleteError'       => _T("An error occurred while deleting.", "kiosk"),
        'close'             => _T("Close", "kiosk"),
    ]
);

$names = array();
$entityNames = array();
$statuses = array();
$cssIds = array();
$params = array();

foreach ($profiles as $profile) {
    $id = intval($profile['id']);
    $names[] = htmlspecialchars((string) $profile['name'], ENT_QUOTES, 'UTF-8');
    $entityId = $profile['entity_id'] ?? null;
    $entityNames[] = ($entityId !== null && isset($entities[intval($entityId)]))
        ? htmlspecialchars($entities[intval($entityId)], ENT_QUOTES, 'UTF-8')
        : _T("No entity", "kiosk");
    $statuses[] = ($profile['active'] == 1) ? _T("Active", "kiosk") : _T("Inactive", "kiosk");
    $cssIds[] = 'k_' . $id;
    $params[] = array('id' => $id);
    $bulkBar->addItem($id, (string) $profile['name']);
}

$n = new OptimizedListInfos($names, _T("Profile Name", "kiosk"));
$n->setCssIds($cssIds);
if (!$canWrite) {
    $n->disableFirstColumnActionLink();
}
if (count($entities) > 1) {
    $n->addExtraInfo($entityNames, _T("Entity", "kiosk"));
}
$n->addExtraInfo($statuses, _T("Profile Status", "kiosk"));
$n->setParamInfo($params);
$n->addActionItem($editAction);
if ($canWrite) {
    $n->addActionItem($deleteAction);
}
$n->setName(_T("Elements", "kiosk"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $count;
$n->display();

if ($canWrite) {
    $bulkBar->display();
}
