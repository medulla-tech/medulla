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
 * Reflex Module - Ajax Probes List
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
// Named `scope` on the wire and in the query string: the value get_probes
// reads, not the visibility of a probe.
$filterOptions = ReflexHelper::probeFilterOptions();
$scope = isset($_GET["scope"]) ? $_GET["scope"] : "all";
if (!isset($filterOptions[$scope])) {
    $scope = "all";
}

$login = reflex_current_login();
$requestedEntity = ReflexTargets::identifier($_GET["entity_id"] ?? null);
$entityId = ($requestedEntity === null) ? "" : (string) $requestedEntity;

// A shipped probe is stored in English and translated on display: searching
// the stored text would answer nothing to someone typing what he reads. The
// catalog is small, so the page does the search, the sort and the pagination.
$result = xmlrpc_reflex_get_probes($login, 0, 500, "", $scope, $entityId);
$rows = reflex_rows($result);
$total = reflex_total($result);
if ($total > count($rows)) {
    $result = xmlrpc_reflex_get_probes($login, 0, $total, "", $scope, $entityId);
    $rows = reflex_rows($result, $rows);
}

$needle = ReflexHelper::fold(trim($filter));
$matches = array();
foreach ($rows as $row) {
    $isBuiltin = !empty($row['is_builtin']);
    $name = ReflexHelper::productText($row['label'] ?? '', $isBuiltin);
    if ($needle !== '') {
        // The keys stay searchable: the server used to accept them.
        $haystack = ReflexHelper::fold(implode(' ', array(
            $name,
            ReflexHelper::productText($row['description'] ?? '', $isBuiltin),
            ReflexHelper::categoryLabel($row['category'] ?? ''),
            (string) ($row['probe_key'] ?? ''),
            (string) ($row['metric_key'] ?? '')
        )));
        if (strpos($haystack, $needle) === false) {
            continue;
        }
    }
    $row['_sortkey'] = ReflexHelper::fold($name);
    $matches[] = $row;
}

usort($matches, function ($a, $b) {
    $cmp = strcmp($a['_sortkey'], $b['_sortkey']);
    if ($cmp !== 0) {
        return $cmp;
    }
    return intval($a['id'] ?? 0) - intval($b['id'] ?? 0);
});

$count = count($matches);
if ($start < 0 || $start >= $count) {
    $start = 0;
}
$data = array_slice($matches, $start, $maxperpage);

$labels = array();
$categories = array();
$thresholds = array();
$assigned = array();
$params = array();
$editActions = array();
$deleteActions = array();

$editAction = new ActionItem(_T("Edit probe", "reflex"), "probeEdit", "edit", "", "reflex", "reflex");

$deleteAction = new ActionPopupItem(_T("Delete probe", "reflex"), "ajaxDeleteProbe", "delete", "", "reflex", "reflex");
$deleteAction->setWidth(450);

// A shipped probe and a probe shared in read only forbid the same gestures
// for reasons the operator does not act upon in the same way.
$noEditBuiltin = new ReflexDisabledAction(
    _T("Probe shipped with Medulla: duplicate it to obtain an editable variant.", "reflex"),
    "editg"
);
$noEditShared = new ReflexDisabledAction(
    _T("Shared in read only: only its owner changes it.", "reflex"),
    "editg"
);
$noDeleteBuiltin = new ReflexDisabledAction(
    _T("Probe shipped with Medulla: remove its assignments instead of deleting it.", "reflex"),
    "deleteg"
);
$noDeleteOther = new ReflexDisabledAction(
    _T("Only the owner of the probe deletes it.", "reflex"),
    "deleteg"
);

$detailAction = new ActionItem(_T("View probe", "reflex"), "probeDetail", "reflexprobe", "", "reflex", "reflex");
// Duplicating is the way to obtain an editable variant of a catalog probe.
$duplicateAction = new ActionPopupItem(_T("Duplicate probe into a variant of your own", "reflex"), "ajaxDuplicateProbe", "duplicatemaster", "", "reflex", "reflex");
// Wider than a confirmation: the popup carries the label of the copy.
$duplicateAction->setWidth(600);

