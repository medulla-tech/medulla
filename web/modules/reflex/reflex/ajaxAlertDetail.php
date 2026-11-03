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
 * Reflex Module - Alert Detail Popup
 *
 * One alert, answering in this order what happened, when, on what, and
 * whether anybody was warned. A popup and not a page: leaving the list would
 * cost the filters AjaxFilter freezes when it is built.
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

$alertId = isset($_GET['alert_id']) ? intval($_GET['alert_id']) : 0;
$login = reflex_current_login();

$result = ($alertId > 0) ? xmlrpc_reflex_get_alert($login, $alertId) : null;
$alert = (is_array($result) && isset($result['alert']) && is_array($result['alert']))
    ? $result['alert'] : array();

function reflex_alert_popup_close()
{
    echo '<div class="reflex-popup-actions">';
    echo '<input type="button" class="btnPrimary" value="'
       . htmlspecialchars(_T("Close", "reflex"), ENT_QUOTES, 'UTF-8')
       . '" onclick="closePopup(); return false;" />';
    echo '</div>';
}
?>

<h1 class="reflex-popup-heading"><?php echo _T("Alert detail", "reflex"); ?></h1>

<?php
if (empty($alert)) {
    // An alert out of scope and an alert that never existed answer the same
    // refusal. One the console knows how to word takes over.
    $refusal = ReflexHelper::callRefusal($result);
    $reason = ReflexHelper::refusalReasonText(is_array($refusal) ? ($refusal['reason'] ?? '') : '');
    if ($alertId <= 0) {
        $reason = _T("No alert identifier was supplied.", "reflex");
    } elseif ($reason === '') {
        $reason = _T("This alert does not exist any more or you are not allowed to see it.", "reflex");
    }
    echo '<p class="reflex-popup-empty">' . htmlspecialchars($reason, ENT_QUOTES, 'UTF-8') . '</p>';
    reflex_alert_popup_close();
    return;
}

$condition = (isset($result['condition']) && is_array($result['condition'])) ? $result['condition'] : array();
// Both answered by the backend: two screens must not spell the rule
// differently.
$frozen = (isset($result['condition_at_trigger']) && is_array($result['condition_at_trigger']))
    ? $result['condition_at_trigger'] : array();
$trust = (isset($result['condition_trust']) && is_array($result['condition_trust']))
    ? $result['condition_trust'] : array();
$notifications = (isset($result['notifications']) && is_array($result['notifications'])) ? $result['notifications'] : array();
$skipped = (isset($result['skipped']) && is_array($result['skipped'])) ? $result['skipped'] : array();

$status = strtolower((string) ($alert['status'] ?? 'open'));
$unit = (string) ($alert['unit'] ?? '');
// An alert row carries no value_type: the catalog answers for it.
$valueType = reflex_probe_value_type($login, $alert['probe_id'] ?? 0);
$instance = ReflexHelper::alertInstance($alert);
$ackUser = trim((string) ($alert['ack_user'] ?? ''));
$ackComment = trim((string) ($alert['ack_comment'] ?? ''));
$alertMessage = trim((string) ($alert['message'] ?? ''));
$openedAt = ReflexHelper::plainDate($alert['opened_at'] ?? '');
$confirmedAt = ReflexHelper::plainDate($alert['last_seen_at'] ?? '');
?>

<div class="reflex-alert-sheet">
<div class="reflex-summary">
    <div class="reflex-summary-title">
        <?php echo ReflexHelper::safe($alert['hostname'] ?? ''); ?>
        <?php echo ReflexBadge::severity($alert['severity'] ?? 'info'); ?>
        <?php echo ReflexBadge::alertStatus($status); ?>
    </div>
    <dl class="reflex-meta">
        <div class="reflex-meta-item">
            <dt><?php echo _T("Probe", "reflex"); ?></dt>
            <dd><?php echo ReflexHelper::safeProduct($alert['probe_label'] ?? '', null); ?></dd>
        </div>
        <?php if ($instance !== ''): ?>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Measured on", "reflex"); ?></dt>
            <dd><?php echo ReflexHelper::safe($instance); ?></dd>
        </div>
        <?php endif; ?>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Value", "reflex"); ?></dt>
            <dd><?php echo ReflexBadge::value(
                $alert['value_at_trigger'] ?? null,
                $alert['value_text_at_trigger'] ?? null,
                $unit,
                $valueType
            ); ?></dd>
        </div>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Opened", "reflex"); ?></dt>
            <dd><?php echo ReflexHelper::formatDate($alert['opened_at'] ?? ''); ?></dd>
        </div>
        <?php
        // A first measure opens the alert and confirms it in the same breath.
        if ($confirmedAt !== '' && $confirmedAt !== $openedAt): ?>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Last confirmed", "reflex"); ?></dt>
            <dd><?php echo ReflexHelper::formatDate($alert['last_seen_at'] ?? ''); ?></dd>
        </div>
        <?php endif; ?>
        <?php if (!empty($alert['resolved_at'])): ?>
        <div class="reflex-meta-item reflex-meta-resolved">
            <dt><?php echo _T("Resolved", "reflex"); ?></dt>
            <dd><?php echo ReflexBadge::resolution($alert['resolved_at'], $alert['resolved_reason'] ?? ''); ?></dd>
        </div>
        <?php endif; ?>
    </dl>
