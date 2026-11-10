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
 * Reflex Module - HTML Components
 *
 * Reusable UI components for the reflex module. Every helper that renders
 * agent-provided data escapes it: hostnames, alert messages and measure
 * values are untrusted input.
 */

require_once("includes/UIComponents.php");
require_once("includes/PageGenerator.php");

// Window the data layer compares the two clocks over, its
// MACHINE_ACTIVITY_WINDOW_SECONDS.
if (!defined('REFLEX_DRIFT_WINDOW_SECONDS')) {
    define('REFLEX_DRIFT_WINDOW_SECONDS', 86400);
}

// Badges rendered in probe, alert and machine lists.
class ReflexBadge
{
    // Severity badge.
    public static function severity($severity)
    {
        $severity = strtolower((string) $severity);
        $known = array('info', 'medium', 'high', 'critical');
        if (!in_array($severity, $known)) {
            return '<span class="reflex-badge reflex-badge-unknown">'
                . htmlspecialchars(_T("Unknown", "reflex")) . '</span>';
        }
        return '<span class="reflex-badge reflex-badge-' . $severity . '">'
            . htmlspecialchars(ReflexHelper::severityLabel($severity)) . '</span>';
    }

    // Visibility badge: who sees the probe, private or shared.
    public static function visibility($visibility, $isBuiltin = 0)
    {
        $visibility = strtolower((string) $visibility);
        $known = array('private', 'entity', 'global');
        if (!in_array($visibility, $known)) {
            $visibility = 'private';
        }
        // A shipped probe is always in the catalog: both badges would say the
        // same thing twice.
        if (!empty($isBuiltin)) {
            return '<span class="reflex-visibility reflex-visibility-builtin">'
                . htmlspecialchars(_T("Built-in", "reflex")) . '</span>';
        }
        $label = ReflexHelper::visibilityLabel($visibility);
        return '<span class="reflex-visibility reflex-visibility-' . $visibility . '">'
            . htmlspecialchars($label) . '</span>';
    }

    // Alert status badge (open, ack, resolved).
    public static function alertStatus($status)
    {
        $status = strtolower((string) $status);
        $known = array('open', 'ack', 'resolved');
        if (!in_array($status, $known)) {
            $status = 'open';
        }
        return '<span class="reflex-state reflex-state-' . $status . '">'
            . htmlspecialchars(ReflexHelper::alertStatusLabel($status)) . '</span>';
    }

    // Closing of an alert: when it was resolved, and how.
    public static function resolution($at, $reason = '')
    {
        $date = ReflexHelper::formatDate($at);
        $label = ReflexHelper::resolvedReasonLabel($reason);
        if ($label === '') {
            if (empty($at) || strtotime($at) === false) {
                return $date;
            }
            return $date . '<span class="reflex-resolution-reason">'
                . htmlspecialchars(_T("Resolved automatically", "reflex")) . '</span>';
        }
        $title = sprintf(_T("Alert closed without returning to normal: %s", "reflex"), $label);
        return $date . '<span class="reflex-resolution-reason" title="'
            . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars($label) . '</span>';
    }

    // Collection anomaly marker, shown only when the reading went wrong.
    public static function collectionIssue($status, $probeType = '', $detail = '')
    {
        $status = strtolower(trim((string) $status));
        switch ($status) {
            case 'warning':
                $label = _T("Degraded reading", "reflex");
                $title = _T("The agent took this reading in degraded conditions.", "reflex");
                break;
            case 'error':
                $label = _T("Reading failed", "reflex");
                $title = _T("The agent could not take this reading on the machine.", "reflex");
                break;
            case 'unavailable':
                list($label, $title) = ReflexHelper::unavailableReading($probeType, $detail);
                break;
            default:
                // 'ok' and any status this console does not know: nothing to
                // signal rather than a verdict nobody can read.
                return '';
        }
        return ' <span class="reflex-state reflex-measure-' . $status . '" title="'
            . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars($label) . '</span>';
    }

