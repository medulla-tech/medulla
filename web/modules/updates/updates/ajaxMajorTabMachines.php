<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMajorTabMachines.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");
require_once("modules/base/includes/computers_list.inc.php");

$tabId = isset($_GET['tab']) ? (string) $_GET['tab'] : "";
if (updatesAjaxDenied("MajorEntitiesList", $tabId)) {
    return;
}
$entity = updatesSelectedEntity();
list($filter, $start, $maxperpage) = updatesListParams();

$total = 0;
$rows = array();
$system = updatesUpgradeTabs()[$tabId]['system'] ?? null;
$linux = ($system === 'linux');
if ($system !== null) {
    $result = xmlrpc_get_upgrade_machine_list($entity ? array(updatesEntityId($entity)) : array(),
                                              $start, $maxperpage, $filter, "", $system);
    if (updatesReadFailed($result)) {
        updatesReadFailedBox();
        return;
    }
    if (is_array($result['rows'] ?? null)) {
        $total = intval($result['total'] ?? 0);
        $rows = array_values(array_filter($result['rows'], 'is_array'));
    }
}

$canLaunch = updatesUpgradeCanLaunch($tabId);
$launchAction = new ActionPopupItem(htmlspecialchars(_T("Upgrade machine", "updates"), ENT_QUOTES, 'UTF-8'),
                                    "launchUpgrade", "up", "", "updates", "updates", null, 500);
$cancelAction = new ActionPopupItem(htmlspecialchars(_T("Abandon", "updates"), ENT_QUOTES, 'UTF-8'),
                                    "cancelUpgrade", "stop", "", "updates", "updates", null, 500);
$noLaunchAction = new EmptyActionItem(htmlspecialchars(_T("Upgrade unavailable", "updates"), ENT_QUOTES, 'UTF-8'));
$noLaunchAction->setClassCss('up');
$noCancelActions = array();
foreach (array('not_launched'   => _T("No upgrade launched", "updates"),
               'step_running'   => updatesWinDeployErrorText('step_running', ''),
               'reboot_pending' => updatesWinDeployErrorText('reboot_pending', '')) as $refusal => $reason) {
    $noCancelActions[$refusal] = new EmptyActionItem(htmlspecialchars($reason, ENT_QUOTES, 'UTF-8'));
    $noCancelActions[$refusal]->setClassCss('stop');
}
$noLogAction = new EmptyActionItem1(_T("Detail", "xmppmaster"), "viewlogs", "displayg");