</div>

<?php
// Shown whole here, next to its author; a table only shows its beginning.
if ($ackUser !== '' || $ackComment !== '') {
    $when = ReflexHelper::plainDate($alert['ack_at'] ?? '');
    if ($ackUser !== '' && $when !== '') {
        $ackHead = sprintf(_T("Acknowledged by %s on %s", "reflex"), $ackUser, $when);
    } elseif ($ackUser !== '') {
        $ackHead = sprintf(_T("Acknowledged by %s", "reflex"), $ackUser);
    } else {
        $ackHead = _T("Acknowledged", "reflex");
    }
    ?>
    <div class="reflex-ack">
        <div class="reflex-ack-head"><?php echo htmlspecialchars($ackHead, ENT_QUOTES, 'UTF-8'); ?></div>
        <?php if ($ackComment !== ''): ?>
        <div class="reflex-ack-comment"><?php echo htmlspecialchars($ackComment, ENT_QUOTES, 'UTF-8'); ?></div>
        <?php endif; ?>
    </div>
    <?php
}

// What the measure that raised the alert enumerated, frozen when it opened.
// A count alone does not say which entry it counted, and the machine sheet is
// too far from the screen where the question is asked.
$triggerItems = ReflexHelper::detailItems($alert['detail_at_trigger'] ?? '');
if (!empty($triggerItems)) {
    echo '<h3 class="reflex-section-title">'
       . _T("Detail of the triggering measure", "reflex") . '</h3>';
    echo '<ul class="reflex-trace">';
    foreach ($triggerItems as $item) {
        echo '<li><div class="reflex-trace-head"><span class="reflex-trace-name">'
           . ReflexHelper::safe($item) . '</span></div></li>';
    }
    echo '</ul>';
}

// The two halves of a condition, wherever it is read from. The frozen one
// carries the very keys of a condition row, so one rendering serves both.
function reflex_condition_fields($label, $condition, $unit, $valueType = '', $marks = '')
{
    return '<div class="reflex-meta-item"><dt>' . $label . '</dt><dd>'
        . ReflexHelper::describeCondition($condition, $unit, $valueType) . $marks . '</dd></div>'
        . '<div class="reflex-meta-item"><dt>' . htmlspecialchars(_T("Duration", "reflex")) . '</dt><dd>'
        . htmlspecialchars(ReflexHelper::formatInterval($condition['duration_seconds'] ?? 0)) . '</dd></div>';
}

$trustStatus = strtolower(trim((string) ($trust['status'] ?? '')));
// Only a certified alert carries the condition that fired. The flag and the
// frozen structure are both required.
$certified = !empty($trust['certified']) && !empty($frozen);
$movedFields = (isset($trust['condition_moved_fields']) && is_array($trust['condition_moved_fields']))
    ? $trust['condition_moved_fields'] : array();
// Computed by the backend, which compares the frozen severity with today's.
$severityMoved = !empty($trust['severity_moved']);
$severityNow = strtolower(trim((string) ($trust['severity_now'] ?? '')));
$evidence = (isset($trust['evidence']) && is_array($trust['evidence'])) ? $trust['evidence'] : array();

// The edit of a probe is not said at all: any change moves that column, a
// rename included.
$said = array('probe_edited_after_open', 'trigger_value_unsatisfied',
              'severity_moved', 'condition_disabled_now');