foreach ($data as $row) {
    $isBuiltin = !empty($row['is_builtin']);
    $isOwner = (isset($row['owner_login']) && $row['owner_login'] === $login && $login !== '');
    $canWrite = (!$isBuiltin && ($isOwner || (isset($row['permission']) && $row['permission'] === 'rw')));

    // A shipped name and description are translated on display; a personal one
    // is the text of its author.
    $label = ReflexHelper::safeProduct($row['label'] ?? '', $isBuiltin);
    $description = trim(ReflexHelper::productText($row['description'] ?? '', $isBuiltin));
    if ($description !== '') {
        $tip = '<div class="column-tooltip__text">'
             . htmlspecialchars($description, ENT_QUOTES, 'UTF-8')
             . '</div>';
        $label = '<span class="infomach reflex-probe-tip" mydata="'
               . htmlentities($tip, ENT_QUOTES, 'UTF-8') . '">'
               . $label . '</span>';
    }
    // A personal probe names its owner; a shipped one names nobody.
    $owner = trim((string) ($row['owner_login'] ?? ''));
    if (!$isBuiltin && $owner !== '') {
        $label .= ' <span class="reflex-owner-tag">' . htmlspecialchars($owner, ENT_QUOTES, 'UTF-8') . '</span>';
    }
    $labels[] = $label;
    $categories[] = htmlspecialchars(ReflexHelper::categoryLabel($row['category'] ?? ''));
    $thresholds[] = ReflexHelper::conditionsSummary($row);
    $assigned[] = ReflexBadge::assignedOn($row);

    $params[] = array(
        'probe_id' => intval($row['id'] ?? 0),
        'label' => $row['label'] ?? ''
    );

    if ($canWrite) {
        $editActions[] = $editAction;
    } else {
        $editActions[] = $isBuiltin ? $noEditBuiltin : $noEditShared;
    }
    if ($canWrite && $isOwner) {
        $deleteActions[] = $deleteAction;
    } else {
        $deleteActions[] = $isBuiltin ? $noDeleteBuiltin : $noDeleteOther;
    }
}

if ($count > 0) {
    $list = new OptimizedListInfos($labels, _T("Probe", "reflex"));
    $list->setResizable();
    $list->setTableCssClass("reflex-table reflex-list-probes");
    $list->addExtraInfo($categories, _T("Category", "reflex"));
    // The page reads the conditions of one entity: the header says which, since
    // the same probe is not set alike everywhere.
    $list->addExtraInfoRaw(
        $thresholds,
        _T("Alert when", "reflex"),
        "",
        _T("Conditions applied in the selected entity.", "reflex")
    );
    $list->addExtraInfoCenteredRaw(
        $assigned,
        _T("State", "reflex"),
        "",
        implode('<br>', array(
            '- ' . _T("In service: measured on at least one machine of your estate.", "reflex"),
            '- ' . _T("A dash: no machine of your estate measures it.", "reflex")
        ))
    );
    $list->setName(_T("Elements", "reflex"));
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter));
    $list->setParamInfo($params);
    $list->addActionItem($detailAction);
    $list->addActionItemArray($editActions);
    $list->addActionItem($duplicateAction);
    $list->addActionItemArray($deleteActions);
    $list->start = 0;
    $list->end = $count;
    $list->display();

    echo ReflexDisabledAction::tooltipScript();

    // Same pattern as ajaxMajorEntitiesList.php of the updates module: jQuery UI
    // plus a mydata attribute.
    echo '<script>
jQuery(function() {
    if (!(jQuery.ui && jQuery.ui.tooltip)) { return; }
    jQuery(".reflex-probe-tip").tooltip({
        position: { my: "left+15 center", at: "right center" },
        items: "[mydata]",
        content: function() { return jQuery(this).attr("mydata"); }
    });
});
</script>';
} else {
    EmptyStateBox::show(
        _T("No probe found", "reflex"),
        _T("No probe matches this filter and this search.", "reflex")
    );
}
?>