    // Recipient count, the list itself living in the tooltip.
    public static function recipientList($recipients)
    {
        $raw = trim(str_replace(';', ',', (string) $recipients));
        $all = ($raw === '')
            ? array()
            : array_values(array_filter(array_map('trim', explode(',', $raw)), 'strlen'));
        if (empty($all)) {
            return '<span class="reflex-muted">-</span>';
        }

        $count = safeCount($all);
        $label = ($count === 1)
            ? _T("1 recipient", "reflex")
            : sprintf(_T("%d recipients", "reflex"), $count);

        // mydata carries the tooltip content, as everywhere else in Medulla
        // (.infomach pattern, styled by graph/css/tooltip.css).
        $lines = implode('<br/>', array_map(
            function ($address) {
                return htmlspecialchars($address, ENT_QUOTES, 'UTF-8');
            }, $all));
        return '<span class="reflex-recipients" mydata="'
            . htmlspecialchars($lines, ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars($label) . '</span>';
    }

    // Whether the probe measures somewhere on the reader estate, and therefore
    // works.
    public static function assignedOn($row)
    {
        if (empty($row['cadences'])) {
            return ReflexHelper::safe('');
        }
        return '<span class="reflex-state reflex-state-enabled">'
            . htmlspecialchars(_T("In service", "reflex")) . '</span>';
    }

    // Enabled / disabled badge, for a rule, a channel or a condition.
    public static function enabled($enabled)
    {
        if (!empty($enabled)) {
            return '<span class="reflex-state reflex-state-enabled">'
                . htmlspecialchars(_T("Enabled", "reflex")) . '</span>';
        }
        return '<span class="reflex-state reflex-state-disabled">'
            . htmlspecialchars(_T("Disabled", "reflex")) . '</span>';
    }

    // Mark on a condition whose alert settings were adapted locally.
    public static function customized($condition, $unit = '', $valueType = '')
    {
        if (!ReflexHelper::conditionIsCustomized($condition)) {
            return '';
        }
        return ' <span class="reflex-adapted" title="'
            . htmlspecialchars(ReflexHelper::conditionCustomizationTitle($condition, $unit, $valueType),
                               ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars(_T("Adapted", "reflex")) . '</span>';
    }

    // No collector of this probe runs on the system of this machine.
    public static function notMeasurable($probe)
    {
        if (!ReflexHelper::agentCannotMeasure($probe)) {
            return '';
        }
        return ' <span class="reflex-not-measurable" title="'
            . htmlspecialchars(
                _T("No collector of this probe covers the operating system of this machine: it will never report a measure here.", "reflex"),
                ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars(_T("Not measurable on this system", "reflex")) . '</span>';
    }

    // Exception badge: the probe reaches this machine through an assignment
    // but has been lifted on it.
    public static function excluded($reason = '', $by = '', $at = '')
    {
        $details = array();
        if (trim((string) $by) !== '') {
            $details[] = sprintf(_T("Excluded by %s", "reflex"), trim((string) $by));
        }
        $when = ReflexHelper::plainDate($at);
        if ($when !== '') {
            $details[] = $when;
        }
        if (trim((string) $reason) !== '') {
            $details[] = trim((string) $reason);
        }
        $title = implode(' - ', $details);
        $attr = ($title === '')
            ? ''
            : ' title="' . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '"';
        return '<span class="reflex-state reflex-state-excluded"' . $attr . '>'
            . htmlspecialchars(_T("Excluded", "reflex")) . '</span>';
    }

    // Measure value with its unit. Produced by an agent: escaped before rendering.
    public static function value($numeric, $text = null, $unit = '', $valueType = '')
    {
        if (ReflexHelper::isBooleanType($valueType)) {
            $flag = ReflexHelper::booleanText($numeric);
            if ($flag !== '') {
                return '<span class="reflex-value">' . htmlspecialchars($flag) . '</span>';
            }
            return '<span class="reflex-muted">-</span>';
        }
        // A value counted in seconds is a duration: printed raw it reads as
        // 7259, which tells nobody it means two hours.
        if ($unit === 's' && $numeric !== null && $numeric !== '' && is_numeric($numeric)) {
            return '<span class="reflex-value">'
                . htmlspecialchars(ReflexHelper::formatDuration($numeric)) . '</span>';
        }
        if ($numeric === null || $numeric === '') {
            $raw = ($text === null) ? '' : (string) $text;
        } else {
            $raw = ReflexHelper::displayNumber($numeric);
            if ($raw === '') {
                $raw = '0';
            }
        }
        if ($raw === '') {
            return '<span class="reflex-muted">-</span>';
        }
        $out = '<span class="reflex-value">' . htmlspecialchars($raw);
        $unitText = ReflexHelper::unitLabel($unit);
        if ($unitText !== '') {
            $out .= ' <span class="reflex-unit">' . htmlspecialchars($unitText) . '</span>';
        }
        $out .= '</span>';
        return $out;
    }

    // Probes cell of the machines list: the probes placed on the machine.
    public static function reporting($row)
    {
        if (ReflexHelper::reportingState($row) === 'unwatched') {
            return ReflexTip::on(
                '<span class="reflex-muted">'
                . htmlspecialchars(_T("Not watched", "reflex")) . '</span>',
                array(_T("No probe is measured on this machine.", "reflex"))
            );
        }
        return self::probesCount($row);
    }

    // Date of the last measure of a machine, in red with the length of the
    // silence when the server found the whole machine silent.
    public static function lastMeasure($row)
    {
        if (ReflexHelper::reportingState($row) === 'never') {
            return ReflexTip::on(
                '<span class="reflex-muted">' . htmlspecialchars(_T("No measure received", "reflex")) . '</span>',
                array(empty($row['config_acked'])
                    ? _T("The machine has never been reached: its configuration has not been delivered.", "reflex")
                    : _T("The machine received its configuration but has not reported anything yet.", "reflex"))
            );
        }
        $date = ReflexHelper::formatDate($row['last_measure_at'] ?? '');
        if (ReflexHelper::reportingState($row) !== 'silent') {
            return $date;
        }
        return ReflexTip::on(
            '<span class="reflex-silent-date">' . $date . '</span>',
            ReflexHelper::silenceLines($row)
        );
    }

    // Probes placed on a machine, in plain text.
    public static function probesCount($row)
    {
        $count = array_key_exists('probes_placed_count', $row)
            ? intval($row['probes_placed_count'])
            : intval($row['probes_count'] ?? 0);
        $text = htmlspecialchars(sprintf(
            dngettext("reflex", "%d probe", "%d probes", $count), $count
        ));
        return ($count > 0) ? $text : '<span class="reflex-muted">' . $text . '</span>';
    }

    // Mark on the assignment row of a probe that has stopped reporting.
    public static function probeSilence($probe)
    {
        if (ReflexHelper::reportingState($probe) !== 'silent') {
            return '';
        }
        return ' ' . ReflexTip::on(
            '<span class="reflex-stale">'
            . htmlspecialchars(_T("Silent", "reflex")) . '</span>',
            ReflexHelper::stalenessLines($probe['measure_age_seconds'] ?? null)
        );
    }

    // Counter badge, dimmed when the count is zero.
    public static function count($count, $severity)
    {
        $count = intval($count);
        if ($count <= 0) {
            return '<span class="reflex-muted">0</span>';
        }
        $severity = strtolower((string) $severity);
        return '<span class="reflex-badge reflex-badge-' . $severity . '">' . $count . '</span>';
    }

    // Outcome of one sending attempt.
    public static function notificationStatus($status)
    {
        $status = strtolower(trim((string) $status));
        $known = array('sent', 'failed', 'pending', 'skipped');
        if (!in_array($status, $known, true)) {
            // A status this console does not know travels on as it stands
            // rather than being read as a success or as a failure.
            return ReflexHelper::safe($status, _T("Unknown", "reflex"));
        }
        return '<span class="reflex-state reflex-notif-' . $status . '">'
            . htmlspecialchars(ReflexHelper::notificationStatusLabel($status)) . '</span>';
    }
}

// Label and formatting helpers shared by the reflex views.
class ReflexHelper
{
    // Visibility a new probe takes when its author says nothing.
    const DEFAULT_VISIBILITY = 'entity';

    // Longest command a scripted probe may carry, in characters. Mirrors
    // SCRIPT_COMMAND_MAX_LENGTH of the reflex database module, which refuses
    // anything longer: the console says so before the call rather than after.
    const SCRIPT_COMMAND_MAX_LENGTH = 4000;

    // Script tag of a module file, versioned by its modification time so a
    // browser never keeps a stale copy after an update.
    public static function scriptTag($file, $defer = false)
    {
        $file = basename((string) $file);
        $mtime = @filemtime(__DIR__ . '/../graph/js/' . $file);
        $src = 'modules/reflex/graph/js/' . rawurlencode($file) . ($mtime ? '?v=' . $mtime : '');
        return '<script src="' . htmlspecialchars($src, ENT_QUOTES, 'UTF-8') . '"'
            . ($defer ? ' defer' : '') . '></script>';
    }

    // Wiring shared by the filtered lists. AjaxFilter freezes its own address
    // when the page is written and AjaxNavBar builds its links on that frozen
    // one, so every call rebuilds it from what the fields hold now.
    // $urlFunction names a page function returning the address without filter.
    // Related: the framework names the pagination line "Elements" in English and
    // out of any catalog, hence the setName() every list of this module calls.
    public static function ajaxListScript($urlFunction, $updateFunction)
    {
        $url = preg_replace('/[^A-Za-z0-9_]/', '', (string) $urlFunction);
        $update = preg_replace('/[^A-Za-z0-9_]/', '', (string) $updateFunction);
        return <<<JS
function reflexListSearchTerm() {
    var filterInput = document.querySelector('input[name="param"]');
    return filterInput ? filterInput.value : '';
}

function {$update}() {
    jQuery('#container').load(
        {$url}() + '&filter=' + encodeURIComponent(reflexListSearchTerm()));
}

// Search button.
updateSearch = function () {
    jQuery('#container').load(
        {$url}()
        + '&filter=' + encodeURIComponent(reflexListSearchTerm())
        + '&maxperpage=' + maxperpage);
};

// Pagination links.
updateSearchParam = function (filter, start, end, max) {
    jQuery('#container').load(
        {$url}()
        + '&filter=' + encodeURIComponent(filter)
        + '&start=' + start
        + '&end=' + end
        + '&maxperpage=' + max);
};
JS;
    }

    public static function severityLabel($severity)
    {
        switch (strtolower((string) $severity)) {
            case 'critical':
                return _T("Critical", "reflex");
            case 'high':
                return _T("High", "reflex");
            case 'medium':
                return _T("Medium", "reflex");
            case 'info':
                return _T("Info", "reflex");
        }
        return _T("Unknown", "reflex");
    }

    public static function severityOptions()
    {
        return array(
            'info' => _T("Info", "reflex"),
            'medium' => _T("Medium", "reflex"),
            'high' => _T("High", "reflex"),
            'critical' => _T("Critical", "reflex")
        );
    }

    // Refusal of a write, worded by the server when it said why.
    public static function notifyRefusal($answer, $fallback)
    {
        new NotifyWidgetFailure(self::refusalMessage(self::callRefusal($answer), $fallback));
    }

    // Outcome of a write. true and 1 both mean written.
    public static function notifyOutcome($result, $success, $fallback)
    {
        if ($result === true || $result === 1) {
            new NotifyWidgetSuccess($success);
            return true;
        }
        self::notifyRefusal($result, $fallback);
        return false;
    }

    // The instance column only exists where there is something to tell apart,
    // decided by the server on the whole filtered result so it does not come
    // and go from one page to the next. A server that does not say keeps it.
    public static function hasInstances($result)
    {
        return (is_array($result) && array_key_exists('has_instance', $result))
            ? !empty($result['has_instance']) : true;
    }

    // Icons every alert list carries: the alert itself, its machine, its probe.
    // A popup rather than a page: the list keeps its filters.
    public static function alertActions()
    {
        $alert = new ActionPopupItem(_T("View alert", "reflex"), "ajaxAlertDetail", "display", "", "reflex", "reflex");
        $alert->setWidth(600);
        return array(
            $alert,
            new ActionItem(_T("View supervision", "reflex"), "machineDetail", "monit", "", "reflex", "reflex"),
            new ActionItem(_T("View probe", "reflex"), "probeDetail", "reflexprobe", "", "reflex", "reflex")
        );
    }

    // Severity a list is filtered on, empty meaning every severity.
    public static function severityFilter($raw)
    {
        $severity = (string) $raw;
        $known = self::severityOptions();
        return ($severity !== '' && !isset($known[$severity])) ? '' : $severity;
    }

    // Probe a list is restricted to, 0 being the whole estate.
    public static function probeFilter($raw)
    {
        $probeId = intval($raw);
        return ($probeId < 0) ? 0 : $probeId;
    }

    public static function alertStatusLabel($status)
    {
        switch (strtolower((string) $status)) {
            case 'open':
                return _T("Open", "reflex");
            case 'ack':
                return _T("Acknowledged", "reflex");
            case 'resolved':
                return _T("Resolved", "reflex");
        }
        return _T("Unknown", "reflex");
    }

    // Reason an alert was closed.
    public static function resolvedReasonLabel($reason)
    {
        $reason = trim((string) $reason);
        if ($reason === '') {
            return '';
        }
        // Two distinct wordings on purpose: reading the history, knowing
        // whether the probe was excepted on this machine alone or whether the
        // whole assignment was dropped is not the same information.
        $known = array(
            'probe_removed' => _T("Probe removed from this machine", "reflex"),
            'probe_excluded' => _T("Probe excluded on this machine", "reflex"),
            'probe_unassigned' => _T("Probe assignment removed", "reflex"),
            'probe_out_of_scope' => _T("Probe no longer reaches this machine", "reflex"),
            'condition_changed' => _T("Condition changed", "reflex"),
            'condition_disabled' => _T("Condition switched off", "reflex"),
            'condition_removed' => _T("Condition removed", "reflex"),
            'superseded' => _T("Superseded by a more severe alert", "reflex")
        );
        $key = strtolower($reason);
        return isset($known[$key]) ? $known[$key] : $reason;
    }

    // Outcome of one sending attempt, in words.
    public static function notificationStatusLabel($status)
    {
        switch (strtolower(trim((string) $status))) {
            case 'sent':
                // Accepted by the remote server, which is all that is known:
                // delivery and reading are not.
                return _T("Accepted", "reflex");
            case 'failed':
                return _T("Failed", "reflex");
            case 'pending':
                return _T("Waiting", "reflex");
            case 'skipped':
                return _T("Not sent", "reflex");
        }
        return _T("Unknown", "reflex");
    }

    // Why a sending did not happen, or why it failed.
    public static function skipReasonLabel($reason, $fallbackToKey = true)
    {
        $reason = trim((string) $reason);
        if ($reason === '') {
            return '';
        }
        $known = array(
            'cooldown' => _T("The rule had just notified: its anti-repetition delay was still running.", "reflex"),
            'severity_below_min' => _T("This alert is below the minimum severity the rule requires.", "reflex"),
            'rule_disabled' => _T("The notification rule is switched off.", "reflex"),
            'channel_disabled' => _T("The channel is switched off.", "reflex"),
            'target_not_matched' => _T("This machine is outside the scope of the rule.", "reflex"),
            'channel_type_unsupported' => _T("The server cannot send on this type of channel.", "reflex"),
            'no_rule_matches' => _T("No rule covers this probe.", "reflex"),
            'retry_attempts_exhausted' => _T("Resending abandoned: no attempt got through.", "reflex"),
            'retry_alert_resolved' => _T("The alert closed before the resending got through.", "reflex"),
            'retry_rule_unavailable' => _T("The rule or its channel no longer exists: the resending was abandoned.", "reflex"),
            'retry_target_not_matched' => _T("This machine left the scope of the rule before the resending.", "reflex"),
            'rule_no_recipient' => _T("The rule names no recipient: nothing was sent.", "reflex"),
            'channel_entity_mismatch' => _T("This machine belongs to another entity than the channel: the alert is not sent outside its own entity.", "reflex"),
            'retry_channel_entity_mismatch' => _T("This machine belongs to another entity than the channel: the resending was abandoned.", "reflex"),
            // Corrected on the form of the channel.
            'channel_no_host' => _T("No SMTP server is set on this channel.", "reflex"),
            'channel_no_sender' => _T("No sender address is set on this channel.", "reflex"),
            'channel_no_recipient' => _T("No recipient: nothing was sent.", "reflex"),
            'channel_password_unreadable' => _T("The password of this channel cannot be read.", "reflex"),
            // Corrected on the mail server, or with whoever runs it.
            'smtp_host_unknown' => _T("The name of the SMTP server does not resolve.", "reflex"),
            'smtp_connect_refused' => _T("The SMTP server refused the connection.", "reflex"),
            'smtp_unreachable' => _T("The SMTP server cannot be reached.", "reflex"),
            'smtp_timeout' => _T("The SMTP server did not answer in time.", "reflex"),
            'smtp_tls_failed' => _T("The encrypted connection could not be established.", "reflex"),
            'smtp_auth_refused' => _T("The SMTP server refused the account.", "reflex"),
            'smtp_sender_refused' => _T("The SMTP server refused the sender address.", "reflex"),
            'smtp_recipients_refused' => _T("The SMTP server refused every recipient.", "reflex"),
            'smtp_connection_lost' => _T("The connection with the SMTP server was lost while sending.", "reflex"),
            'smtp_server_error' => _T("The SMTP server answered with an error of its own.", "reflex"),
            'smtp_error' => _T("The exchange with the SMTP server failed.", "reflex")
        );
        $key = strtolower($reason);
        if (isset($known[$key])) {
            return $known[$key];
        }
        return $fallbackToKey ? $reason : '';
    }

    // How many times a sending was attempted.
    public static function attemptsLabel($count)
    {
        $count = intval($count);
        if ($count <= 0) {
            return '';
        }
        return ($count === 1)
            ? _T("1 attempt", "reflex")
            : sprintf(_T("%d attempts", "reflex"), $count);
    }

    // Span covered by a group of identical rows.
    public static function timeSpan($first, $last)
    {
        $from = empty($first) ? false : strtotime((string) $first);
        $to = empty($last) ? false : strtotime((string) $last);
        if ($from === false && $to === false) {
            return '';
        }
        if ($from === false || $to === false) {
            return date('d/m/Y H:i', ($from === false) ? $to : $from);
        }
        if (date('d/m/Y H:i', $from) === date('d/m/Y H:i', $to)) {
            return date('d/m/Y H:i', $from);
        }
        if (date('d/m/Y', $from) === date('d/m/Y', $to)) {
            return sprintf(_T("%s, from %s to %s", "reflex"),
                           date('d/m/Y', $from), date('H:i', $from), date('H:i', $to));
        }
        return sprintf(_T("from %s to %s", "reflex"),
                       date('d/m/Y H:i', $from), date('d/m/Y H:i', $to));
    }

    public static function visibilityLabel($visibility)
    {
        switch (strtolower((string) $visibility)) {
            case 'private':
                return _T("Private", "reflex");
            case 'entity':
                return _T("Shared", "reflex");
            case 'global':
                // Written by no code path any more, kept for stored rows.
                return _T("Catalog", "reflex");
        }
        return _T("Unknown", "reflex");
    }

    // Visibilities a probe can be created with or moved to.
    public static function visibilityOptions()
    {
        return array(
            'private' => _T("Private", "reflex"),
            'entity' => _T("Shared", "reflex")
        );
    }

    // Who sees a probe, in one sentence.
    public static function visibilityHint($visibility, $entityId = null)
    {
        $visibility = strtolower((string) $visibility);
        if ($visibility === 'private') {
            return _T("Visible to you only.", "reflex");
        }
        if ($visibility !== 'entity') {
            return '';
        }
        $entities = ReflexTargets::entityOptions();
        $id = ReflexTargets::identifier($entityId);
        if ($id !== null && isset($entities[$id])) {
            return sprintf(_T("Visible to the users of %s.", "reflex"), $entities[$id]);
        }
        return _T("Visible to the users of its entity.", "reflex");
    }

    // Renders an alert message template, highlighting its @@markers@@.
    public static function messageTemplate($template)
    {
        $safe = htmlspecialchars((string) $template, ENT_QUOTES, 'UTF-8');
        return preg_replace(
            '/@@([a-z_]+)@@/i',
            '<span class="reflex-tpl-var">$0</span>',
            $safe
        );
    }

    // Subsets of probes the list filter offers.
    public static function probeFilterOptions()
    {
        return array(
            'all' => _T("All probes", "reflex"),
            'mine' => _T("My probes", "reflex"),
            'entity' => _T("Shared probes", "reflex"),
            'catalog' => _T("Catalog probes", "reflex")
        );
    }

    // Whether a probe row is measured somewhere on the reader estate.
    public static function isPlaced($row)
    {
        return !empty($row['cadences']);
    }

    // Where a probe stands on the estate of the reader, in one sentence.
    public static function placementSentence($assignedEntities, $readerEntities)
    {
        $placed = intval($assignedEntities);
        $total = intval($readerEntities);
        if ($placed <= 0 || $total <= 0) {
            return '';
        }
        if ($placed >= $total) {
            return _T("Placed on your whole estate.", "reflex");
        }
        return sprintf(_T("Placed on %1\$d of your %2\$d entities.", "reflex"), $placed, $total);
    }

    // Options of the probe selector of the alert pages, sorted by label.
    public static function probeSelectOptions($login, $placedOnly, $currentId = 0)
    {
        $options = array();
        foreach (reflex_probe_rows($login) as $row) {
            $id = intval($row['id'] ?? 0);
            if ($id > 0 && (!$placedOnly || self::isPlaced($row))) {
                $options[$id] = self::productText($row['label'] ?? '', !empty($row['is_builtin']));
            }
        }
        $currentId = intval($currentId);
        if ($currentId > 0 && !isset($options[$currentId])) {
            $detail = xmlrpc_reflex_get_probe($login, $currentId);
            $probe = (is_array($detail) && isset($detail['probe']) && is_array($detail['probe']))
                ? $detail['probe'] : array();
            $options[$currentId] = !empty($probe['label'])
                ? self::productText($probe['label'], !empty($probe['is_builtin']))
                : _T("Probe not found", "reflex");
        }
        uasort($options, function ($a, $b) {
            return strcmp(ReflexHelper::fold($a), ReflexHelper::fold($b));
        });
        return $options;
    }

    public static function categoryOptions()
    {
        return array(
            'system' => _T("System", "reflex"),
            'security' => _T("Security", "reflex"),
            'network' => _T("Network", "reflex"),
            'storage' => _T("Storage", "reflex"),
            'service' => _T("Service", "reflex"),
            'application' => _T("Application", "reflex")
        );
    }

    public static function categoryLabel($category)
    {
        $options = self::categoryOptions();
        $key = strtolower((string) $category);
        return isset($options[$key]) ? $options[$key] : (string) $category;
    }

    public static function valueTypeOptions()
    {
        return array(
            'numeric' => _T("Numeric", "reflex"),
            'text' => _T("Text", "reflex"),
            'boolean' => _T("Boolean", "reflex")
        );
    }

    public static function operatorOptions()
    {
        return array(
            'gt' => _T("greater than", "reflex"),
            'gte' => _T("greater than or equal to", "reflex"),
            'lt' => _T("less than", "reflex"),
            'lte' => _T("less than or equal to", "reflex"),
            'eq' => _T("equal to", "reflex"),
            'ne' => _T("different from", "reflex"),
            'between' => _T("between", "reflex"),
            'outside' => _T("outside", "reflex"),
            'changed' => _T("changed", "reflex")
        );
    }

    // Operator as a symbol, for the compact notation of a list.
    public static function operatorSymbol($operator)
    {
        $symbols = array('gt' => '>', 'gte' => '≥', 'lt' => '<', 'lte' => '≤', 'eq' => '=', 'ne' => '≠');
        $key = strtolower((string) $operator);
        return isset($symbols[$key]) ? $symbols[$key] : self::operatorLabel($operator);
    }

    // Unit of a probe as the reader writes it: the catalog stores short keys,
    // a personal probe stores what its author typed.
    public static function unitLabel($unit)
    {
        $unit = trim((string) $unit);
        switch ($unit) {
            case 'count':
                return '';
            case 'd':
                return _T("d", "reflex");
        }
        return $unit;
    }

    public static function operatorLabel($operator)
    {
        $options = self::operatorOptions();
        $key = strtolower((string) $operator);
        return isset($options[$key]) ? $options[$key] : (string) $operator;
    }

    public static function targetTypeOptions()
    {
        return array(
            'all' => _T("All machines", "reflex"),
            'machine' => _T("Machine", "reflex"),
            'group' => _T("Group", "reflex"),
            'entity' => _T("Entity", "reflex")
        );
    }

    public static function targetTypeLabel($targetType)
    {
        $options = self::targetTypeOptions();
        $key = strtolower((string) $targetType);
        return isset($options[$key]) ? $options[$key] : (string) $targetType;
    }

    public static function channelTypeOptions()
    {
        return array(
            'email' => _T("Email", "reflex"),
            'telegram' => _T("Telegram", "reflex"),
            'webhook' => _T("Webhook", "reflex"),
            'slack' => _T("Slack", "reflex"),
            'teams' => _T("Teams", "reflex"),
            'sms' => _T("SMS", "reflex"),
            'whatsapp' => _T("WhatsApp", "reflex")
        );
    }

    public static function channelTypeLabel($channelType)
    {
        $options = self::channelTypeOptions();
        $key = strtolower((string) $channelType);
        return isset($options[$key]) ? $options[$key] : (string) $channelType;
    }

    // Operating systems of the reflex schema, in a stable display order.
    public static function osOptions()
    {
        return array(
            'windows' => _T("Windows", "reflex"),
            'linux' => _T("Linux", "reflex"),
            'darwin' => _T("macOS", "reflex")
        );
    }

    public static function osLabel($os)
    {
        $options = self::osOptions();
        $key = strtolower((string) $os);
        return isset($options[$key]) ? $options[$key] : (string) $os;
    }

    // Split a probes.os_support set value into a normalised list.
    public static function parseOsSupport($osSupport)
    {
        $list = array();
        foreach (explode(',', (string) $osSupport) as $os) {
            $os = strtolower(trim($os));
            if ($os !== '') {
                $list[] = $os;
            }
        }
        return array_values(array_unique($list));
    }

    // Verdict the server took on whether something still reports.
    public static function reportingState($data)
    {
        if (!is_array($data)) {
            return '';
        }
        $state = strtolower(trim((string) (
            $data['reporting_state'] ?? ($data['state'] ?? '')
        )));
        $known = array('reporting', 'partial', 'silent', 'never',
                       'unwatched', 'unknown');
        return in_array($state, $known, true) ? $state : '';
    }

    // How long the silence has lasted, in words.
    public static function silenceLines($data)
    {
        $silence = isset($data['silence_seconds']) ? $data['silence_seconds'] : null;
        return array(($silence === null || $silence === '')
            ? _T("No measure received for over a day.", "reflex")
            : sprintf(_T("Nothing received for %s.", "reflex"),
                      self::formatDuration($silence)));
    }

    // Age of a value.
    public static function stalenessLines($age)
    {
        return array(($age === null || $age === '')
            ? _T("No measure received for over a day.", "reflex")
            : sprintf(_T("Received %s ago.", "reflex"),
                      self::formatDuration($age)));
    }

    // Common measurement intervals offered in the assignment form.
    public static function intervalOptions()
    {
        return array(
            300 => _T("5 minutes", "reflex"),
            900 => _T("15 minutes", "reflex"),
            1800 => _T("30 minutes", "reflex"),
            3600 => _T("1 hour", "reflex"),
            21600 => _T("6 hours", "reflex"),
            86400 => _T("1 day", "reflex")
        );
    }

    // Shortest cadence the console can offer. Read from the list itself: it is
    // the only place a cadence is decided.
    public static function shortestInterval()
    {
        return min(array_keys(self::intervalOptions()));
    }

    // Retention periods offered, the stored one included when it is not
    // listed.
    public static function retentionChoices($days, $current)
    {
        $current = intval($current);
        if ($current > 0 && !in_array($current, $days, true)) {
            $days[] = $current;
            sort($days);
        }
        $choices = array();
        foreach ($days as $day) {
            $choices[$day] = ($day % 365 === 0)
                ? sprintf(dngettext("reflex", "%d year", "%d years", $day / 365), $day / 365)
                : sprintf(dngettext("reflex", "%d day", "%d days", $day), $day);
        }
        return $choices;
    }

    // Human readable duration.
    public static function formatInterval($seconds)
    {
        $seconds = intval($seconds);
        if ($seconds <= 0) {
            return _T("Immediate", "reflex");
        }
        if ($seconds % 86400 === 0) {
            return sprintf(_T("%d d", "reflex"), $seconds / 86400);
        }
        if ($seconds % 3600 === 0) {
            return sprintf(_T("%d h", "reflex"), $seconds / 3600);
        }
        if ($seconds % 60 === 0) {
            return sprintf(_T("%d min", "reflex"), $seconds / 60);
        }
        return sprintf(_T("%d s", "reflex"), $seconds);
    }

    // Measured duration, rendered with at most two units. Distinct from
    // formatInterval(), which formats a cadence picked from a closed list.
    public static function formatDuration($seconds)
    {
        if (!is_numeric($seconds)) {
            return sprintf(_T("%d s", "reflex"), 0);
        }
        $seconds = (int) round((float) $seconds);
        if ($seconds <= 0) {
            return sprintf(_T("%d s", "reflex"), 0);
        }
        if ($seconds < 60) {
            return sprintf(_T("%d s", "reflex"), $seconds);
        }

        // The last unit shown is rounded, not truncated: 7259 s is two hours
        // and one minute short of a second, and reads better as 2 h 01 than as
        // 2 h 00.
        $minutes = (int) round($seconds / 60);
        if ($minutes < 60) {
            return sprintf(_T("%d min", "reflex"), $minutes);
        }
        if (intdiv($minutes, 60) < 24) {
            return sprintf(_T("%d h %02d", "reflex"),
                           intdiv($minutes, 60), $minutes % 60);
        }
        $hours = (int) round($seconds / 3600);
        return sprintf(_T("%d d %02d h", "reflex"),
                       intdiv($hours, 24), $hours % 24);
    }

    // Date coming from the database, rendered in the local short format.
    public static function formatDate($value)
    {
        if (empty($value)) {
            return '<span class="reflex-muted">-</span>';
        }
        $ts = strtotime($value);
        if ($ts === false) {
            return '<span class="reflex-muted">-</span>';
        }
        return htmlspecialchars(date('d/m/Y H:i', $ts));
    }

    // Same date, as plain text: used inside attributes, where the markup of
    // formatDate() would be printed literally.
    public static function plainDate($value)
    {
        if (empty($value)) {
            return '';
        }
        $ts = strtotime($value);
        if ($ts === false) {
            return '';
        }
        return date('d/m/Y H:i', $ts);
    }

    // One end of a period, as the backend reads it, or an empty string.
    public static function periodBound($value)
    {
        $value = trim((string) $value);
        if ($value === '') {
            return '';
        }
        if (!preg_match('/^(\d{4})-(\d{2})-(\d{2})$/', $value, $parts)) {
            return '';
        }
        if (!checkdate((int) $parts[2], (int) $parts[3], (int) $parts[1])) {
            return '';
        }
        return $value;
    }

    // Period shown in the range field: "dd/mm/yyyy -> dd/mm/yyyy", one date
    // when both bounds are the same day, empty when there is none.
    public static function rangeText($from, $to)
    {
        $show = function ($day) {
            return $day !== '' ? date('d/m/Y', strtotime($day)) : '';
        };
        if ($from === '' && $to === '') {
            return '';
        }
        if ($from === $to) {
            return $show($from);
        }
        return trim($show($from) . " \u{2192} " . $show($to));
    }

    // Normalise what reflex.test_channel returns.
    public static function testChannelOutcome($result, $recipient = '')
    {
        $sent = function ($accepted) use ($recipient, $result) {
            $address = (is_array($accepted) && !empty($accepted))
                ? implode(', ', array_map('strval', $accepted))
                : (is_scalar($accepted) && (string) $accepted !== '' ? (string) $accepted : (string) $recipient);
            return array(
                'success' => true,
                'attempted' => self::testSendAttempted($result, '', true),
                'message' => htmlspecialchars(sprintf(_T("Test message sent to %s.", "reflex"), $address)),
                'field' => ''
            );
        };

        if ($result === true || $result === 1) {
            return $sent(null);
        }

        if (is_array($result)) {
            if (!empty($result['success'])) {
                return $sent($result['accepted'] ?? null);
            }

            $field = trim((string) ($result['field'] ?? ''));
            $details = (!empty($result['details']) && is_array($result['details']))
                ? $result['details'] : array();
            // The server names the family of the failure; its own text is a
            // Python exception, readable only by whoever already knows it.
            if (!empty($result['reason'])) {
                $reasonKey = strtolower(trim((string) $result['reason']));
                // A test is sent to the one address typed here: the sentence
                // names it rather than trailing it after a full stop, and the
                // typed value answers when the server named none.
                $aboutAddresses = ($reasonKey === 'email_invalid' || $reasonKey === 'test_recipient_single');
                if ($aboutAddresses && empty($details) && (string) $recipient !== '') {
                    $details = array($recipient);
                }
                if ($reasonKey === 'email_invalid') {
                    return array(
                        'success' => false,
                        'attempted' => self::testSendAttempted($result, $reasonKey),
                        'message' => htmlspecialchars(self::invalidAddressText($details)),
                        'field' => $field
                    );
                }
                // Several addresses, all valid: the rule is said, then what
                // was typed, introduced instead of trailing a full stop.
                if ($reasonKey === 'test_recipient_single') {
                    $message = htmlspecialchars(self::refusalReasonText($reasonKey));
                    $typed = self::addressList($details);
                    if (!empty($typed)) {
                        $message .= '<br/>' . htmlspecialchars(sprintf(
                            _T("Addresses typed: %s", "reflex"), implode(', ', $typed)));
                    }
                    return array('success' => false,
                                 'attempted' => self::testSendAttempted($result, $reasonKey),
                                 'message' => $message, 'field' => $field);
                }
                $said = self::skipReasonLabel($reasonKey, false);
                if ($said === '') {
                    $said = self::refusalReasonText($reasonKey);
                }
                if ($said !== '') {
                    $message = htmlspecialchars($said);
                    if (!empty($details)) {
                        $message .= '<br/>' . htmlspecialchars(implode(', ', array_map('strval', $details)));
                    }
                    return array('success' => false,
                                 'attempted' => self::testSendAttempted($result, $reasonKey),
                                 'message' => $message, 'field' => $field);
                }
            }
            if (!empty($result['error'])) {
                return array('success' => false,
                             'attempted' => self::testSendAttempted($result),
                             'message' => htmlspecialchars((string) $result['error']),
                             'field' => $field);
            }
        }

        return array(
            'success' => false,
            'attempted' => self::testSendAttempted($result, '', true),
            'message' => htmlspecialchars(_T("The mail server did not accept the message, without giving a reason.", "reflex")),
            'field' => ''
        );
    }

    // Whether the test message was really handed over to the mail server.
    private static function testSendAttempted($result, $reason = '', $whenUnsaid = false)
    {
        if (is_array($result) && array_key_exists('attempted', $result)) {
            return !empty($result['attempted']);
        }
        return $whenUnsaid || strpos(strtolower(trim((string) $reason)), 'smtp_') === 0;
    }

    // Comparable form of a text: the operator types neither the case nor the
    // accents of what he reads, and sorting on the stored bytes would send
    // every accented initial past the letter z.
    public static function fold($text)
    {
        $text = mb_strtolower((string) $text, 'UTF-8');
        return strtr($text, array(
            'á' => 'a', 'à' => 'a', 'â' => 'a', 'ä' => 'a', 'ã' => 'a', 'å' => 'a',
            'é' => 'e', 'è' => 'e', 'ê' => 'e', 'ë' => 'e',
            'í' => 'i', 'ì' => 'i', 'î' => 'i', 'ï' => 'i',
            'ó' => 'o', 'ò' => 'o', 'ô' => 'o', 'ö' => 'o', 'õ' => 'o',
            'ú' => 'u', 'ù' => 'u', 'û' => 'u', 'ü' => 'u',
            'ç' => 'c', 'ñ' => 'n', 'ý' => 'y', 'ÿ' => 'y'
        ));
    }

    // Escape a value produced by an agent (hostname, message, text measure).
    public static function safe($value, $fallback = '-')
    {
        if ($value === null || $value === '') {
            return '<span class="reflex-muted">' . htmlspecialchars($fallback) . '</span>';
        }
        return htmlspecialchars((string) $value);
    }

    // =========================================================================
    // Catalog shipped with the product
    //
    // The names and descriptions of the probes shipped with the product, and
    // the default message of their conditions, are stored in the database in
    // English, in one version and one only. That version is the translation
    // key: it is passed through _T() at display time, and the language of the
    // session decides what is shown. The database is never translated, so a
    // measure, a notification and a console all read the same row.
    //
    // A string that no catalog holds comes back from dgettext() as it went
    // in, which is the English of the database: nothing breaks and nothing is
    // blank when a translation is missing.
    //
    // WHAT IS NOT TRANSLATED is what an operator typed: his own probes, and
    // the message he adapted on a shipped condition. See productText() for
    // how the two are told apart.
    //
    // The shipped strings are not in the code: they are kept by hand in
    // reflex.pot and the .po files.
    // =========================================================================

    // A string of the catalog, in the language of the session.
    public static function productText($text, $isProduct = true)
    {
        $text = (string) $text;
        // dgettext('') answers the header of the catalog, not an empty string:
        // an empty description would print the metadata block.
        if ($text === '' || $isProduct === false) {
            return $text;
        }
        return _T($text, 'reflex');
    }

    // Same, escaped, with the dash the module shows for an absent value.
    public static function safeProduct($value, $isProduct = true, $fallback = '-')
    {
        if ($value === null || $value === '') {
            return self::safe($value, $fallback);
        }
        return self::safe(self::productText($value, $isProduct), $fallback);
    }

    // Alert message of a condition, in the language of the session when the
    // product ships it.
    public static function conditionMessage($condition, $isProduct = true)
    {
        $override = (is_array($condition) && isset($condition['message_template']))
            ? $condition['message_template'] : null;
        $default = self::conditionDefault($condition, 'message_template');
        if ($override !== null && trim((string) $override) !== ''
            && !self::sameConditionValue('message_template', $override, $default)) {
            return (string) $override;
        }
        return self::productText($default, $isProduct);
    }

    // Enabled conditions of a probe row of get_probes, compact, one per line.
    public static function conditionsSummary($row)
    {
        $unit = (string) ($row['unit'] ?? '');
        $valueType = (string) ($row['value_type'] ?? '');
        $lines = array();
        foreach ((is_array($row['conditions'] ?? null) ? $row['conditions'] : array()) as $condition) {
            if (is_array($condition) && !empty($condition['enabled'])) {
                $lines[] = htmlspecialchars(self::describeConditionText($condition, $unit, $valueType, true));
            }
        }
        return empty($lines) ? self::safe('') : implode('<br>', $lines);
    }

    // Human readable condition, used in the probe detail page.
    public static function describeCondition($condition, $unit = '', $valueType = '')
    {
        return htmlspecialchars(self::describeConditionText($condition, $unit, $valueType));
    }

    // Same wording as plain text, for a tooltip attribute where the markup of
    // describeCondition() would be escaped a second time and printed.
    public static function describeConditionText($condition, $unit = '', $valueType = '', $compact = false)
    {
        $operator = isset($condition['operator']) ? $condition['operator'] : '';
        $label = $compact ? self::operatorSymbol($operator) : self::operatorLabel($operator);
        // Compact: a state compared for equality is written alone.
        $stateLabel = ($compact && strtolower((string) $operator) === 'eq') ? '' : $label;
        $unitText = self::unitLabel($unit);
        $suffix = ($unitText !== '') ? ' ' . $unitText : '';

        if (self::isBooleanType($valueType) && $operator !== 'changed') {
            $flag = self::booleanText($condition['threshold_value'] ?? null);
            if ($flag !== '' && !$compact && ($operator === 'eq' || $operator === 'ne')) {
                $isYes = ($flag === _T("Yes", "reflex"));
                if ($operator === 'eq') {
                    return $isYes ? _T("is Yes", "reflex") : _T("is No", "reflex");
                }
                return $isYes ? _T("is not Yes", "reflex") : _T("is not No", "reflex");
            }
            if ($flag !== '') {
                return ltrim($stateLabel . ' ' . $flag);
            }
        }

        switch ($operator) {
            case 'between':
            case 'outside':
                $low = self::displayNumber($condition['threshold_value'] ?? null);
                $high = self::displayNumber($condition['threshold_value2'] ?? null);
                if (!$compact) {
                    return $label . ' ' . $low . $suffix . ' / ' . $high . $suffix;
                }
                $range = $low . ' – ' . $high . $suffix;
                return ($operator === 'between') ? $range : sprintf(_T("outside %s", "reflex"), $range);
            case 'changed':
                return $label;
        }
        if (isset($condition['threshold_text']) && $condition['threshold_text'] !== null
            && $condition['threshold_text'] !== '') {
            return ltrim($stateLabel . ' ' . $condition['threshold_text']);
        }
        $number = self::displayNumber($condition['threshold_value'] ?? null);
        if ($number === '') {
            return $label;
        }
        return $label . ' ' . $number . $suffix;
    }

    // Why the condition shown next to an alert may not be read as its cause.
    public static function conditionTrustNotice($status)
    {
        switch (strtolower(trim((string) $status))) {
            case 'unverified':
                return _T("This alert predates the recording of the condition that fires: what follows is the setting in force today.", "reflex");
            case 'changed':
                return _T("The condition changed since this alert was raised: what follows is the setting in force today.", "reflex");
            case 'contradicted':
                return _T("The value that raised this alert does not satisfy the condition below: it changed since, and the one that fired was not kept.", "reflex");
        }
        return '';
    }

    // One observation of condition_trust.evidence, in words.
    public static function conditionEvidenceLabel($key, $movedFields = array())
    {
        switch (strtolower(trim((string) $key))) {
            case 'trigger_value_unsatisfied':
                return _T("The value this alert was raised on does not satisfy the condition set today.", "reflex");
            case 'severity_moved':
                return _T("The severity of the condition changed since.", "reflex");
            case 'condition_disabled_now':
                return _T("The condition is switched off today.", "reflex");
            case 'customized_after_open':
                return _T("This condition was adapted after the alert was raised.", "reflex");
            case 'probe_edited_after_open':
                return _T("The probe was edited after the alert was raised.", "reflex");
            case 'condition_moved':
                $named = array();
                foreach ((array) $movedFields as $field) {
                    $named[] = self::conditionFieldLabel($field);
                }
                return empty($named)
                    ? _T("The settings of this condition changed since.", "reflex")
                    : sprintf(_T("Changed since the alert was raised: %s", "reflex"),
                              implode(', ', $named));
            case 'condition_deleted_now':
                return _T("This condition has been deleted since.", "reflex");
        }
        return '';
    }

    // What a measure was taken on, null when the probe reports one value.
    public static function measureInstance($measure)
    {
        if (!is_array($measure)) {
            return null;
        }
        $valueType = strtolower(trim((string) ($measure['value_type'] ?? 'numeric')));
        if ($valueType === 'text') {
            return null;
        }
        $instance = trim((string) ($measure['value_text'] ?? ''));
        return ($instance === '') ? null : $instance;
    }

    // Whether the agent of this machine has no collector to run for this
    // probe. A null agent_measurable is a system nobody could read, not a
    // verdict; a server-evaluated probe has no collector by design.
    public static function agentCannotMeasure($probe)
    {
        if (!is_array($probe) || !array_key_exists('agent_measurable', $probe)) {
            return false;
        }
        $measurable = $probe['agent_measurable'];
        // The backend answers 0 or 1: anything else, a nil decoded as it may
        // be, leaves the question open.
        if (!is_numeric($measurable)) {
            return false;
        }
        if (!empty($probe['server_evaluated'])) {
            return false;
        }
        return intval($measurable) === 0;
    }

    // Why the conditions of a probe could not be decided.
    public static function unevaluatedCause($measures)
    {
        $measures = self::measureRows($measures);
        if (empty($measures)) {
            return 'silent';
        }
        foreach ($measures as $measure) {
            if (strtolower(trim((string) ($measure['status'] ?? ''))) !== 'unavailable') {
                return 'several';
            }
        }
        return 'unavailable';
    }

    // Measures of one probe as a list, whatever shape the caller holds.
    public static function measureRows($measures)
    {
        if (!is_array($measures) || empty($measures)) {
            return array();
        }
        // A single row is an associative array: its first element is a scalar.
        $first = reset($measures);
        return is_array($first) ? array_values($measures) : array($measures);
    }

    // Entries a measure detail carries as {"items": [...]}. The same column also
    // holds the plain text reason of a reading that could not be taken, so
    // anything that is not that object reads as no list at all.
    public static function detailItems($detail)
    {
        $detail = is_string($detail) ? trim($detail) : '';
        if ($detail === '' || substr($detail, 0, 1) !== '{') {
            return array();
        }
        $decoded = json_decode($detail, true);
        if (!is_array($decoded) || !isset($decoded['items']) || !is_array($decoded['items'])) {
            return array();
        }
        $items = array();
        foreach ($decoded['items'] as $item) {
            if (is_string($item) && trim($item) !== '') {
                $items[] = trim($item);
            }
        }
        return $items;
    }

    // Label and tooltip of a reading that could not be taken. The reason comes
    // from the collector and says what this machine could not read; the
    // generic sentence only stands when the agent gave none.
    public static function unavailableReading($probeType = '', $detail = '')
    {
        $detail = trim((string) $detail);
        // A detail holding a list describes the reading, not its failure.
        if (!empty(self::detailItems($detail))) {
            $detail = '';
        }
        if ((string) $probeType === 'script') {
            return array(
                _T("Command failed", "reflex"),
                ($detail !== '') ? $detail : _T("The command returned nothing usable.", "reflex")
            );
        }
        return array(
            _T("No reading", "reflex"),
            ($detail !== '') ? $detail
                : _T("The agent read nothing for this metric on this machine.", "reflex")
        );
    }

    // Number without trailing zeroes, as plain text.
    public static function plainNumber($value)
    {
        if ($value === null || $value === '') {
            return '';
        }
        $formatted = rtrim(rtrim(number_format((float) $value, 2, '.', ''), '0'), '.');
        return ($formatted === '' || $formatted === '-') ? '0' : $formatted;
    }

    // Decimal separator of the language the console is read in.
    public static function decimalSeparator()
    {
        $lang = strtolower(trim((string) ($_SESSION['lang'] ?? '')));
        if ($lang === '' || $lang === 'c' || strpos($lang, 'en') === 0) {
            return '.';
        }
        return ',';
    }

    // Number as it is read, never as it is posted back.
    public static function displayNumber($value)
    {
        $formatted = self::plainNumber($value);
        if ($formatted === '') {
            return '';
        }
        return str_replace('.', self::decimalSeparator(), $formatted);
    }

    // Whether a probe answers yes or no.
    public static function isBooleanType($valueType)
    {
        return strtolower(trim((string) $valueType)) === 'boolean';
    }

    // A yes/no value in words.
    public static function booleanText($value)
    {
        if ($value === null || $value === '') {
            return '';
        }
        if (!is_numeric($value)) {
            // An agent may report the flag as a word rather than as a digit.
            switch (strtolower(trim((string) $value))) {
                case 'true':
                case 'yes':
                case 'on':
                    return _T("Yes", "reflex");
                case 'false':
                case 'no':
                case 'off':
                    return _T("No", "reflex");
            }
            return '';
        }
        return (floatval($value) != 0) ? _T("Yes", "reflex") : _T("No", "reflex");
    }

    // Who owns a personal probe, or wrote an exception or a channel.
    public static function authorLabel($login)
    {
        return self::safe($login, _T("Unknown", "reflex"));
    }

    // =========================================================================
    // Adapted alert conditions
    //
    // Same pattern as the settings table: the product ships default_*, the
    // operator may store a value of their own, and a NULL means "follow the
    // product". The operator of the condition and its display order are not
    // adaptable, so they never appear here.
    // =========================================================================

    // Fields of a condition an operator may adapt.
    public static function conditionOverridableFields()
    {
        return array(
            'threshold_value', 'threshold_value2', 'threshold_text',
            'duration_seconds', 'severity', 'message_template', 'enabled'
        );
    }

    // Whether the backend told what the product ships for this field.
    public static function conditionHasDefault($condition, $field)
    {
        return is_array($condition)
            && array_key_exists('default_' . $field, $condition)
            && $condition['default_' . $field] !== null;
    }

    // Value the product ships for a field, null when it is not known.
    public static function conditionDefault($condition, $field)
    {
        return self::conditionHasDefault($condition, $field)
            ? $condition['default_' . $field]
            : null;
    }

    // Value in force: what the operator chose, or what the product ships.
    public static function conditionEffective($condition, $field)
    {
        if (is_array($condition) && array_key_exists($field, $condition)
            && $condition[$field] !== null) {
            return $condition[$field];
        }
        return self::conditionDefault($condition, $field);
    }

    // Condition row with every adaptable field resolved to the value in force,
    // so the rendering helpers need to know nothing about overrides.
    public static function conditionEffectiveRow($condition)
    {
        if (!is_array($condition)) {
            return array();
        }
        $row = $condition;
        foreach (self::conditionOverridableFields() as $field) {
            $row[$field] = self::conditionEffective($condition, $field);
        }
        return $row;
    }

    // Condition row as the probe defines it: the definition, never a setting.
    public static function conditionDefinitionRow($condition)
    {
        if (!is_array($condition)) {
            return array();
        }
        $row = $condition;
        foreach (self::conditionOverridableFields() as $field) {
            if (self::conditionHasDefault($condition, $field)) {
                $row[$field] = self::conditionDefault($condition, $field);
            }
        }
        return $row;
    }

    // Compare a value with the shipped one in the type of its field: a
    // threshold typed 90 and a shipped 90.00 are the same threshold, and
    // storing an override for it would mark the condition adapted for nothing.
    public static function sameConditionValue($field, $a, $b)
    {
        if ($a === null || $b === null) {
            return ($a === null && $b === null);
        }
        switch ($field) {
            case 'threshold_value':
            case 'threshold_value2':
                return (abs(floatval($a) - floatval($b)) < 0.000001);
            case 'duration_seconds':
                return (intval($a) === intval($b));
            case 'enabled':
                return ((bool) $a === (bool) $b);
        }
        return (trim((string) $a) === trim((string) $b));
    }

    // Whether the condition carries an adaptation.
    public static function conditionIsCustomized($condition)
    {
        if (!is_array($condition)) {
            return false;
        }
        if (array_key_exists('is_customized', $condition)) {
            return !empty($condition['is_customized']);
        }
        if (!empty($condition['customized_at']) || !empty($condition['customized_by'])) {
            return true;
        }
        foreach (self::conditionOverridableFields() as $field) {
            if (!self::conditionHasDefault($condition, $field)) {
                continue;
            }
            if (!array_key_exists($field, $condition) || $condition[$field] === null) {
                continue;
            }
            if (!self::sameConditionValue($field, $condition[$field],
                                          $condition['default_' . $field])) {
                return true;
            }
        }
        return false;
    }

    // Label of an adaptable field.
    public static function conditionFieldLabel($field)
    {
        switch ($field) {
            case 'operator':
                return _T("Comparison", "reflex");
            case 'threshold_value':
                return _T("Threshold", "reflex");
            case 'threshold_value2':
                return _T("Upper bound", "reflex");
            case 'threshold_text':
                return _T("Text value", "reflex");
            case 'duration_seconds':
                return _T("Duration", "reflex");
            case 'severity':
                return _T("Severity", "reflex");
            case 'message_template':
                return _T("Alert message", "reflex");
            case 'enabled':
                return _T("Activation", "reflex");
        }
        return (string) $field;
    }

    // Label of a field named by a refused write, whatever the payload.
    public static function refusalFieldLabel($field)
    {
        switch ((string) $field) {
            // Probes.
            case 'label':
                return _T("Name", "reflex");
            case 'category':
                return _T("Category", "reflex");
            case 'description':
                return _T("Description", "reflex");
            case 'unit':
                return _T("Unit", "reflex");
            case 'alert_when':
            case 'alert_value':
            case 'alert_value2':
                return _T("Alert if the result", "reflex");
            case 'alert_duration':
                return _T("Duration", "reflex");
            case 'alert_severity':
                return _T("Severity", "reflex");
            case 'alert_message':
                return _T("Alert message", "reflex");
            case 'command_unix':
            case 'command_windows':
                return _T("Commands", "reflex");
            case 'value_type':
                return _T("Alert if the result", "reflex");
            case 'default_interval_seconds':
                return _T("Default interval", "reflex");
            case 'visibility':
                return _T("Visibility", "reflex");
            // Retention.
            case 'measures_days':
                return _T("Measures", "reflex");
            case 'alerts_resolved_days':
                return _T("Resolved alerts", "reflex");
            case 'notification_history_days':
                return _T("Sending history", "reflex");
            case 'entity_id':
                return _T("Entity", "reflex");
            // Assignments.
            case 'target_type':
                return _T("Target", "reflex");
            case 'target_id':
            case 'target_ids':
                return _T("Selected targets", "reflex");
            case 'interval_seconds':
                return _T("Cadence", "reflex");
            // Channels.
            case 'name':
                return _T("Name", "reflex");
            case 'channel_type':
                return _T("Type", "reflex");
            case 'config_json':
                return _T("Channel parameters", "reflex");
            case 'smtp_password':
                return _T("SMTP password", "reflex");
            // Notification rules.
            case 'channel_id':
                return _T("Channel", "reflex");
            case 'probe_id':
                return _T("Probe", "reflex");
            case 'min_severity':
                return _T("Minimum severity", "reflex");
            case 'recipients':
                return _T("Recipients", "reflex");
            case 'recipient':
                return _T("Send the test to", "reflex");
            case 'target_filter':
                return _T("Target restriction", "reflex");
            case 'cooldown_minutes':
                return _T("Cooldown (minutes)", "reflex");
            case 'escalation_minutes':
                return _T("Escalation (minutes)", "reflex");
            // Alerts.
            case 'comment':
                return _T("Comment", "reflex");
        }
        return self::conditionFieldLabel($field);
    }

    // Value of an adaptable field as plain text, for a tooltip or a hint
    // sitting next to a form field.
    public static function conditionFieldText($field, $value, $unit = '', $valueType = '')
    {
        if ($value === null || $value === '') {
            return _T("not set", "reflex");
        }
        switch ($field) {
            case 'threshold_value':
            case 'threshold_value2':
                if (self::isBooleanType($valueType)) {
                    $flag = self::booleanText($value);
                    if ($flag !== '') {
                        return $flag;
                    }
                }
                $unitText = self::unitLabel($unit);
                return self::displayNumber($value) . (($unitText !== '') ? ' ' . $unitText : '');
            case 'duration_seconds':
                return self::formatInterval($value);
            case 'severity':
                return self::severityLabel($value);
            case 'enabled':
                return empty($value) ? _T("Disabled", "reflex") : _T("Enabled", "reflex");
        }
        // Free text: shown beside the field that adapts it, so it is clamped.
        $text = ($field === 'message_template')
            ? self::productText($value)
            : (string) $value;
        if (mb_strlen($text, 'UTF-8') > 60) {
            $text = mb_substr($text, 0, 60, 'UTF-8') . '...';
        }
        return $text;
    }

    // Plain text naming what the product ships for each field that was
    // changed.
    public static function conditionCustomizationTitle($condition, $unit = '', $valueType = '')
    {
        $parts = array();
        foreach (self::conditionOverridableFields() as $field) {
            if (!self::conditionHasDefault($condition, $field)) {
                continue;
            }
            $default = self::conditionDefault($condition, $field);
            if (self::sameConditionValue($field, self::conditionEffective($condition, $field), $default)) {
                continue;
            }
            $parts[] = sprintf(
                _T("%s: %s shipped", "reflex"),
                self::conditionFieldLabel($field),
                self::conditionFieldText($field, $default, $unit, $valueType)
            );
        }

        if (empty($parts)) {
            $parts[] = _T("Adapted from the shipped values.", "reflex");
        }
        return implode(' - ', $parts);
    }

    // =========================================================================
    // Values written by the operator, and refusals answered by the server
    // =========================================================================

    // Threshold as it must leave this console: text, never a PHP float.
    // xmlrpc_encode_request() converts a double through LC_NUMERIC, which
    // i18n.inc.php sets: a French session would write <double>90,000000</double>.
    public static function thresholdText($raw)
    {
        $text = trim((string) $raw);
        return ($text === '') ? null : str_replace(',', '.', $text);
    }

    // Refusal carried by the answer of a write method, null when it succeeded.
    // A refusal answers a structure, and a non empty array is true in PHP:
    // intval() on it gives 1, the identifier of somebody else's row.
    public static function callRefusal($result)
    {
        if ($result === true || $result === 1 || $result === '1') {
            return null;
        }
        if (is_array($result) && !empty($result['success'])) {
            return null;
        }

        $refusal = array('code' => '', 'reason' => '', 'error' => '',
                         'field' => '', 'condition' => 0);
        if (is_array($result)) {
            $refusal['code'] = strtolower(trim((string) ($result['code'] ?? '')));
            // The class of the refusal decides what is done about it, the
            // reason decides how it is worded.
            $refusal['reason'] = strtolower(trim((string) ($result['reason'] ?? '')));
            $refusal['error'] = trim((string) ($result['error'] ?? ''));
            $refusal['field'] = trim((string) ($result['field'] ?? ''));
            $refusal['condition'] = intval($result['condition'] ?? 0);
            // Values the refusal names, such as the addresses that are not
            // ones.
            $refusal['details'] = (isset($result['details']) && is_array($result['details']))
                ? array_values(array_map('strval', $result['details'])) : array();
        }
        return $refusal;
    }

    // Identifier answered by a creation, 0 when it was refused.
    public static function createdId($result)
    {
        return (is_numeric($result) && intval($result) > 0) ? intval($result) : 0;
    }

    // What an alert was raised on, empty when the probe reports one value.
    public static function alertInstance($alert)
    {
        return is_array($alert) ? trim((string) ($alert['instance'] ?? '')) : '';
    }

    // The rule a refused value broke, said in the language of the console.
    public static function refusalReasonText($reason)
    {
        switch (strtolower(trim((string) $reason))) {
            case 'payload_malformed':
                return _T("The data sent does not have the expected form.", "reflex");
            case 'value_type_unknown':
                return _T("This value type is not supported.", "reflex");
            case 'operator_unknown':
                return _T("This operator is not supported.", "reflex");
            case 'operator_not_applicable':
                return _T("This operator does not apply to this kind of probe.", "reflex");
            case 'severity_unknown':
                return _T("This severity is not supported.", "reflex");
            case 'value_not_numeric':
                return _T("A number is expected here.", "reflex");
            case 'threshold_not_whole':
                return _T("A threshold is a whole number.", "reflex");
            case 'duration_negative':
                return _T("A duration cannot be negative.", "reflex");
            case 'threshold_required':
                return _T("This operator needs a threshold.", "reflex");
            case 'threshold_not_allowed':
                return _T("The changed operator takes no threshold.", "reflex");
            case 'threshold_text_required':
                return _T("A text probe is compared to a text value.", "reflex");
            case 'threshold_text_not_allowed':
                return _T("This operator compares numbers, not text.", "reflex");
            case 'threshold_boolean_expected':
                return _T("A boolean threshold is 0 or 1.", "reflex");
            case 'second_bound_not_allowed':
                return _T("A second bound belongs to the between and outside operators only.", "reflex");
            case 'range_bounds_required':
                return _T("This operator needs both bounds.", "reflex");
            case 'range_bounds_order':
                // Named as the two boxes are named on screen: the first one is
                // labelled "Threshold", and no field is called a lower bound
                // anywhere in this console.
                return _T("The upper bound must be greater than the threshold.", "reflex");
            case 'field_required':
                return _T("This field is required.", "reflex");
            case 'field_too_long':
                return _T("This field is longer than allowed.", "reflex");
            case 'field_not_overridable':
                return _T("This field cannot be adapted.", "reflex");
            case 'field_format_invalid':
                return _T("This field does not have the expected form.", "reflex");
            case 'value_not_positive':
                return _T("A number greater than zero is expected here.", "reflex");
            case 'email_invalid':
                return _T("Some addresses are not valid e-mail addresses.", "reflex");
            case 'test_recipient_required':
                return _T("Enter the address to send the test to.", "reflex");
            case 'test_recipient_single':
                return _T("A test is sent to one address only.", "reflex");
            case 'value_not_integer':
                return _T("A whole number is expected.", "reflex");
            case 'value_out_of_range':
                return _T("This value is outside the allowed range.", "reflex");
            case 'login_required':
                return _T("This action needs an identified user.", "reflex");
            case 'name_already_used':
                return _T("This name is already used.", "reflex");
            case 'label_already_used':
                return _T("A probe of this scope already bears this name.", "reflex");
            case 'label_reserved':
                // The catalog is read by everybody: that name is taken
                // everywhere, and no other scope would free it.
                return _T("This name belongs to a probe shipped with the product.", "reflex");
            case 'limit_reached':
                return _T("The number allowed here is reached.", "reflex");
            case 'category_unknown':
                return _T("This category is not supported.", "reflex");
            case 'channel_type_unknown':
                return _T("This channel type is not supported.", "reflex");
            case 'target_type_unknown':
                return _T("This target type is not supported.", "reflex");
            case 'scope_unknown':
                return _T("This visibility is not supported.", "reflex");
            case 'scope_reserved':
                return _T("The catalog visibility belongs to the probes shipped with the product.", "reflex");
            case 'entity_forbidden':
                return _T("This entity is outside your scope.", "reflex");
            case 'target_forbidden':
                return _T("This target is outside your scope.", "reflex");
            case 'channel_unknown':
                return _T("This notification channel does not exist any more.", "reflex");
            case 'probe_unknown':
                return _T("This probe does not exist any more.", "reflex");
            case 'target_deleted':
                return _T("The target of this assignment does not exist any more.", "reflex");
            case 'config_json_invalid':
                return _T("The channel parameters are not readable.", "reflex");
            case 'config_json_secret':
                return _T("A password does not belong to the channel parameters: use the password field, it is ciphered.", "reflex");
            case 'secret_key_unusable':
                return _T("The server cannot cipher a password: its encryption key is unusable.", "reflex");
        }
        return '';
    }

    // Addresses carried by a refusal, emptied of what was not typed.
    public static function addressList($details)
    {
        $addresses = array();
        foreach ((is_array($details) ? $details : array($details)) as $address) {
            $address = trim((string) $address);
            if ($address !== '') {
                $addresses[] = $address;
            }
        }
        return $addresses;
    }

    // Addresses the server refused, said for the number there are.
    public static function invalidAddressText($details)
    {
        $addresses = self::addressList($details);
        if (count($addresses) === 1) {
            return sprintf(_T("This address is not valid: %s", "reflex"), $addresses[0]);
        }
        if (!empty($addresses)) {
            return sprintf(_T("Invalid addresses: %s", "reflex"), implode(', ', $addresses));
        }
        // The server named none: nothing can be pointed at, only the rule.
        return self::refusalReasonText('email_invalid');
    }

    // Refusal turned into what the operator reads: the reason the server gave,
    // the row it points at, and the field it names. Displayed raw by the
    // notification widget, so it is escaped here.
    public static function refusalMessage($refusal, $fallback)
    {
        $reasonKey = is_array($refusal)
            ? strtolower(trim((string) ($refusal['reason'] ?? ''))) : '';
        $details = array();
        if (is_array($refusal) && !empty($refusal['details'])) {
            $details = is_array($refusal['details'])
                ? $refusal['details'] : array($refusal['details']);
        }
        // Refused addresses read inside the sentence, so they are not listed
        // under it a second time.
        $addressesSaid = ($reasonKey === 'email_invalid' && !empty($details));
        $reason = $addressesSaid
            ? self::invalidAddressText($details)
            : self::refusalReasonText($reasonKey);
        $error = is_array($refusal) ? (string) $refusal['error'] : '';
        if ($reason === '') {
            $reason = ($error !== '') ? $error : (string) $fallback;
        }
        // The sentence may come from the server: it is displayed raw by the
        // notification widget and has to be escaped here.
        $message = htmlspecialchars($reason, ENT_QUOTES, 'UTF-8');

        $rank = is_array($refusal) ? intval($refusal['condition']) : 0;
        if ($rank > 0) {
            $message = sprintf(
                htmlspecialchars(_T("Condition %1\$d: %2\$s", "reflex"), ENT_QUOTES, 'UTF-8'),
                $rank,
                $message
            );
        }

        // A refusal coded failed is a state of the server, not a value that
        // was typed: pointing at a box would send the operator correcting a
        // form that cannot fix it, while the detail the server wrote names
        // what has to be repaired on the machine.
        if (is_array($refusal) && ($refusal['code'] ?? '') === 'failed') {
            if ($error !== '' && $error !== $reason) {
                $message .= '<br/>' . htmlspecialchars($error, ENT_QUOTES, 'UTF-8');
            }
            return $message;
        }

        if (!$addressesSaid && !empty($details)) {
            $message .= '<br/>' . htmlspecialchars(
                implode(', ', array_map('strval', $details)), ENT_QUOTES, 'UTF-8');
        }

        $field = is_array($refusal) ? (string) $refusal['field'] : '';
        if ($field !== '') {
            $message .= '<br/>' . sprintf(
                htmlspecialchars(_T("Field concerned: %s", "reflex"), ENT_QUOTES, 'UTF-8'),
                htmlspecialchars(self::refusalFieldLabel($field), ENT_QUOTES, 'UTF-8')
            );
        }
        return $message;
    }
}

// Targets a probe can be placed on, read from the modules that own them.
class ReflexTargets
{
    // Machines preloaded in the picker.
    const MACHINE_LIMIT = 200;

    // Matches returned by one search, enough to pick from without scrolling.
    const SEARCH_LIMIT = 30;

    // Below that, a term matches too much of the estate to be worth a query.
    const SEARCH_MIN_LENGTH = 2;

    private static $machineLabels = null;
    private static $groupLabels = null;
    private static $entityLabels = null;
    private static $ruleFilterLabels = null;
    private static $resolvedMachines = array();
    private static $resolvedInventoryUuids = array();

    // Load a module helper file once, and tell whether it delivered.
    private static function helper($path, $probe)
    {
        if (!function_exists($probe) && file_exists($path)) {
            require_once($path);
        }
        return function_exists($probe);
    }

    // Identifier of a target or of an entity, or null when there is none.
    // The root GLPI entity is 0, a target like any other, while 0 reads as
    // "not set" everywhere else: intval('') is 0 too and cannot tell them apart.
    public static function identifier($value)
    {
        if (is_int($value)) {
            return ($value >= 0) ? $value : null;
        }
        $raw = trim((string) $value);
        if ($raw === '' || !ctype_digit($raw)) {
            return null;
        }
        return intval($raw);
    }

    // Turn an inventory answer into machines_id => hostname.
    private static function toMachineOptions($computers)
    {
        $labels = array();
        if (!is_array($computers) || empty($computers)) {
            return $labels;
        }
        if (!self::helper("modules/xmppmaster/includes/xmlrpc.php",
                          "xmlrpc_get_machines_infos_generic")) {
            return $labels;
        }

        $answer = xmlrpc_get_machines_infos_generic(
            'uuid_inventorymachine', array(array_keys($computers)),
            array('id', 'hostname', 'uuid_inventorymachine'), 0, -1, false);
        if (!is_array($answer) || !isset($answer['result']) || !is_array($answer['result'])) {
            return $labels;
        }

        foreach ($answer['result'] as $row) {
            $machineId = intval($row['id'] ?? 0);
            if ($machineId <= 0) {
                continue;
            }
            // The inventory name is preferred: it is the one shown everywhere
            // else in the console.
            $uuid = (string) ($row['uuid_inventorymachine'] ?? '');
            $name = '';
            if ($uuid !== '' && isset($computers[$uuid][1]['cn'][0])) {
                $name = (string) $computers[$uuid][1]['cn'][0];
            }
            if ($name === '') {
                $name = (string) ($row['hostname'] ?? '');
            }
            if ($name === '') {
                continue;
            }
            $labels[$machineId] = $name;
        }

        natcasesort($labels);
        return $labels;
    }

    // Machines the user may see, as machines_id => hostname.
    public static function machineOptions()
    {
        if (self::$machineLabels !== null) {
            return self::$machineLabels;
        }
        self::$machineLabels = array();

        if (!self::helper("modules/base/includes/computers.inc.php",
                          "getRestrictedComputersList")) {
            return self::$machineLabels;
        }

        $computers = getRestrictedComputersList(
            0, self::MACHINE_LIMIT, array('hostname' => ''), False);
        self::$machineLabels = self::toMachineOptions($computers);
        return self::$machineLabels;
    }

    // Machines whose name matches a term, as machines_id => hostname.
    public static function searchMachineOptions($term, $limit = self::SEARCH_LIMIT)
    {
        $term = trim((string) $term);
        if (strlen($term) < self::SEARCH_MIN_LENGTH) {
            return array();
        }
        if (!self::helper("modules/base/includes/computers.inc.php",
                          "getRestrictedComputersList")) {
            return array();
        }

        $limit = intval($limit);
        if ($limit <= 0) {
            $limit = self::SEARCH_LIMIT;
        }
        $computers = getRestrictedComputersList(
            0, $limit, array('hostname' => $term), False);
        return self::toMachineOptions($computers);
    }

    // Hostname of a machine the session may target, empty when it may not.
    public static function assignableMachineName($machineId)
    {
        $machineId = intval($machineId);
        if ($machineId <= 0) {
            return '';
        }

        self::preloadMachineNames(array($machineId));
        $name = (string) (self::$resolvedMachines[$machineId] ?? '');
        $uuid = (string) (self::$resolvedInventoryUuids[$machineId] ?? '');
        if ($name === '' || $uuid === '') {
            return '';
        }

        if (!self::helper("modules/base/includes/computers.inc.php",
                          "getRestrictedComputersList")) {
            return '';
        }
        $computers = getRestrictedComputersList(0, 1, array('uuid' => $uuid), False);
        if (!is_array($computers) || empty($computers)) {
            return '';
        }
        return $name;
    }

    // Resolve a known set of machine identifiers to their hostname.
    public static function preloadMachineNames($ids)
    {
        $wanted = array();
        foreach ((array) $ids as $id) {
            $id = intval($id);
            if ($id > 0 && !isset(self::$resolvedMachines[$id])) {
                $wanted[$id] = $id;
            }
        }
        if (empty($wanted)) {
            return;
        }
        if (!self::helper("modules/xmppmaster/includes/xmlrpc.php",
                          "xmlrpc_get_machines_infos_generic")) {
            return;
        }

        $answer = xmlrpc_get_machines_infos_generic(
            'id', array(array_values($wanted)),
            array('id', 'hostname', 'uuid_inventorymachine'), 0, -1, false);
        if (!is_array($answer) || !isset($answer['result']) || !is_array($answer['result'])) {
            return;
        }
        foreach ($answer['result'] as $row) {
            $id = intval($row['id'] ?? 0);
            $name = (string) ($row['hostname'] ?? '');
            if ($id > 0 && $name !== '') {
                self::$resolvedMachines[$id] = $name;
                // Kept aside so a target can be checked against the inventory
                // scope without a second round trip.
                self::$resolvedInventoryUuids[$id] = (string) ($row['uuid_inventorymachine'] ?? '');
            }
        }
    }

    // Machine groups, as dyngroup id => name.
    public static function groupOptions()
    {
        if (self::$groupLabels !== null) {
            return self::$groupLabels;
        }
        self::$groupLabels = array();

        if (!in_array("dyngroup", (array) ($_SESSION["modulesList"] ?? array()))) {
            return self::$groupLabels;
        }
        if (!self::helper("modules/dyngroup/includes/dyngroup.php", "getAllGroups")) {
            return self::$groupLabels;
        }

        $groups = getAllGroups(array('min' => 0, 'max' => -1, 'filter' => ''));
        if (!is_array($groups)) {
            return self::$groupLabels;
        }
        foreach ($groups as $group) {
            $id = is_object($group) ? intval($group->id ?? 0) : intval($group['id'] ?? 0);
            $name = is_object($group) ? (string) ($group->name ?? '') : (string) ($group['name'] ?? '');
            if ($id > 0 && $name !== '') {
                self::$groupLabels[$id] = $name;
            }
        }

        natcasesort(self::$groupLabels);
        return self::$groupLabels;
    }

    // Entities, as GLPI entity id => full name.
    public static function entityOptions()
    {
        if (self::$entityLabels !== null) {
            return self::$entityLabels;
        }
        self::$entityLabels = array();

        if (!self::helper("modules/medulla_server/includes/locations_xmlrpc.inc.php",
                          "getUserLocations")) {
            return self::$entityLabels;
        }

        $locations = getUserLocations();
        if (!is_array($locations)) {
            return self::$entityLabels;
        }
        foreach ($locations as $location) {
            if (!is_array($location)) {
                continue;
            }
            $uuid = trim((string) ($location['uuid'] ?? ''));
            if (stripos($uuid, 'UUID') === 0) {
                $uuid = substr($uuid, 4);
            }
            $id = self::identifier($uuid);
            // Tested for emptiness, not for its presence: a key answered as an
            // empty string satisfies ??
            $name = trim((string) ($location['completename'] ?? ''));
            if ($name === '') {
                $name = trim((string) ($location['name'] ?? ''));
            }
            if ($id !== null && $name !== '') {
                self::$entityLabels[$id] = $name;
            }
        }

        return self::$entityLabels;
    }

    // Entities the user may attach a probe to, as GLPI entity id => name.
    public static function userEntityOptions($login)
    {
        if (!function_exists('xmlrpc_reflex_get_user_entities')) {
            return array();
        }
        $rows = xmlrpc_reflex_get_user_entities($login);
        if (!is_array($rows)) {
            return array();
        }

        $known = self::entityOptions();
        $options = array();
        foreach ($rows as $row) {
            $id = null;
            $name = '';
            if (is_array($row)) {
                // The root entity answers 0, so a missing key and the root
                // itself must not collapse onto the same value.
                $id = self::identifier($row['id'] ?? ($row['entity_id'] ?? null));
                $name = (string) ($row['completename'] ?? ($row['name'] ?? ''));
            } else {
                $id = self::identifier($row);
            }
            if ($id === null) {
                continue;
            }
            // The console names entities itself; the backend name is only a
            // fallback for an entity the session cannot list.
            if (isset($known[$id])) {
                $name = (string) $known[$id];
            }
            if ($name === '') {
                $name = sprintf(_T("Entity %d", "reflex"), $id);
            }
            $options[$id] = $name;
        }

        natcasesort($options);
        return $options;
    }

    // Entities offered to read the condition settings, the one the server
    // really used included even when the account cannot list it.
    public static function settingEntityOptions($login, $settingEntity)
    {
        $options = self::userEntityOptions($login);
        if (count($options) < 2) {
            return null;
        }
        if ($settingEntity !== null && !isset($options[$settingEntity])) {
            $known = self::entityOptions();
            $options[$settingEntity] = isset($known[$settingEntity])
                ? $known[$settingEntity]
                : sprintf(_T("Entity %d", "reflex"), $settingEntity);
        }
        return $options;
    }

    // Labelled entity selector of a page header.
    public static function displayEntitySelector($id, $jsFunc, $options, $selected)
    {
        // SelectItem prints its options verbatim, and entity names come from
        // GLPI.
        $select = new SelectItem($id, $jsFunc);
        $select->setElements(array_map(
            array('ReflexDynamicForm', 'escapeForWidget'), array_values($options)));
        $select->setElementsVal(array_map(
            array('ReflexDynamicForm', 'escapeForWidget'), array_keys($options)));
        $select->setSelected(($selected === null) ? '' : (string) $selected);
        echo '<div class="reflex-filter">'
            . '<label for="' . htmlspecialchars($id, ENT_QUOTES, 'UTF-8') . '">'
            . _T("Entity", "reflex") . ':</label>';
        $select->display();
        echo '</div>';
    }

    // Options offered for a target type, empty for 'all'.
    public static function optionsFor($targetType)
    {
        switch ((string) $targetType) {
            case 'machine':
                return self::machineOptions();
            case 'group':
                return self::groupOptions();
            case 'entity':
                return self::entityOptions();
            default:
                return array();
        }
    }

    // Whether a row says its target is gone.
    public static function isDeleted($row)
    {
        return is_array($row)
            && self::saysDeleted($row['target_type'] ?? '', $row['target_state'] ?? '');
    }

    // Whether a state names a target that had a chance of disappearing.
    private static function saysDeleted($targetType, $targetState)
    {
        return ((string) $targetState === 'deleted')
            && in_array((string) $targetType, array('machine', 'group', 'entity'), true);
    }

    // Readable name of an assignment target.
    public static function label($targetType, $targetId, $targetState = null)
    {
        $targetType = (string) $targetType;
        if ($targetType === 'all' || $targetType === '') {
            return ReflexHelper::targetTypeLabel('all');
        }

        // 'entity' with an empty identifier is not the root entity, it is an
        // assignment carrying nothing: without this the two would read alike,
        // since intval('') is the identifier of the root entity.
        $key = self::identifier($targetId);
        if ($key === null) {
            return _T("Target not visible from your scope", "reflex");
        }
        if ($targetType === 'machine') {
            // Resolved on demand rather than through the bounded picker.
            self::preloadMachineNames(array($key));
            if (isset(self::$resolvedMachines[$key])) {
                return (string) self::$resolvedMachines[$key];
            }
            return _T("Target not visible from your scope", "reflex");
        }

        $options = self::optionsFor($targetType);
        if (isset($options[$key])) {
            return (string) $options[$key];
        }
        return _T("Target not visible from your scope", "reflex");
    }

    // Target of an assignment, in one readable phrase.
    public static function describe($targetType, $targetId, $targetState = null)
    {
        $label = self::label($targetType, $targetId, $targetState);
        switch ((string) $targetType) {
            case 'group':
                return sprintf(_T("Group: %s", "reflex"), $label);
            case 'entity':
                return sprintf(_T("Entity: %s", "reflex"), $label);
            default:
                return $label;
        }
    }

    // Restrictions a notification rule may carry, as stored value => label.
    public static function ruleFilterOptions()
    {
        if (self::$ruleFilterLabels !== null) {
            return self::$ruleFilterLabels;
        }
        self::$ruleFilterLabels = array();
        foreach (array_keys(self::groupOptions()) as $id) {
            self::$ruleFilterLabels['group:' . intval($id)] = self::describe('group', $id);
        }
        foreach (array_keys(self::entityOptions()) as $id) {
            self::$ruleFilterLabels['entity:' . intval($id)] = self::describe('entity', $id);
        }
        return self::$ruleFilterLabels;
    }

    // Readable form of a rule restriction.
    public static function ruleFilterLabel($filter)
    {
        $filter = trim((string) $filter);
        if ($filter === '') {
            return '';
        }
        $options = self::ruleFilterOptions();
        return isset($options[$filter]) ? $options[$filter] : null;
    }
}

// Form widgets whose fields are driven by a select.
class ReflexDynamicForm
{
    // Operators offered for a given value type.
    public static function operatorsFor($valueType)
    {
        switch (strtolower((string) $valueType)) {
            case 'boolean':
            case 'text':
                return array('eq', 'ne', 'changed');
            case 'numeric':
            default:
                return array('gt', 'gte', 'lt', 'lte', 'eq', 'ne', 'between', 'outside');
        }
    }

    // Operators needing a second bound.
    public static function rangeOperators()
    {
        return array('between', 'outside');
    }

    // Operators needing no threshold at all.
    public static function thresholdlessOperators()
    {
        return array('changed');
    }

    // Effective interval floor: the minimum the probe declares.
    public static function intervalFloor($probeMinInterval)
    {
        return intval($probeMinInterval);
    }

    // Operator tables the browser needs, plus the script tag. Inert
    // application/json block, HEX flags: nothing in it can leave as markup.
    public static function catalog()
    {
        $flags = JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT;
        $payload = json_encode(array(
            'operators' => array(
                'numeric' => self::operatorsFor('numeric'),
                'boolean' => self::operatorsFor('boolean'),
                'text' => self::operatorsFor('text')
            ),
            'rangeOperators' => self::rangeOperators(),
            'thresholdlessOperators' => self::thresholdlessOperators()
        ), $flags);

        if ($payload === false) {
            $payload = '{}';
        }

        echo '<script type="application/json" id="reflex-form-catalog">' . $payload . '</script>' . "\n";
        echo ReflexHelper::scriptTag('reflex.js', true) . "\n";
    }

    // Plain select built from a key => label map.
    public static function optionSelect($name, $options, $selected = '', $attrs = array(), $disabled = array())
    {
        $id = isset($attrs['id']) ? $attrs['id'] : $name;
        unset($attrs['id']);

        echo '<select class="mmc-select" name="' . htmlspecialchars($name) . '"';
        echo ' id="' . htmlspecialchars($id) . '"';
        foreach ($attrs as $attribute => $value) {
            if ($value === true) {
                echo ' ' . htmlspecialchars($attribute);
            } elseif ($value !== false && $value !== null) {
                echo ' ' . htmlspecialchars($attribute) . '="' . htmlspecialchars((string) $value) . '"';
            }
        }
        echo '>';

        foreach ($options as $value => $label) {
            $isSelected = ((string) $value === (string) $selected);
            // The stored value stays selectable even when disabled, so that
            // opening an old row never silently rewrites it.
            $isDisabled = (!$isSelected && in_array((string) $value, array_map('strval', $disabled), true));
            echo '<option value="' . htmlspecialchars((string) $value) . '"'
                . ($isSelected ? ' selected="selected"' : '')
                . ($isDisabled ? ' disabled="disabled"' : '') . '>'
                . htmlspecialchars((string) $label) . '</option>';
        }
        echo '</select>';
    }

    // Measurement cadences offered for a probe, already bounded by the
    // effective floor.
    public static function intervalChoices($probeMinInterval)
    {
        $floor = self::intervalFloor($probeMinInterval);
        $choices = array();
        foreach (ReflexHelper::intervalOptions() as $seconds => $label) {
            if ($seconds >= $floor) {
                $choices[$seconds] = $label;
            }
        }
        // A probe whose floor sits above every preset would otherwise offer
        // nothing: keep the shortest acceptable cadence in that case.
        if (empty($choices)) {
            $choices[$floor] = ReflexHelper::formatInterval($floor);
        }
        return $choices;
    }

    // Cadence field of a placement, shared by the placement popup and the
    // cadence change of an existing placement.
    public static function intervalSelect($probeMinInterval, $selected, $keepSelected = false)
    {
        $choices = self::intervalChoices($probeMinInterval);
        $selected = intval($selected);
        if ($keepSelected && $selected > 0 && !isset($choices[$selected])) {
            $choices[$selected] = ReflexHelper::formatInterval($selected);
            ksort($choices);
        }
        $keys = array_keys($choices);
        $select = new SelectItem('interval_seconds');
        $select->setElements(array_map(
            array('ReflexDynamicForm', 'escapeForWidget'), array_values($choices)));
        $select->setElementsVal($keys);
        $select->setSelected(isset($choices[$selected]) ? $selected : $keys[0]);
        return $select;
    }

    // Why a cadence chosen by the operator is refused, or '' when it is not.
    public static function intervalRefusal($interval)
    {
        $interval = intval($interval);
        if ($interval <= 0) {
            return _T("The measurement interval must be a positive number of seconds", "reflex");
        }
        $shortest = ReflexHelper::shortestInterval();
        if ($interval < $shortest) {
            return sprintf(
                _T("The measurement interval cannot be shorter than %s.", "reflex"),
                ReflexHelper::formatInterval($shortest)
            );
        }
        return '';
    }

    // Decode the config_json column into an array.
    public static function decodeChannelConfig($json)
    {
        if ($json === null || trim((string) $json) === '') {
            return array();
        }
        $decoded = json_decode((string) $json, true);
        return is_array($decoded) ? $decoded : array();
    }

    // Escape a value before it reaches a framework widget: InputTpl and
    // TextareaTpl print their value attribute verbatim, and SelectItem does the
    // same with its option labels and values.
    public static function escapeForWidget($value)
    {
        return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
    }

    // Kept for readability inside this class.
    protected static function safeValue($value)
    {
        return self::escapeForWidget($value);
    }

    // Append the email channel sections to a ValidatingForm.
    public static function addEmailChannelSections($form, $config, $secretConfigured, $isNew)
    {
        // config_json is free form: a key may hold a list, a boolean or a
        // number.
        $value = function ($key) use ($config) {
            if (!isset($config[$key])) {
                return '';
            }
            $raw = $config[$key];
            if (is_array($raw)) {
                return implode(', ', array_map('strval', $raw));
            }
            if (is_bool($raw)) {
                return $raw ? '1' : '0';
            }
            return (string) $raw;
        };

        $inherit = _T("Leave empty to inherit the server configuration.", "reflex");

        // --- Server ---------------------------------------------------
        $form->add(new SpanElement(_T("Server", "reflex"), "section-title"));
        $form->push(new Table());

        $form->add(
            new TrFormElement(_T("SMTP server", "reflex"), new multifieldTpl(array(
                new InputTpl('channel_host', '/^.*$/'),
                new textTpl('<i class="reflex-inherit-hint">' . htmlspecialchars($inherit) . '</i>')
            ))),
            array("value" => array(self::safeValue($value('host'))))
        );

        $form->add(
            new TrFormElement(_T("Port", "reflex"), new IntegerTpl('channel_port', '/^([0-9]{1,5})?$/')),
            array("value" => self::safeValue($value('port')))
        );

        // Three states are needed: a checkbox could not tell "disabled" from
        // "inherited", and the backend reads an empty value as disabled.
        $tls = '';
        if (isset($config['use_tls'])) {
            $raw = $config['use_tls'];
            if (is_bool($raw)) {
                $tls = $raw ? '1' : '0';
            } else {
                $raw = strtolower(trim((string) $raw));
                if ($raw !== '') {
                    $tls = in_array($raw, array('1', 'true', 'yes', 'on')) ? '1' : '0';
                }
            }
        }
        $tlsSelect = new SelectItem('channel_use_tls');
        $tlsSelect->setElements(array(
            _T("Server configuration", "reflex"),
            _T("STARTTLS enabled", "reflex"),
            _T("No encryption", "reflex")
        ));
        $tlsSelect->setElementsVal(array('', '1', '0'));
        $tlsSelect->setSelected($tls);
        $form->add(new TrFormElement(_T("Encryption", "reflex"), $tlsSelect));

        $form->pop();

        // --- Authentication -------------------------------------------
        $form->add(new SpanElement(_T("Authentication", "reflex"), "section-title"));

        // Shown only when the server could not create its key: without it no
        // password can be stored at all.
        if (!xmlrpc_reflex_has_encryption_key()) {
            $form->add(new ParaElement(
                htmlspecialchars(_T("The server could not create its encryption key, so a password cannot be stored. Check that mmc-agent can write to /etc/mmc/plugins/reflex.ini.local.", "reflex")),
                "reflex-warning-line"
            ));
        }

        $form->push(new Table());

        $form->add(
            new TrFormElement(_T("Authentication account", "reflex"), new multifieldTpl(array(
                new InputTpl('channel_username', '/^.*$/'),
                new textTpl('<i class="reflex-inherit-hint">'
                    . htmlspecialchars(_T("Leave empty for a server that accepts unauthenticated relaying.", "reflex"))
                    . '</i>')
            ))),
            array("value" => array(self::safeValue($value('username'))))
        );

        // The field is never prefilled: the backend returns whether a secret
        // exists, never the secret.
        $passwordTpl = new PasswordTpl('smtp_password', '/^.*$/');
        // Placed before the hard coded autocomplete="off" of InputTpl; the
        // first occurrence of an attribute is the one browsers apply.
        $passwordTpl->setAttributCustom('autocomplete="new-password" spellcheck="false"');

        if ($isNew) {
            $passwordHint = _T("Leave empty for a server that accepts unauthenticated relaying.", "reflex");
            $hintClass = 'reflex-inherit-hint';
        } elseif ($secretConfigured) {
            $passwordHint = _T("A password is stored. Leave empty to keep it.", "reflex");
            $hintClass = 'reflex-secret-set';
        } else {
            $passwordHint = _T("No password stored.", "reflex");
            $hintClass = 'reflex-inherit-hint';
        }

        $form->add(new TrFormElement(_T("SMTP password", "reflex"), new multifieldTpl(array(
            $passwordTpl,
            new textTpl('<i class="' . $hintClass . '">' . htmlspecialchars($passwordHint) . '</i>')
        ))));

        // Without this, a channel moving from an authenticated server to an
        // open one would keep a ghost secret.
        if (!$isNew && $secretConfigured) {
            $clearCb = new CheckboxTpl('smtp_password_clear');
            $form->add(
                new TrFormElement(_T("Delete the stored password", "reflex"), $clearCb),
                array("value" => "")
            );
        }

        $form->pop();

        // --- Sender ---------------------------------------------------
        $form->add(new SpanElement(_T("Sender", "reflex"), "section-title"));
        $form->push(new Table());
        $form->add(
            new TrFormElement(_T("Sender address", "reflex"), new multifieldTpl(array(
                new MailInputTpl('channel_from_address'),
                new textTpl('<i class="reflex-inherit-hint">' . htmlspecialchars($inherit) . '</i>')
            ))),
            array("value" => array(self::safeValue($value('from_address'))))
        );
        $form->add(
            new TrFormElement(_T("Sender name", "reflex"), new InputTpl('channel_from_name', '/^.*$/')),
            array("value" => self::safeValue($value('from_name')))
        );
        $form->pop();
    }

    // Compose config_json from the submitted form.
    public static function collectChannelConfig($channelType, $existingJson = '')
    {
        if (strtolower((string) $channelType) !== 'email') {
            // Only email has a form.
            return (string) $existingJson;
        }

        $config = self::decodeChannelConfig($existingJson);

        $fields = array(
            'host' => 'channel_host',
            'port' => 'channel_port',
            'use_tls' => 'channel_use_tls',
            'username' => 'channel_username',
            'from_address' => 'channel_from_address',
            'from_name' => 'channel_from_name'
        );
        unset($config['recipients'], $config['to']);

        foreach ($fields as $key => $field) {
            $raw = isset($_POST[$field]) ? trim((string) $_POST[$field]) : '';
            if ($raw === '') {
                unset($config[$key]);
                continue;
            }
            if ($key === 'port') {
                $config[$key] = intval($raw);
            } elseif ($key === 'use_tls') {
                $config[$key] = ($raw === '1');
            } else {
                $config[$key] = $raw;
            }
        }

        if (empty($config)) {
            return '';
        }
        $encoded = json_encode($config);
        return ($encoded === false) ? '' : $encoded;
    }

    // Repeatable condition rows.
    public static function conditionRows($conditions, $options = array())
    {
        $containerId = isset($options['containerId']) ? $options['containerId'] : 'reflex-conditions';
        $valueType = isset($options['valueType']) ? (string) $options['valueType'] : 'numeric';
        $unit = isset($options['unit']) ? (string) $options['unit'] : '';

        $invalid = (isset($options['invalid']) && is_array($options['invalid']))
            ? $options['invalid'] : array();
        $invalidRank = intval($invalid['condition'] ?? 0);
        $invalidField = (string) ($invalid['field'] ?? '');

        $rows = is_array($conditions) ? $conditions : array();
        if (empty($rows)) {
            $rows[] = array();
        }

        echo '<div class="reflex-condition-group" id="' . htmlspecialchars($containerId) . '"';
        echo ' data-reflex-conditions data-reflex-value-type="' . htmlspecialchars($valueType) . '"';
        echo ' data-reflex-unit="' . htmlspecialchars($unit) . '">';

        $index = 0;
        foreach ($rows as $condition) {
            // The server numbers the refused condition from 1.
            $rowField = ($invalidRank === ($index + 1)) ? $invalidField : '';
            self::conditionRow(is_array($condition) ? $condition : array(), $unit, $index, $rowField);
            $index++;
        }

        echo '</div>';

        // Blank row the script adds, identical to the one a form without any
        // condition starts with.
        echo '<template data-reflex-row-template="#' . htmlspecialchars($containerId) . '">';
        self::conditionRow(array(), $unit, 0, '');
        echo '</template>';

        echo '<div class="reflex-toolbar">';
        echo '<input type="button" class="btnSecondary" data-reflex-add-row';
        echo ' data-reflex-target="#' . htmlspecialchars($containerId) . '"';
        echo ' value="' . htmlspecialchars(_T("Add a condition", "reflex")) . '" />';
        echo '</div>';
    }

    // Mark of a field the server refused, drawn inline rather than from the
    // stylesheet: it is carried by one field of one row, and only until the
    // operator saves again.
    const INVALID_MARK_STYLE = 'outline:2px solid var(--severity-critical);'
        . 'outline-offset:2px;border-radius:3px;';

    // Style attribute of a refused field, empty for every other one.
    protected static function invalidMark($part, $flagged)
    {
        return in_array($part, $flagged, true)
            ? ' style="' . self::INVALID_MARK_STYLE . '"' : '';
    }

    // One condition row.
    protected static function conditionRow($condition, $unit, $index = 0, $invalidField = '')
    {
        $operator = (string) ($condition['operator'] ?? '');
        $severity = (string) ($condition['severity'] ?? 'medium');
        // A row created by the form has no stored state yet and is meant to
        // alert, so it starts enabled.
        $enabled = array_key_exists('enabled', $condition) ? !empty($condition['enabled']) : true;

        // A refused field is pointed at where it was typed: the notification
        // says what the server answered, the mark says which box it is about.
        $flagged = array();
        switch ($invalidField) {
            case 'operator':
                $flagged = array('operator');
                break;
            case 'threshold_value':
                $flagged = array('threshold_numeric', 'threshold_boolean');
                break;
            case 'threshold_value2':
                $flagged = array('threshold_value2');
                break;
            case 'threshold_text':
                $flagged = array('threshold_text');
                break;
            case 'duration_seconds':
                $flagged = array('duration');
                break;
            case 'severity':
                $flagged = array('severity');
                break;
            case 'message_template':
                $flagged = array('message');
                break;
            case 'enabled':
                $flagged = array('enabled');
                break;
        }

        echo '<div class="reflex-condition-row" data-reflex-condition-row>';

        // Stored condition this row updates, empty for a row to create.
        $conditionId = intval($condition['id'] ?? 0);
        echo '<input type="hidden" name="condition_id[]" value="'
            . (($conditionId > 0) ? htmlspecialchars((string) $conditionId, ENT_QUOTES, 'UTF-8') : '')
            . '" />';

        // Operator
        echo '<span class="reflex-condition-part"' . self::invalidMark('operator', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Comparison", "reflex")) . '</span>';
        echo '<select class="mmc-select" name="condition_operator[]" data-reflex-field="operator">';
        echo '<option value="">' . htmlspecialchars(_T("No condition", "reflex")) . '</option>';
        foreach (ReflexHelper::operatorOptions() as $value => $label) {
            echo '<option value="' . htmlspecialchars($value) . '"'
                . (($operator === $value) ? ' selected="selected"' : '') . '>'
                . htmlspecialchars($label) . '</option>';
        }
        echo '</select>';
        echo '</label>';
        echo '</span>';

        // Numeric threshold and its unit.
        echo '<span class="reflex-condition-part" data-reflex-field="threshold_numeric"'
            . self::invalidMark('threshold_numeric', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Threshold", "reflex")) . '</span>';
        echo '<input type="text" name="condition_threshold_value[]"';
        echo ' value="' . htmlspecialchars(ReflexHelper::plainNumber($condition['threshold_value'] ?? '')) . '" />';
        echo '</label>';
        echo '<span class="reflex-unit" data-reflex-field="unit">' . htmlspecialchars($unit) . '</span>';
        echo '</span>';

        // Upper bound, only meaningful for between and outside
        echo '<span class="reflex-condition-part" data-reflex-field="threshold_value2"'
            . self::invalidMark('threshold_value2', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Upper bound", "reflex")) . '</span>';
        echo '<input type="text" name="condition_threshold_value2[]"';
        echo ' value="' . htmlspecialchars(ReflexHelper::plainNumber($condition['threshold_value2'] ?? '')) . '" />';
        echo '</label>';
        echo '</span>';

        // Boolean threshold
        $boolValue = '';
        if (isset($condition['threshold_value']) && $condition['threshold_value'] !== null
            && $condition['threshold_value'] !== '') {
            $boolValue = (floatval($condition['threshold_value']) != 0) ? '1' : '0';
        }
        echo '<span class="reflex-condition-part" data-reflex-field="threshold_boolean"'
            . self::invalidMark('threshold_boolean', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Threshold", "reflex")) . '</span>';
        echo '<select class="mmc-select" name="condition_threshold_bool[]">';
        echo '<option value="">' . htmlspecialchars(_T("Not set", "reflex")) . '</option>';
        echo '<option value="1"' . (($boolValue === '1') ? ' selected="selected"' : '') . '>'
            . htmlspecialchars(_T("Yes", "reflex")) . '</option>';
        echo '<option value="0"' . (($boolValue === '0') ? ' selected="selected"' : '') . '>'
            . htmlspecialchars(_T("No", "reflex")) . '</option>';
        echo '</select>';
        echo '</label>';
        echo '</span>';

        // Text threshold
        echo '<span class="reflex-condition-part" data-reflex-field="threshold_text"'
            . self::invalidMark('threshold_text', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Text value", "reflex")) . '</span>';
        echo '<input type="text" name="condition_threshold_text[]"';
        echo ' value="' . htmlspecialchars((string) ($condition['threshold_text'] ?? '')) . '" />';
        echo '</label>';
        echo '</span>';

        // Duration.
        echo '<span class="reflex-condition-part"' . self::invalidMark('duration', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Duration (s)", "reflex")) . '</span>';
        echo '<input type="number" name="condition_duration[]" min="0" step="60"';
        echo ' title="' . htmlspecialchars(_T("Duration before alerting (seconds)", "reflex")) . '"';
        echo ' value="' . intval($condition['duration_seconds'] ?? 0) . '" />';
        echo '</label>';
        echo '</span>';

        // Severity
        echo '<span class="reflex-condition-part"' . self::invalidMark('severity', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Severity", "reflex")) . '</span>';
        echo '<select class="mmc-select" name="condition_severity[]">';
        foreach (ReflexHelper::severityOptions() as $value => $label) {
            echo '<option value="' . htmlspecialchars($value) . '"'
                . (($severity === $value) ? ' selected="selected"' : '') . '>'
                . htmlspecialchars($label) . '</option>';
        }
        echo '</select>';
        echo '</label>';
        echo '</span>';

        // Message.
        echo '<span class="reflex-condition-part reflex-condition-message"'
            . self::invalidMark('message', $flagged) . '>';
        echo '<label class="reflex-condition-label">';
        echo '<span>' . htmlspecialchars(_T("Alert message", "reflex")) . '</span>';
        echo '<input type="text" name="condition_message[]" maxlength="512"';
        echo ' value="' . htmlspecialchars((string) ($condition['message_template'] ?? '')) . '" />';
        echo '</label>';
        echo '</span>';

        // Activation.
        echo '<span class="reflex-condition-part reflex-condition-enabled"'
            . self::invalidMark('enabled', $flagged) . '>';
        echo '<label><input type="checkbox" data-reflex-indexed="condition_enabled"';
        echo ' name="condition_enabled[' . intval($index) . ']" value="1"';
        echo $enabled ? ' checked="checked"' : '';
        echo ' /> ' . htmlspecialchars(_T("Active", "reflex")) . '</label>';
        echo '</span>';

        // Row removal
        echo '<span class="reflex-condition-actions">';
        echo '<input type="button" class="btnSecondary" data-reflex-remove-row';
        echo ' value="' . htmlspecialchars(_T("Remove", "reflex")) . '" />';
        echo '</span>';

        echo '</div>';
    }

    // Import of an address list next to a recipients box. The file is read by
    // graph/js/reflex.js in the browser and never sent.
    public static function recipientsImport($fieldId)
    {
        $attr = function ($text) {
            return htmlspecialchars((string) $text, ENT_QUOTES, 'UTF-8');
        };
        return '<span class="reflex-recipients-import" data-reflex-recipients="' . $attr($fieldId) . '"'
            . ' data-msg-none="' . $attr(_T("No address found in this file.", "reflex")) . '"'
            . ' data-msg-invalid="' . $attr(_T("Invalid addresses: %s", "reflex")) . '"'
            . ' data-msg-invalid-one="' . $attr(_T("This address is not valid: %s", "reflex")) . '">'
            . '<input type="button" class="btnSecondary" data-reflex-recipients-pick value="'
            . $attr(_T("Import a list…", "reflex")) . '" />'
            . '<input type="file" accept=".csv,.txt,text/csv,text/plain" class="reflex-hidden" data-reflex-recipients-file />'
            . '<span class="reflex-recipients-report" data-reflex-recipients-report aria-live="polite"></span>'
            . '</span>';
    }

    // Import of a script next to a command box. Typing comfort only: the file
    // is read by graph/js/reflex.js in the browser, put in the box, and never
    // sent. What travels is the box, as if it had been pasted.
    public static function commandImport($fieldId, $label)
    {
        $attr = function ($text) {
            return htmlspecialchars((string) $text, ENT_QUOTES, 'UTF-8');
        };
        $max = ReflexHelper::SCRIPT_COMMAND_MAX_LENGTH;
        return '<span class="reflex-command-import" data-reflex-command="' . $attr($fieldId) . '"'
            . ' data-max="' . intval($max) . '"'
            . ' data-msg-replace="' . $attr(_T("Replace the command already written with the contents of this file?", "reflex")) . '"'
            . ' data-msg-empty="' . $attr(_T("This file holds no command.", "reflex")) . '"'
            . ' data-msg-unreadable="' . $attr(_T("This file could not be read.", "reflex")) . '"'
            . ' data-msg-too-long="' . $attr(
                _T("This file holds %s characters, more than the %s a command may carry.", "reflex")) . '"'
            . ' data-msg-loaded="' . $attr(_T("Command read from %s.", "reflex")) . '">'
            . '<input type="button" class="btnSecondary" data-reflex-command-pick'
            . ' aria-label="' . $attr(sprintf(
                _T("Import a file into the command for %s", "reflex"), $label)) . '"'
            . ' value="' . $attr(_T("Import a file…", "reflex")) . '" />'
            . '<input type="file" accept=".sh,.bash,.ps1,.cmd,.bat,.txt,text/plain" class="reflex-hidden"'
            . ' data-reflex-command-file />'
            . '<span class="reflex-command-report" data-reflex-command-report aria-live="polite"></span>'
            . '</span>';
    }

    // Comparisons of the one-line alert of a scripted probe.
    public static function alertChoices()
    {
        return array(
            'gt' => array(_T("is greater than", "reflex"), 1, true),
            'gte' => array(_T("is greater than or equal to", "reflex"), 1, true),
            'lt' => array(_T("is less than", "reflex"), 1, true),
            'lte' => array(_T("is less than or equal to", "reflex"), 1, true),
            'between' => array(_T("is between", "reflex"), 2, true),
            'outside' => array(_T("is outside", "reflex"), 2, true),
            'eq' => array(_T("is equal to", "reflex"), 1, true),
            'ne' => array(_T("is different from", "reflex"), 1, true),
            'yes' => array(_T("is Yes", "reflex"), 0, false),
            'no' => array(_T("is No", "reflex"), 0, false),
            'changed' => array(_T("has changed", "reflex"), 0, false)
        );
    }

    // Starting points offered on a new probe. Commands copied as they were
    // tested: nowdoc, nothing escaped nor translated.
    public static function probeTemplates()
    {
        $template = function ($name, $unix, $windows, $when, $value, $unit, $category) {
            return array(
                'name' => $name,
                'command_unix' => $unix,
                'command_windows' => $windows,
                'alert_when' => $when,
                'alert_value' => $value,
                'unit' => $unit,
                'category' => $category
            );
        };
        return array(
            $template(_T("Disk space used", "reflex"),
<<<'EOC'
df -P / | awk 'NR==2 {gsub("%","",$5); print $5}'
EOC
                ,
<<<'EOC'
$d = Get-PSDrive C; [math]::Round($d.Used / ($d.Used + $d.Free) * 100)
EOC
                , 'gt', '90', '%', 'storage'),
            $template(_T("Service running", "reflex"),
<<<'EOC'
systemctl is-active --quiet ssh && echo oui || echo non
EOC
                ,
<<<'EOC'
if ((Get-Service -Name Spooler).Status -eq 'Running') { 'oui' } else { 'non' }
EOC
                , 'no', '', '', 'service'),
            $template(_T("Port listening", "reflex"),
<<<'EOC'
if command -v ss >/dev/null 2>&1; then ss -ltn | grep -qE '[:.]22[[:space:]]'; else netstat -an | grep LISTEN | grep -qE '[:.]22[[:space:]]'; fi && echo oui || echo non
EOC
                ,
<<<'EOC'
if (Get-NetTCPConnection -State Listen -LocalPort 3389 -ErrorAction SilentlyContinue) { 'oui' } else { 'non' }
EOC
                , 'no', '', '', 'network'),
            $template(_T("Process running", "reflex"),
<<<'EOC'
pgrep -x nginx >/dev/null && echo oui || echo non
EOC
                ,
<<<'EOC'
if (Get-Process -Name nginx -ErrorAction SilentlyContinue) { 'oui' } else { 'non' }
EOC
                , 'no', '', '', 'application'),
            $template(_T("Backup age", "reflex"),
<<<'EOC'
f=/var/backups/latest.tar.gz; m=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f"); echo $(( ($(date +%s) - m) / 3600 ))
EOC
                ,
<<<'EOC'
[int]((Get-Date) - (Get-Item 'D:\Backup\latest.zip').LastWriteTime).TotalHours
EOC
                , 'gt', '24', 'h', 'storage'),
            $template(_T("Uptime", "reflex"),
<<<'EOC'
if [ -r /proc/uptime ]; then awk '{print int($1/86400)}' /proc/uptime; else b=$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+).*/\1/'); echo $(( ($(date +%s) - b) / 86400 )); fi
EOC
                ,
<<<'EOC'
[int]((Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalDays
EOC
                , 'gt', '30', 'd', 'system')
        );
    }

    // Alert durations offered, the stored one included when it is not listed.
    public static function durationChoices($current = 0)
    {
        $choices = array();
        foreach (array(0, 60, 300, 600, 900, 1800, 3600) as $seconds) {
            $choices[$seconds] = ReflexHelper::formatInterval($seconds);
        }
        $current = intval($current);
        if (!isset($choices[$current])) {
            $choices[$current] = ReflexHelper::formatInterval($current);
            ksort($choices);
        }
        return $choices;
    }

    // One-line alert read from a stored condition.
    public static function alertFromCondition($condition, $valueType)
    {
        $operator = (string) ($condition['operator'] ?? 'gt');
        // The line carries no box for the activation, and the form writes the
        // definition of the owner whole: read and sent back as it stands, or
        // saving the probe would switch a condition on again behind the back
        // of whoever switched it off.
        $enabled = ReflexHelper::conditionHasDefault($condition, 'enabled')
            ? ReflexHelper::conditionDefault($condition, 'enabled')
            : (array_key_exists('enabled', $condition) ? $condition['enabled'] : 1);
        $alert = array(
            'choice' => $operator,
            'value' => '',
            'value2' => '',
            'severity' => (string) ($condition['severity'] ?? 'medium'),
            'duration' => intval($condition['duration_seconds'] ?? 0),
            'message' => (string) ($condition['message_template'] ?? ''),
            'enabled' => empty($enabled) ? 0 : 1,
            'id' => intval($condition['id'] ?? 0)
        );
        if ($valueType === 'boolean' && ($operator === 'eq' || $operator === 'ne')) {
            $isOne = floatval($condition['threshold_value'] ?? 0) != 0;
            $alert['choice'] = (($operator === 'eq') === $isOne) ? 'yes' : 'no';
        } elseif ($valueType === 'text') {
            $alert['value'] = (string) ($condition['threshold_text'] ?? '');
        } else {
            $alert['value'] = ReflexHelper::plainNumber($condition['threshold_value'] ?? '');
            $alert['value2'] = ReflexHelper::plainNumber($condition['threshold_value2'] ?? '');
        }
        if (!array_key_exists($alert['choice'], self::alertChoices())) {
            $alert['choice'] = 'gt';
        }
        return $alert;
    }

    // One-line alert as submitted.
    public static function alertFromPost()
    {
        return array(
            'choice' => (string) ($_POST['alert_when'] ?? ''),
            'value' => trim((string) ($_POST['alert_value'] ?? '')),
            'value2' => trim((string) ($_POST['alert_value2'] ?? '')),
            'severity' => (string) ($_POST['alert_severity'] ?? 'medium'),
            'duration' => intval($_POST['alert_duration'] ?? 0),
            'message' => trim((string) ($_POST['alert_message'] ?? '')),
            // Carried by a hidden field rather than typed: the line has no box
            // for it, and a condition switched off elsewhere stays off.
            'enabled' => (isset($_POST['alert_enabled'])
                && (string) $_POST['alert_enabled'] === '0') ? 0 : 1,
            'id' => intval($_POST['alert_condition_id'] ?? 0)
        );
    }

    // Value type and condition a one-line alert stands for.
    public static function alertCondition($alert, $keptType = null)
    {
        $result = array('value_type' => 'numeric', 'condition' => null, 'error' => '', 'field' => '');
        $choices = self::alertChoices();
        $choice = (string) $alert['choice'];
        if (!isset($choices[$choice])) {
            $result['error'] = _T("This operator is not supported.", "reflex");
            $result['field'] = 'alert_when';
            return $result;
        }
        $number = function ($text) {
            $text = str_replace(',', '.', (string) $text);
            return is_numeric($text) ? $text : null;
        };
        $value = (string) $alert['value'];
        $value2 = (string) $alert['value2'];
        $operator = $choice;
        $threshold = null;
        $threshold2 = null;
        $thresholdText = null;

        switch ($choice) {
            case 'yes':
            case 'no':
                $result['value_type'] = 'boolean';
                $operator = 'eq';
                $threshold = ($choice === 'yes') ? '1' : '0';
                break;
            case 'changed':
                $result['value_type'] = $keptType ? (string) $keptType : 'text';
                break;
            case 'eq':
            case 'ne':
                if ($value === '') {
                    $result['error'] = _T("This field is required.", "reflex");
                    $result['field'] = 'alert_value';
                    return $result;
                }
                $threshold = $number($value);
                if ($threshold === null) {
                    $result['value_type'] = 'text';
                    $thresholdText = $value;
                }
                break;
            case 'between':
            case 'outside':
                if ($value === '' || $value2 === '') {
                    $result['error'] = _T("This operator needs both bounds.", "reflex");
                    $result['field'] = ($value === '') ? 'alert_value' : 'alert_value2';
                    return $result;
                }
                $threshold2 = $number($value2);
                if ($threshold2 === null) {
                    $result['error'] = _T("A number is expected here.", "reflex");
                    $result['field'] = 'alert_value2';
                    return $result;
                }
                // Falls through to read the first bound.
            default:
                if ($value === '') {
                    $result['error'] = _T("This field is required.", "reflex");
                    $result['field'] = 'alert_value';
                    return $result;
                }
                $threshold = $number($value);
                if ($threshold === null) {
                    $result['error'] = _T("A number is expected here.", "reflex");
                    $result['field'] = 'alert_value';
                    return $result;
                }
        }

        $result['condition'] = array(
            'id' => ($alert['id'] > 0) ? intval($alert['id']) : '',
            'operator' => $operator,
            'threshold_value' => $threshold,
            'threshold_value2' => $threshold2,
            'threshold_text' => $thresholdText,
            'duration_seconds' => intval($alert['duration']),
            'severity' => (string) $alert['severity'],
            'message_template' => (string) $alert['message'],
            // A line built here without the key means a condition being
            // created, and a new condition alerts.
            'enabled' => (array_key_exists('enabled', $alert) && empty($alert['enabled'])) ? 0 : 1,
            'display_order' => 10
        );
        return $result;
    }

    // Box of the one-line alert a refused condition field is typed in.
    public static function alertField($field)
    {
        $map = array(
            'operator' => 'alert_when',
            'enabled' => 'alert_when',
            'threshold_value' => 'alert_value',
            'threshold_text' => 'alert_value',
            'threshold_value2' => 'alert_value2',
            'duration_seconds' => 'alert_duration',
            'severity' => 'alert_severity',
            'message_template' => 'alert_message'
        );
        return isset($map[$field]) ? $map[$field] : '';
    }

    // Rebuild the condition rows from the submitted parallel arrays.
    public static function collectConditions($valueType)
    {
        $valueType = strtolower((string) $valueType);
        $collected = array();
        $operators = (isset($_POST['condition_operator']) && is_array($_POST['condition_operator']))
            ? $_POST['condition_operator'] : array();

        $rangeOperators = self::rangeOperators();
        $thresholdless = self::thresholdlessOperators();

        foreach ($operators as $index => $operator) {
            $operator = (string) $operator;
            if ($operator === '') {
                continue;
            }

            $thresholdValue = null;
            $thresholdValue2 = null;
            $thresholdText = null;

            if (!in_array($operator, $thresholdless)) {
                if ($valueType === 'text') {
                    $raw = isset($_POST['condition_threshold_text'][$index])
                        ? trim((string) $_POST['condition_threshold_text'][$index]) : '';
                    $thresholdText = ($raw === '') ? null : $raw;
                } elseif ($valueType === 'boolean') {
                    $raw = isset($_POST['condition_threshold_bool'][$index])
                        ? trim((string) $_POST['condition_threshold_bool'][$index]) : '';
                    // Text, like every threshold: see
                    // ReflexHelper::thresholdText().
                    $thresholdValue = ($raw === '') ? null : (($raw === '1') ? '1' : '0');
                } else {
                    $raw = isset($_POST['condition_threshold_value'][$index])
                        ? trim((string) $_POST['condition_threshold_value'][$index]) : '';
                    // Never a float on the wire, the locale would decide its
                    // decimal separator: see ReflexHelper::thresholdText().
                    $thresholdValue = ReflexHelper::thresholdText($raw);

                    if (in_array($operator, $rangeOperators)) {
                        $raw2 = isset($_POST['condition_threshold_value2'][$index])
                            ? trim((string) $_POST['condition_threshold_value2'][$index]) : '';
                        $thresholdValue2 = ReflexHelper::thresholdText($raw2);
                    }
                }
            }

            $conditionId = isset($_POST['condition_id'][$index])
                ? intval($_POST['condition_id'][$index]) : 0;

            $collected[] = array(
                'id' => ($conditionId > 0) ? $conditionId : '',
                'operator' => $operator,
                'threshold_value' => $thresholdValue,
                'threshold_value2' => $thresholdValue2,
                'threshold_text' => $thresholdText,
                'duration_seconds' => isset($_POST['condition_duration'][$index])
                    ? intval($_POST['condition_duration'][$index]) : 0,
                'severity' => isset($_POST['condition_severity'][$index])
                    ? (string) $_POST['condition_severity'][$index] : 'medium',
                'message_template' => isset($_POST['condition_message'][$index])
                    ? trim((string) $_POST['condition_message'][$index]) : '',
                'enabled' => (isset($_POST['condition_enabled'][$index])
                    && (string) $_POST['condition_enabled'][$index] !== '') ? 1 : 0,
                'display_order' => (count($collected) + 1) * 10
            );
        }

        return $collected;
    }
}


// Action drawn as unavailable, with the reason readable on hover. The framework
// draws one as a grey link whose :hover rule brightens it again, and carries no
// reason: hence the inline style and the bubble below.
class ReflexDisabledAction extends ActionItem
{
    // Copy of the .inactive rendering of global.css.
    const OFF_STYLE = 'cursor:default;opacity:0.5;'
        . 'filter:brightness(0) saturate(100%) invert(75%) sepia(0%) saturate(0%);';

    public function __construct($desc, $classCss)
    {
        $this->desc = $desc;
        $this->classCss = $classCss;
    }

    public function display($param = null, $extraParams = array())
    {
        $reason = htmlspecialchars((string) $this->desc, ENT_QUOTES, 'UTF-8');
        $bubble = htmlentities(
            '<div class="column-tooltip__text">' . $reason . '</div>',
            ENT_QUOTES,
            'UTF-8'
        );
        echo '<li class="' . htmlspecialchars((string) $this->classCss, ENT_QUOTES, 'UTF-8')
            . ' inactive">'
            . '<a class="reflex-action-off" href="#" onclick="return false;"'
            . ' aria-disabled="true" tabindex="-1"'
            . ' style="' . self::OFF_STYLE . '"'
            . ' title="' . $reason . '"'
            . ' mydata="' . $bubble . '">&nbsp;</a>'
            . '</li>';
    }

    // Keeps an unavailable action from turning the row name into a dead link.
    public function encapsulate($obj, $extraParams = array())
    {
        return $obj;
    }

    // Tooltip on the unavailable icons, emitted once per rendered fragment.
    public static function tooltipScript()
    {
        return '<script>
jQuery(function() {
    if (!(jQuery.ui && jQuery.ui.tooltip)) { return; }
    jQuery(".reflex-action-off").tooltip({
        position: { my: "right-12 center", at: "left center", collision: "flipfit flip" },
        items: "[mydata]",
        content: function() { return jQuery(this).attr("mydata"); }
    });
});
</script>';
    }
}

// Alert conditions as one entity reads them. The backend answers the entities
// this account may set, and the reader picks one: the sheet and the endpoint
// that refreshes it draw the same row from the same answer.
class ReflexEntitySettings
{
    // Entities worth a setting, keyed by entity and in reading order: those
    // holding machines first, then those holding a setting read by nothing.
    // The scope stays what the backend answered for this account.
    public static function entities($entitySettings, $login)
    {
        $rows = (is_array($entitySettings) && isset($entitySettings['data'])
                 && is_array($entitySettings['data']))
            ? $entitySettings['data'] : array();
        if (empty($rows)) {
            return array();
        }

        // The server could not count the machines: every entity is then kept.
        $countsUnreadable = !empty($entitySettings['unreadable']);
        $userNames = ReflexTargets::userEntityOptions($login);
        $knownNames = ReflexTargets::entityOptions();
        $readerEntity = ReflexTargets::identifier($entitySettings['reader_entity_id'] ?? null);

        $readerRow = null;
        $applying = array();
        $unused = array();
        foreach ($rows as $entityRow) {
            if (!is_array($entityRow)) {
                continue;
            }
            $key = ReflexTargets::identifier($entityRow['entity_id'] ?? null);
            if ($key === null) {
                continue;
            }
            if (isset($userNames[$key])) {
                $name = (string) $userNames[$key];
            } elseif (isset($knownNames[$key])) {
                $name = (string) $knownNames[$key];
            } else {
                $name = sprintf(_T("Entity %d", "reflex"), $key);
            }
            $entityRow['key'] = $key;
            $entityRow['name'] = $name;
            // An entity without machines holds a setting nothing will ever read.
            $entityRow['applies'] = ($countsUnreadable
                                     || intval($entityRow['machines_count'] ?? 0) > 0);
            if ($readerEntity !== null && $key === $readerEntity) {
                $readerRow = $entityRow;
            }
            if ($entityRow['applies']) {
                $applying[] = $entityRow;
            } elseif (!empty($entityRow['is_customized'])) {
                $unused[] = $entityRow;
            }
        }

        // An estate that has not registered a machine yet would offer nothing:
        // its own entity is kept so the setting stays reachable.
        if (empty($applying) && empty($unused) && $readerRow !== null) {
            $applying[] = $readerRow;
        }

        $byName = function ($a, $b) {
            return strnatcasecmp($a['name'], $b['name']);
        };
        usort($applying, $byName);
        usort($unused, $byName);

        $entities = array();
        foreach (array_merge($applying, $unused) as $entityRow) {
            $entities[$entityRow['key']] = $entityRow;
        }
        return $entities;
    }

    // The entity whose settings are drawn. What the address asks for is looked
    // up in what the backend answered for this account: an identifier typed by
    // hand is none of them, and the entity of the reader is drawn instead.
    public static function selected($entities, $requested, $entitySettings)
    {
        if ($requested !== null && isset($entities[$requested])) {
            return $entities[$requested];
        }
        $reader = ReflexTargets::identifier(
            is_array($entitySettings) ? ($entitySettings['reader_entity_id'] ?? null) : null);
        if ($reader !== null && isset($entities[$reader])) {
            return $entities[$reader];
        }
        foreach ($entities as $entityRow) {
            return $entityRow;
        }
        return null;
    }

    // Names offered by the selector, as entity id => name.
    public static function options($entities)
    {
        $options = array();
        foreach ($entities as $key => $entityRow) {
            $options[$key] = $entityRow['name'];
        }
        return $options;
    }

    // Whether any entity carries a condition to draw.
    public static function hasConditions($entities)
    {
        foreach ($entities as $entityRow) {
            if (!empty($entityRow['conditions']) && is_array($entityRow['conditions'])) {
                return true;
            }
        }
        return false;
    }

    // The conditions of one entity, one line each, with the gesture adapting
    // them. The entity is named by the selector, so no column repeats it.
    public static function display($probeId, $probe, $entityRow, $login)
    {
        if (!is_array($entityRow) || !is_array($probe)) {
            return;
        }
        $entityConditions = (isset($entityRow['conditions']) && is_array($entityRow['conditions']))
            ? $entityRow['conditions'] : array();
        if (empty($entityConditions)) {
            return;
        }

        $unit = isset($probe['unit']) ? (string) $probe['unit'] : '';
        $valueType = isset($probe['value_type']) ? (string) $probe['value_type'] : '';
        $isBuiltin = !empty($probe['is_builtin']);
        $isOwner = (isset($probe['owner_login']) && $probe['owner_login'] === $login
                    && $login !== '');
        $canWrite = (!$isBuiltin && ($isOwner
                     || (isset($probe['permission']) && $probe['permission'] === 'rw')));
        // Adapting the conditions of a shipped probe is the point of the override.
        $canAdaptConditions = ($isBuiltin || $canWrite);

        // What is set on this entity is never read: said rather than hidden.
        if (empty($entityRow['applies'])) {
            echo '<p class="reflex-warning-line">' . htmlspecialchars(
                _T("This entity holds no machine you can see: what is set on it is never read.", "reflex"))
                . '</p>';
        }

        $conditionCells = array();
        $thresholdCells = array();
        $severityCells = array();
        $durationCells = array();
        $rowParams = array();

        foreach ($entityConditions as $condition) {
            if (!is_array($condition)) {
                continue;
            }
            $effective = ReflexHelper::conditionEffectiveRow($condition);
            $conditionCells[] = ReflexHelper::describeCondition(
                    ReflexHelper::conditionDefinitionRow($condition), $unit, $valueType)
                . ReflexBadge::customized($condition, $unit, $valueType)
                . (empty($effective['enabled']) ? ' ' . ReflexBadge::enabled(0) : '');
            $thresholdCells[] = self::thresholdCell($effective, $unit, $valueType);
            $severityCells[] = ReflexBadge::severity($effective['severity'] ?? 'medium');
            $durationCells[] = htmlspecialchars(
                ReflexHelper::formatInterval($effective['duration_seconds'] ?? 0));
            // The gesture is made on the entity the reader chose, and this row
            // carries no other.
            $rowParams[] = array(
                'condition_id' => intval($condition['id'] ?? 0),
                'probe_id' => intval($probeId),
                'entity_id' => (string) $entityRow['key']
            );
        }

        if (empty($conditionCells)) {
            return;
        }

        $list = new OptimizedListInfos($conditionCells, _T("Condition", "reflex"), "", "",
                                       _T("The condition as the probe defines it.", "reflex"));
        $list->setTableCssClass("reflex-table reflex-entity-settings");
        // The condition text must stay text, it carries its own markers.
        $list->disableFirstColumnActionLink();
        $list->addExtraInfoCentered($thresholdCells, _T("Threshold", "reflex"));
        $list->addExtraInfoCentered($severityCells, _T("Severity", "reflex"));
        $list->addExtraInfoCentered($durationCells, _T("Duration", "reflex"));

        if ($canAdaptConditions) {
            $editAction = new ActionPopupItem(
                $isBuiltin
                    ? _T("Adapt this condition", "reflex")
                    : _T("Edit this condition", "reflex"),
                "ajaxEditCondition",
                "edit",
                "",
                "reflex",
                "reflex"
            );
            $editAction->setWidth(600);
            $list->setParamInfo($rowParams);
            $list->addActionItem($editAction);
        }

        $list->setItemCount(count($conditionCells));
        $list->start = 0;
        $list->end = count($conditionCells);
        $list->display(0, 0);
    }

    // Threshold in force, read the way the condition compares.
    private static function thresholdCell($effective, $unit, $valueType)
    {
        $operator = strtolower((string) ($effective['operator'] ?? ''));
        if (in_array($operator, ReflexDynamicForm::thresholdlessOperators(), true)) {
            return htmlspecialchars(ReflexHelper::operatorLabel($operator));
        }
        if (in_array($operator, ReflexDynamicForm::rangeOperators(), true)
            && ($effective['threshold_value2'] ?? null) !== null) {
            return htmlspecialchars(
                ReflexHelper::conditionFieldText('threshold_value',
                    $effective['threshold_value'] ?? null, $unit, $valueType)
                . ' - ' .
                ReflexHelper::conditionFieldText('threshold_value2',
                    $effective['threshold_value2'] ?? null, $unit, $valueType));
        }
        $text = (string) ($effective['threshold_text'] ?? '');
        if ($text !== '') {
            return htmlspecialchars(
                ReflexHelper::conditionFieldText('threshold_text', $text, $unit, $valueType));
        }
        return htmlspecialchars(
            ReflexHelper::conditionFieldText('threshold_value',
                $effective['threshold_value'] ?? null, $unit, $valueType));
    }
}



?>