$conditionDeleted = ($certified && empty($condition));
if ($conditionDeleted) {
    $said[] = 'condition_deleted_now';
}
$notes = array();
foreach ($evidence as $key) {
    if (in_array($key, $said, true)) {
        continue;
    }
    $text = ReflexHelper::conditionEvidenceLabel($key, $movedFields);
    if ($text !== '') {
        $notes[] = $text;
    }
}

$sectionTitle = ($certified || (empty($condition) && empty($frozen)))
    ? _T("Condition that fired", "reflex")
    : _T("Condition", "reflex");
?>

<h3 class="reflex-section-title"><?php echo $sectionTitle; ?></h3>

<?php
if (empty($condition) && empty($frozen)) {
    // This alert froze nothing: there is no cause to show.
    echo '<p class="reflex-popup-empty">'
       . htmlspecialchars(_T("The condition that raised this alert does not exist any more.", "reflex"))
       . '</p>';
} else {
    // Values in force, adaptation included. The frozen condition carries its own.
    $effective = empty($condition) ? array() : ReflexHelper::conditionEffectiveRow($condition);
    $disabledNow = (!empty($effective) && empty($effective['enabled']));

    if (!$certified) {
        // An alert opened at 24 % displayed next to "greater than 85 %" reads as an
        // arithmetic the product never did.
        $notice = ReflexHelper::conditionTrustNotice($trustStatus);
        if ($notice !== '') {
            echo '<p class="reflex-condition-notice">'
               . ReflexTip::on(htmlspecialchars($notice, ENT_QUOTES, 'UTF-8'), $notes)
               . '</p>';
        }
    } else {
        // The explanation, and the only line that claims to be one.
        echo '<dl class="reflex-meta">'
           . reflex_condition_fields(htmlspecialchars(_T("Condition", "reflex")), $frozen, $unit, $valueType)
           . '</dl>';
    }

    if ($conditionDeleted) {
        $deleted = htmlspecialchars(
            ReflexHelper::conditionEvidenceLabel('condition_deleted_now'), ENT_QUOTES, 'UTF-8');
        echo '<p class="reflex-popup-empty">'
           . ReflexTip::on($deleted, $notes) . '</p>';
    } elseif (!empty($condition)) {
        // Read side by side without a word, two conditions are taken for one
        // repeated twice: the setting of today is shown only where it differs.
        $differs = (!empty($movedFields) || $severityMoved || $disabledNow);
        if (!$certified || $differs) {
            $label = htmlspecialchars($certified ? _T("Set today", "reflex") : _T("Condition", "reflex"));
            if ($certified) {
                $label = ReflexTip::on($label, $notes);
            }
            $marks = ReflexBadge::customized($condition, $unit)
                . ($disabledNow ? ' ' . ReflexBadge::enabled(0) : '');
            echo '<dl class="reflex-meta">'
               . reflex_condition_fields($label, $effective, $unit, $valueType, $marks);
            if ($severityMoved && $severityNow !== '') {
                echo '<div class="reflex-meta-item"><dt>'
                   . htmlspecialchars(_T("Severity now", "reflex")) . '</dt><dd>'
                   . ReflexBadge::severity($severityNow) . '</dd></div>';
            }
            echo '</dl>';
        }
    }
}

// Name of a channel as a trace line carries it, with the mark of a channel
// switched off: nothing more will leave by it.
function reflex_trace_channel($row, $tipLines = array())
{
    $name = trim((string) ($row['channel_name'] ?? ''));
    if ($name === '') {
        // No channel at all, as when no rule covers the probe.
        if (intval($row['channel_id'] ?? 0) <= 0) {
            return '';
        }
        // The joins are permissive: a channel deleted since costs its name, not the
        // trace of what it sent.
        return '<span class="reflex-muted">'
            . htmlspecialchars(_T("Deleted channel", "reflex")) . '</span>';
    }
    // The bubble hangs on the name alone.
    $cell = '<span class="reflex-trace-name">'
        . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . '</span>';
    if (!empty($tipLines)) {
        $cell = ReflexTip::on($cell, $tipLines);
    }
    if (array_key_exists('channel_enabled', $row) && empty($row['channel_enabled'])) {
        $cell .= ' ' . ReflexBadge::enabled(0);
    }
    return $cell;
}
?>

<h3 class="reflex-section-title"><?php echo _T("Notifications", "reflex"); ?></h3>

