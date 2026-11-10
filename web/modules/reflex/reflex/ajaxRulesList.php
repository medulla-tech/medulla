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
 * Reflex Module - Ajax Notification Rules List
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$login = reflex_current_login();
// Partitioned by the server: nothing is filtered here.
$rules = xmlrpc_reflex_get_notification_rules($login);
if (!is_array($rules)) {
    $rules = array();
}

if ($filter !== "") {
    $rules = array_values(array_filter($rules, function ($rule) use ($filter) {
        return stripos((string) ($rule['channel_name'] ?? ''), $filter) !== false
            || stripos((string) ($rule['probe_label'] ?? ''), $filter) !== false
            || stripos((string) ($rule['recipients'] ?? ''), $filter) !== false;
    }));
}

$count = count($rules);
$pagedRules = array_slice($rules, $start, $maxperpage);

// The column only earns its place when at least one rule carries a
// restriction. Counted over the whole list, so browsing keeps the columns.
$hasRestriction = false;
foreach ($rules as $rule) {
    if (trim((string) ($rule['target_filter'] ?? '')) !== '') {
        $hasRestriction = true;
        break;
    }
}

// Same for the escalation: a column of "None" on every row discriminates
// nothing.
$hasEscalation = false;
foreach ($rules as $rule) {
    if (intval($rule['escalation_minutes'] ?? 0) > 0) {
        $hasEscalation = true;
        break;
    }
}

$channelNames = array();
$probeLabels = array();
$minSeverities = array();
$recipients = array();
$cooldowns = array();
$escalations = array();
$restrictions = array();
$states = array();
$params = array();

$hasUnreachable = false;

foreach ($pagedRules as $rule) {
    $channelName = ReflexHelper::safe($rule['channel_name'] ?? '');
    // 0 is the normal state and also covers the case where the server could not
    // count: nothing is shown then.
    if (intval($rule['reaches_nothing'] ?? 0) === 1) {
        $channelName .= ' ' . ReflexTip::on(
            '<span class="reflex-muted">'
                . htmlspecialchars(_T("reaches no machine", "reflex")) . '</span>',
            array(_T("The entity of this channel carries none of your machines: this rule will never send anything.", "reflex"))
        );
        $hasUnreachable = true;
    }
    $channelNames[] = $channelName;
    // get_notification_rules joins the name without saying whether the probe is
    // shipped.
    $probeLabels[] = ReflexHelper::safeProduct(
        $rule['probe_label'] ?? '', null, _T("All probes", "reflex"));
    $minSeverities[] = ReflexBadge::severity($rule['min_severity'] ?? 'high');
    $recipients[] = ReflexBadge::recipientList($rule['recipients'] ?? '');
    $cooldowns[] = htmlspecialchars(ReflexHelper::formatInterval(intval($rule['cooldown_minutes'] ?? 0) * 60));
    if ($hasEscalation) {
        $escalations[] = empty($rule['escalation_minutes'])
            ? '<span class="reflex-muted">' . htmlspecialchars(_T("None", "reflex")) . '</span>'
            : htmlspecialchars(ReflexHelper::formatInterval(intval($rule['escalation_minutes']) * 60));
    }
    if ($hasRestriction) {
        $restrictionLabel = ReflexTargets::ruleFilterLabel($rule['target_filter'] ?? '');
        if ($restrictionLabel === null) {
            // Stored before the restriction became a closed list: it names nothing, so
            // the rule really applies everywhere.
            $restrictions[] = '<span class="reflex-muted">'
                . htmlspecialchars(_T("Restriction not recognised", "reflex")) . '</span>';
        } elseif ($restrictionLabel === '') {
            $restrictions[] = '<span class="reflex-muted">'
                . htmlspecialchars(_T("Every machine", "reflex")) . '</span>';
        } else {
            $restrictions[] = htmlspecialchars($restrictionLabel);
        }
    }
    $states[] = ReflexBadge::enabled($rule['enabled'] ?? 0);
    $params[] = array('rule_id' => intval($rule['id'] ?? 0));
}

$editAction = new ActionItem(_T("Edit rule", "reflex"), "ruleEdit", "edit", "", "reflex", "reflex");
$deleteAction = new ActionPopupItem(_T("Delete rule", "reflex"), "ajaxDeleteRule", "delete", "", "reflex", "reflex");
$deleteAction->setWidth(450);

if ($count > 0) {
    $list = new OptimizedListInfos($channelNames, _T("Channel", "reflex"));
    $list->setTableCssClass("reflex-table");
    $list->addExtraInfo($probeLabels, _T("Probe", "reflex"));
    $list->addExtraInfoCentered($minSeverities, _T("Minimum severity", "reflex"));
    $list->addExtraInfoCenteredRaw($recipients, _T("Recipients", "reflex"));
    if ($hasRestriction) {
        $list->addExtraInfo(
            $restrictions,
            _T("Restriction", "reflex"),
            "",
            _T("Group or entity the rule is limited to.", "reflex")
        );
    }
    $list->addExtraInfoCentered($cooldowns, _T("Cooldown", "reflex"));
    if ($hasEscalation) {
        $list->addExtraInfoCentered($escalations, _T("Escalation", "reflex"));
    }
    $list->addExtraInfoCentered($states, _T("State", "reflex"));
    $list->setName(_T("Elements", "reflex"));
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter));
    $list->setParamInfo($params);
    $list->addActionItem($editAction);
    $list->addActionItem($deleteAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();

    if ($hasUnreachable) {
        echo ReflexTip::script();
    }
} else {
    EmptyStateBox::show(
        _T("No notification rule", "reflex"),
        _T("Without a rule, alerts stay in the console.", "reflex")
    );
}
?>
<script type="text/javascript">
// .infomach pattern: the native title attribute is unstyled and slow.
jQuery(function () {
    jQuery(".reflex-recipients").tooltip({
        position: { my: "left+15 center", at: "right center" },
        items: "[mydata]",
        content: function () {
            return jQuery(this).attr("mydata");
        }
    });
});
</script>
