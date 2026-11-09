<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxApprovalsListWin.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

if (updatesAjaxDenied("updatesListWin")) {
    return;
}

$entity = updatesSelectedEntity();
$linux = (($_GET['system'] ?? '') === 'linux');
$status = updatesApprovalStatus($_GET['status'] ?? null, $linux ? 'linux' : 'windows');
list($filter, $start, $maxperpage) = updatesListParams();

if ($linux) {
    $total = 0;
    $rows = array();
    if ($entity) {
        $result = xmlrpc_get_windows_approvals(updatesEntityId($entity), $status, $start, $maxperpage, $filter, 'linux');
        if (updatesReadFailed($result)) {
            updatesReadFailedBox();
            return;
        }
        if (is_array($result['rows'] ?? null)) {
            $total = intval($result['total'] ?? 0);
            $rows = array_values(array_filter($result['rows'], 'is_array'));
        }
    }
    $packages = array();
    $classifications = array();
    foreach ($rows as $row) {
        $classification = trim((string) ($row['classification'] ?? ''));
        $packages[] = updatesLinuxTextCell($row['package'] ?? '');
        $classifications[] = ($classification !== '') ? updatesCatalogLabel($classification) : '<span class="cell-empty">-</span>';
    }
    $n = new OptimizedListInfos($packages, _T("Package", "updates"));
    $n->disableFirstColumnActionLink();
    $n->setTableCssClass("updates-approval");
    $n->addExtraInfoRaw($classifications, _T("Classification", "updates"));
    $n->start = 0;
    $n->end = $total;
    $n->setItemCount($total);
    $n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES)));
    if ($filter !== '') {
        $n->setEmptyState(_T("No package found", "updates"), _T("No package matches the search.", "updates"));
    } else {
        $n->setEmptyState(($status === 'approved') ? _T("No approved package", "updates") : _T("No package pending", "updates"));
    }
    $n->display();
    return;
}

$total = 0;
$rows = array();
if ($entity) {
    $result = xmlrpc_get_windows_approvals(updatesEntityId($entity), $status, $start, $maxperpage, $filter);
    if (updatesReadFailed($result)) {
        updatesReadFailedBox();
        return;
    }
    if (is_array($result['rows'] ?? null)) {
        $total = intval($result['total'] ?? 0);
        $rows = array_values(array_filter($result['rows'], 'is_array'));
    }
}

$approve = new ActionPopupItem(htmlspecialchars(_T("Approve", "updates")), "grayApprove", "enableupdate", "", "updates", "updates");
$decline = new ActionPopupItem(htmlspecialchars(_T("Decline", "updates")), "banUpdate", "remove", "", "updates", "updates");
$toPending = new ActionPopupItem(htmlspecialchars(_T("Back to pending", "updates")), "whiteUnlist", "pending", "", "updates", "updates");
$none = new EmptyActionItem();

$bulk = array();
if ($entity && $status === 'pending') {
    $bulkTargets = array('approved' => _T("Approve selected", "updates"), 'declined' => _T("Decline selected", "updates"));
    foreach ($bulkTargets as $target => $label) {
        if (hasCorrectAcl("updates", "updates", updatesApprovalActionPage($target))) {
            $bulk[$target] = $label;
        }
    }
}

$checks = array();
$kbs = array();
$titles = array();
$sizes = array();
$risks = array();
$actions = array(array(), array());
$params = array();
$hasByRule = false;
foreach ($rows as $row) {
    $updateId = updatesApprovalId($row['update_id'] ?? null);
    if ($updateId === null) {
        continue;
    }
    $kb = (string) ($row['kb'] ?? '');
    $title = (string) ($row['title'] ?? '');
    $byRule = updatesWinTriState($row['by_rule'] ?? null) === true;
    $hasByRule = $hasByRule || $byRule;
    $inherited = updatesWinInheritedEntity($row['inherited_from'] ?? null);

    $checks[] = '<input type="checkbox" class="approval-check" name="update_ids[]" value="'
        . htmlspecialchars($updateId, ENT_QUOTES, 'UTF-8') . '">';
    $kbs[] = updatesKbCell($kb, updatesWinOfferIcon($row));

    $titleCell = updatesApprovalTitleCell($title, $kb, $status, $byRule, $row['decided_by'] ?? '', $row['decided_at'] ?? '');
    if ($inherited !== null) {
        $titleCell .= ' (' . htmlspecialchars($inherited['name'], ENT_QUOTES, 'UTF-8') . ')';
    }
    $titles[] = $titleCell;
    $sizes[] = updatesSizeCell($row['size'] ?? null);
    $risks[] = updatesWinRiskCell($row['severity'] ?? '', $row['exploited'] ?? null);
    // A deployment only reaches the machines of the entity itself.
    $ownMachines = updatesWinNumber($row['own_machines'] ?? null);

    if ($status === 'pending') {
        $actions[0][] = $approve;
        $actions[1][] = $decline;
    } elseif ($status === 'approved') {
        if ($ownMachines === 0) {
            $actions[0][] = $none;
        } elseif (updatesWinOffer($row) === 'esu') {
            $actions[0][] = updatesWinEsuAction();
        } else {
            $actions[0][] = updatesWinDeployAction(updatesWinPackageBlocker($row['package_state'] ?? '', $row['package_error'] ?? ''));
        }
        $actions[1][] = $decline;
        $actions[2][] = ($byRule || $inherited !== null) ? $none : $toPending;
    } else {
        $actions[0][] = $approve;
        $actions[1][] = ($inherited !== null) ? $none : $toPending;
    }
    $params[] = array(
        'updateid' => $updateId,
        'kb'       => $kb,
        'title'    => $title,
        'location' => $entity['uuid'],
        'from'     => $status,
        'machines' => $ownMachines ?? '',
    );
}