<?php
$noRuleOnly = empty($notifications) && !empty($skipped);
foreach ($skipped as $row) {
    if (strtolower(trim((string) ($row['skip_reason'] ?? ''))) !== 'no_rule_matches'
            || intval($row['channel_id'] ?? 0) > 0) {
        $noRuleOnly = false;
        break;
    }
}
if ($noRuleOnly) {
    $skipped = array();
    // The cause decides where it is fixed.
    $channels = xmlrpc_reflex_get_channels($login);
    $hasChannel = false;
    foreach ((is_array($channels) ? $channels : array()) as $channel) {
        if (is_array($channel)) {
            $hasChannel = true;
            break;
        }
    }
    $settingsTab = $hasChannel ? 'tabrules' : 'tabchannels';
    echo '<p class="reflex-popup-empty">' . htmlspecialchars($hasChannel
        ? _T("No rule covers this probe.", "reflex")
        : _T("No notification channel configured.", "reflex"));
    if (function_exists('hasCorrectTabAcl') && hasCorrectAcl('reflex', 'reflex', 'settings')
            && hasCorrectTabAcl('reflex', 'reflex', 'settings', $settingsTab)) {
        echo ' <a href="' . htmlspecialchars(urlStrRedirect('reflex/reflex/settings', array('tab' => $settingsTab)), ENT_QUOTES, 'UTF-8')
            . '">' . htmlspecialchars(_T("Configure", "reflex")) . '</a>';
    }
    echo '</p>';
} elseif (empty($notifications)) {
    echo '<p class="reflex-popup-empty">' . htmlspecialchars(empty($skipped)
        ? _T("No notification rule was triggered by this alert.", "reflex")
        : _T("Every sending was set aside, see below.", "reflex")) . '</p>';
} else {
    // What the rendered message adds is the wording that left the server, one
    // text for every channel: it belongs to the sendings, once.
    if ($alertMessage !== '') {
        echo '<div class="reflex-trace-message">'
           . '<span class="reflex-trace-message-label">'
           . htmlspecialchars(_T("Message sent", "reflex")) . '</span>'
           . htmlspecialchars($alertMessage, ENT_QUOTES, 'UTF-8')
           . '</div>';
    }
    echo '<ul class="reflex-trace">';
    foreach ($notifications as $row) {
        $rowStatus = strtolower(trim((string) ($row['status'] ?? '')));

        // The moment it accepted and the reference it gave back, which correlates
        // this line with its log.
        $statusLines = array();
        $accepted = ReflexHelper::plainDate($row['accepted_at'] ?? $row['sent_at'] ?? '');
        if ($rowStatus === 'sent' && $accepted !== '') {
            $statusLines[] = sprintf(_T("Accepted by the server on %s", "reflex"), $accepted);
        }
        $providerId = trim((string) ($row['provider_message_id'] ?? ''));
        if ($providerId !== '') {
            $statusLines[] = sprintf(_T("Reference given by the server: %s", "reflex"), $providerId);
        }
        $statusCell = ReflexBadge::notificationStatus($rowStatus);
        if (!empty($statusLines)) {
            $statusCell = ReflexTip::on($statusCell, $statusLines);
        }

        // A rule carries no name: what names it is what it targets.
        $ruleLines = array();
        $ruleLabel = empty($row['rule_all_probes'])
            ? trim(ReflexHelper::productText($row['rule_probe_label'] ?? '', null))
            : _T("All probes", "reflex");
        if ($ruleLabel !== '') {
            $ruleLines[] = sprintf(_T("Rule: %s", "reflex"), $ruleLabel);
        }
        $minSeverity = trim((string) ($row['rule_min_severity'] ?? ''));
        if ($minSeverity !== '') {
            $ruleLines[] = sprintf(_T("From severity %s", "reflex"),
                                   ReflexHelper::severityLabel($minSeverity));
        }
        $channelCell = reflex_trace_channel($row, $ruleLines);

        echo '<li>';
        echo '<div class="reflex-trace-head">';
        echo $statusCell;
        // A second notice is what the escalation sent because nobody took over.
        if (!empty($row['is_escalation'])) {
            echo ' <span class="reflex-escalation">'
               . htmlspecialchars(_T("Second notice", "reflex")) . '</span>';
        }
        echo ' ' . $channelCell;
        echo ' <span class="reflex-trace-when">'
           . ReflexHelper::formatDate($row['created_at'] ?? '') . '</span>';
        echo '</div>';

        // The addresses are shown, not counted.
        $recipients = trim((string) ($row['recipients'] ?? ''));
        if ($recipients !== '') {
            echo '<div class="reflex-trace-detail">'
               . htmlspecialchars($recipients, ENT_QUOTES, 'UTF-8') . '</div>';
        }

        // The reason says which form to open; the verbatim answer is a Python
        // exception kept for support. Without the first, "gaierror: [Errno -2] Name
        // or service not known" sent the reader to the network for a wrong host name.
        $error = trim((string) ($row['error_message'] ?? ''));
        $reason = ReflexHelper::skipReasonLabel($row['skip_reason'] ?? '', ($error === ''));
        if ($reason !== '') {
            echo '<div class="reflex-trace-error">'
               . htmlspecialchars($reason, ENT_QUOTES, 'UTF-8') . '</div>';
        }
        if ($error !== '') {
            if ($reason === '') {
                // The answer of the server is the only thing there is to read.
                echo '<div class="reflex-trace-error">'
                   . ReflexTip::on(htmlspecialchars($error, ENT_QUOTES, 'UTF-8'), array($error))
                   . '</div>';
            } else {
                // Said above in words. The verbatim answer stays, folded.
                echo '<details class="reflex-trace-detail-raw"><summary>'
                   . htmlspecialchars(_T("Technical detail", "reflex"), ENT_QUOTES, 'UTF-8')
                   . '</summary><div class="reflex-trace-raw-text">'
                   . htmlspecialchars($error, ENT_QUOTES, 'UTF-8')
                   . '</div></details>';
            }
        }

        $follow = array();
        $attempts = intval($row['attempt_count'] ?? 0);
        // A first notice is one attempt and says nothing worth a line.
        if ($attempts > 1) {
            $follow[] = ReflexHelper::attemptsLabel($attempts);
        }
        if (!empty($row['next_retry_at'])) {
            $follow[] = sprintf(_T("Next retry on %s", "reflex"),
                                ReflexHelper::plainDate($row['next_retry_at']));
        }
        if (!empty($follow)) {
            echo '<div class="reflex-trace-detail">'
               . htmlspecialchars(implode(' - ', $follow), ENT_QUOTES, 'UTF-8') . '</div>';
        }
        echo '</li>';
    }
    echo '</ul>';
}