$hostnames = array();
$entities = array();
$versions = array();
$targets = array();
$eligibilities = array();
$states = array();
$reports = array();
$actions = array();
$cancelActions = array();
$restartActions = array();
$logActions = array();
$params = array();
$presences = array();
$hasTarget = false;
foreach ($rows as $row) {
    $hostname = trim((string) ($row['hostname'] ?? ''));
    $jid = trim((string) ($row['jid'] ?? ''));
    $hostnames[] = updatesMachineLink(($hostname !== '') ? $hostname : $jid, $jid, $entity);
    $presences[] = updatesWinTriState($row['online'] ?? null) === true ? "machineNamepresente" : "machineName";
    $entityName = htmlspecialchars((string) ($row['entity_name'] ?? ''), ENT_QUOTES, 'UTF-8');
    $entities[] = '<span class="cell-text" title="' . $entityName . '">' . $entityName . '</span>';

    $product = trim((string) ($row['product'] ?? ''));
    $release = trim((string) ($row['release'] ?? ''));
    $target = trim((string) ($row['target_release'] ?? ''));
    if ($linux) {
        $version = ($product !== '') ? $product : $release;
        $build = trim((string) ($row['kernel'] ?? ''));
    } else {
        $version = trim($product . ' ' . $release);
        $build = trim((string) ($row['build'] ?? ''));
    }
    if ($version === '') {
        $versions[] = '<span class="cell-empty">-</span>';
    } else {
        $titleAttr = ($build !== '') ? ' title="' . htmlspecialchars($build, ENT_QUOTES, 'UTF-8') . '"' : '';
        $cell = '<span class="cell-text"' . $titleAttr . '>' . htmlspecialchars($version, ENT_QUOTES, 'UTF-8') . '</span>';
        $reached = $linux
            ? preg_match('/\d+(?:\.\d+)*/', $target, $number) && preg_match('/(?<![\d.])' . preg_quote($number[0], '/') . '(?!\d)/', $version)
            : str_ends_with($version, $target);
        if (($row['category'] ?? '') === 'ready' && $target !== '' && $reached) {
            $cell .= '<span class="updates-upgrade-unfinished" title="'
                . htmlspecialchars(_T("Upgrade not finished: start it again to complete it.", "updates"), ENT_QUOTES, 'UTF-8')
                . '">&#9888;&#xFE0E;</span>';
        }
        $versions[] = $cell;
    }

    $targets[] = ($target !== '') ? htmlspecialchars($target, ENT_QUOTES, 'UTF-8') : '<span class="cell-empty">-</span>';
    $hasTarget = $hasTarget || $target !== '';
    $eligibilities[] = updatesUpgradeEligibilityCell($row);

    $states[] = updatesUpgradeStateCell($row);
    $reports[] = updatesWinReportDate($row['received_at'] ?? '');

    $glpiUuid = trim((string) ($row['glpi_uuid'] ?? ''));
    $entityId = updatesWinNumber($row['entity_id'] ?? null);
    $launchable = $canLaunch && updatesUpgradeLaunchable((string) ($row['category'] ?? ''))
        && $glpiUuid !== '' && $entityId !== null;
    $refusal = ($jid !== '' && $entityId !== null) ? updatesUpgradeCancelRefusal($row, $system) : 'not_launched';
    $actions[] = $launchable ? $launchAction : $noLaunchAction;
    $cancelActions[] = ($refusal === '') ? $cancelAction : $noCancelActions[$refusal];
    $restartActions[] = updatesRestartAction(array('from' => 'major'),
                                             ($row['category'] ?? '') === 'reboot_pending' && $jid !== '',
                                             updatesWinTriState($row['online'] ?? null) === true,
                                             updatesWinTriState($row['restart_requested'] ?? null) === true);
    // Sur l'action seule : le lancement et l'abandon gardent le nom de la machine.
    $logActions[] = is_array($row['last_deployment'] ?? null)
        ? new ActionItem(_T("Detail", "xmppmaster"), "viewlogs", "display", "", "xmppmaster", "xmppmaster", null, false,
                         updatesDeployLogParams($row['last_deployment']))
        : $noLogAction;
    $rowParams = array('entity' => 'UUID' . (int) $entityId, 'uuid' => $glpiUuid, 'jid' => $jid,
                       'hostname' => $hostname, 'tab' => $tabId);
    if ($entity) {
        $rowParams['location'] = $entity['uuid'];
    }
    $params[] = $rowParams;
}

$n = new OptimizedListInfos($hostnames, _T("Machine", "updates"));
$n->disableFirstColumnActionLink();
$n->setMainActionClasses($presences);
$n->addExtraInfoRaw($entities, _T("Entity", "updates"));
$n->addExtraInfoRaw($versions, _T("Current version", "updates"));
if ($hasTarget) {
    $n->addExtraInfoRaw($targets, _T("Target version", "updates"));
    if (!$linux) {
        $n->addExtraInfoRaw($eligibilities, _T("Eligibility", "updates"));
    }
}
$n->addExtraInfoRaw($states, _T("Status", "updates"));
$n->addExtraInfoRaw($reports, _T("Last report", "updates"));
$n->addActionItemArray($logActions);
if ($canLaunch) {
    $n->addActionItemArray($actions);
    $n->addActionItemArray($cancelActions);
}
$n->addActionItemArray($restartActions);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $total;
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES)));
updatesMachinesEmptyState($n, $filter, $linux ? _T("No Linux machines", "updates") : _T("No Windows machines", "updates"));
$n->display();
updatesWinTooltips();
if ($hasTarget && !$linux) {
?>
<script>
jQuery(function() {
    if (!(jQuery.ui && jQuery.ui.tooltip)) { return; }
    jQuery("table.listinfos .updates-eligibility").tooltip({
        position: {
            my: "center top+8",
            at: "center bottom",
            collision: "flipfit flipfit"
        },
        items: "[mydata]",
        content: function() { return jQuery(this).attr("mydata"); }
    });
});
</script>
<?php
}
?>