if (!empty($bulk) && !empty($params)) {
    $n = new OptimizedListInfos($checks, '<input type="checkbox" class="approval-check-all" title="'
        . htmlspecialchars(_T("Select all", "updates"), ENT_QUOTES, 'UTF-8') . '">');
    $n->addExtraInfoRaw($kbs, _T("KB", "updates"));
    $n->setTableCssClass("updates-approval updates-approval-bulk");
} else {
    $n = new OptimizedListInfos($kbs, _T("KB", "updates"));
    $n->setTableCssClass("updates-approval");
}
$n->disableFirstColumnActionLink();
$n->addExtraInfoRaw($titles, _T("Title", "updates"));
$n->addExtraInfoRaw($sizes, _T("Size", "updates"));
$n->addExtraInfoRaw($risks, _T("Update Severity", "updates"));
foreach ($actions as $column) {
    $n->addActionItemArray($column);
}
$n->setParamInfo($params);
$n->start = 0;
$n->end = $total;
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES)));
if ($filter !== '') {
    $n->setEmptyState(_T("No updates found", "updates"), _T("No update matches the search.", "updates"));
} else {
    $emptyTitles = array(
        'pending'  => _T("No update pending", "updates"),
        'approved' => _T("No approved update", "updates"),
        'declined' => _T("No declined update", "updates"),
    );
    $emptyDescriptions = array(
        'pending'  => _T("All updates that concern the machines of this entity have been approved or declined.", "updates"),
        'approved' => _T("Approve them from the pending updates, or automatically with an automatic approval rule.", "updates"),
        'declined' => _T("A declined update is never deployed on the machines of this entity.", "updates"),
    );
    $n->setEmptyState($emptyTitles[$status], $emptyDescriptions[$status]);
}

if ($status === 'approved' && $hasByRule) {
    echo '<p class="updates-entity-scope">'
        . htmlspecialchars(_T("Updates covered by an automatic approval rule are approved automatically. To remove one, decline it or change the rule.", "updates"), ENT_QUOTES, 'UTF-8')
        . '</p>';
}

updatesWinTooltips();

if (empty($bulk) || empty($params)) {
    $n->display();
    return;
}

echo '<form method="post" class="updates-approval-form" action="'
    . htmlspecialchars(updatesApprovalUrl($entity, $status), ENT_QUOTES, 'UTF-8') . '">';
$n->display();
echo '<input type="hidden" name="auth_token" value="' . htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8') . '">';
echo '<div class="approval-form-actions">';
foreach ($bulk as $target => $label) {
    $class = ($target === 'approved') ? 'btnPrimary' : 'btnSecondary';
    echo '<button type="submit" class="' . $class . ' approval-bulk" name="approval_bulk" value="'
        . htmlspecialchars($target, ENT_QUOTES, 'UTF-8') . '" disabled>'
        . htmlspecialchars($label, ENT_QUOTES, 'UTF-8') . '</button> ';
}
echo '</div>';
echo '</form>';
?>
<script>
(function() {
    var form = document.querySelector('form.updates-approval-form');
    if (!form) { return; }
    var master = form.querySelector('.approval-check-all');
    var boxes = Array.prototype.slice.call(form.querySelectorAll('input.approval-check'));
    var buttons = Array.prototype.slice.call(form.querySelectorAll('button.approval-bulk'));

    function refresh() {
        var checked = boxes.filter(function(b) { return b.checked; }).length;
        if (master) {
            master.checked = (checked > 0 && checked === boxes.length);
            master.indeterminate = (checked > 0 && checked < boxes.length);
        }
        buttons.forEach(function(b) { b.disabled = (checked === 0); });
    }

    if (master) {
        master.addEventListener('click', function() {
            boxes.forEach(function(b) { b.checked = master.checked; });
            refresh();
        });
    }
    boxes.forEach(function(b) { b.addEventListener('change', refresh); });
    refresh();
})();
</script>