// Grouped by the server: an alert that stays open is re-evaluated at every
// measure, and a week of a full disk is thousands of identical rows.
if (!empty($skipped)) {
    ?>
    <h3 class="reflex-section-title"><?php echo _T("Sendings set aside", "reflex"); ?></h3>
    <?php
    echo '<ul class="reflex-trace">';
    foreach ($skipped as $row) {
        $count = intval($row['occurrence_count'] ?? 0);
        echo '<li>';
        echo '<div class="reflex-trace-head">';
        echo reflex_trace_channel($row);
        echo ' <span class="reflex-trace-when">' . htmlspecialchars(($count === 1)
            ? _T("Set aside once", "reflex")
            : sprintf(_T("Set aside %d times", "reflex"), $count)) . '</span>';
        echo '</div>';
        // A reason this console does not word travels on as the server wrote it.
        $reason = ReflexHelper::skipReasonLabel($row['skip_reason'] ?? '');
        if ($reason !== '') {
            echo '<div class="reflex-trace-detail">'
               . htmlspecialchars($reason, ENT_QUOTES, 'UTF-8') . '</div>';
        }
        // A first notice is stored with no attempt count.
        $trailing = array();
        $attemptsText = ReflexHelper::attemptsLabel($row['attempt_count'] ?? 0);
        if ($attemptsText !== '') {
            $trailing[] = $attemptsText;
        }
        $span = ReflexHelper::timeSpan($row['first_at'] ?? '', $row['last_at'] ?? '');
        if ($span !== '') {
            $trailing[] = $span;
        }
        if (!empty($trailing)) {
            echo '<div class="reflex-trace-detail reflex-muted">'
               . htmlspecialchars(implode(' - ', $trailing), ENT_QUOTES, 'UTF-8') . '</div>';
        }
        echo '</li>';
    }
    echo '</ul>';
}

echo '</div>';

reflex_alert_popup_close();

// PopupWindow() injects this fragment after the page was drawn.
echo ReflexTip::script();
?>
