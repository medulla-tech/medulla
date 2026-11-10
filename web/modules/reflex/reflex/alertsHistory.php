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
 * Reflex Module - Alerts history
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$p = new PageGenerator(_T("Alerts History", 'reflex'));
$p->setSideMenu($sidemenu);
$p->display();

$severityOptions = ReflexHelper::severityOptions();
$severity = ReflexHelper::severityFilter($_GET['severity'] ?? '');

// The backend answers a bound it cannot read with an empty list, so anything
// that is not a calendar day is dropped.
$openedFrom = ReflexHelper::periodBound($_GET['opened_from'] ?? '');
$openedTo = ReflexHelper::periodBound($_GET['opened_to'] ?? '');
$rangeText = ReflexHelper::rangeText($openedFrom, $openedTo);
$uiLang = str_replace('_', '-', (string) ($_SESSION['lang'] ?? 'en_US'));

$probeId = ReflexHelper::probeFilter($_GET['probe_id'] ?? 0);

// Placed or not: a probe taken off the estate keeps its past alerts.
$probeOptions = ReflexHelper::probeSelectOptions(reflex_current_login(), false, $probeId);

// Carried in the URL the search field and the pagination are built from.
$ajaxUrl = urlStrRedirect("reflex/reflex/ajaxAlertsHistory")
    . "&severity=" . urlencode($severity)
    . "&opened_from=" . urlencode($openedFrom)
    . "&opened_to=" . urlencode($openedTo)
    . "&probe_id=" . $probeId;
?>

<div class="reflex-filter-bar">
    <div class="reflex-filter-grid">
        <div class="reflex-filter-field">
            <label for="reflex-history-severity"><?php echo _T("Severity", "reflex"); ?></label>
            <select id="reflex-history-severity" onchange="reflexUpdateHistoryFilter()">
                <option value=""><?php echo _T("All severities", "reflex"); ?></option>
                <?php foreach ($severityOptions as $value => $label): ?>
                <option value="<?php echo htmlspecialchars($value); ?>"
                    <?php echo ($value === $severity) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($label); ?>
                </option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="reflex-filter-field">
            <label for="reflex-history-probe"><?php echo _T("Probe", "reflex"); ?></label>
            <select id="reflex-history-probe" onchange="reflexUpdateHistoryFilter()">
                <option value="0" <?php echo ($probeId === 0) ? 'selected' : ''; ?>>
                    <?php echo _T("All probes", "reflex"); ?>
                </option>
                <?php foreach ($probeOptions as $value => $label): ?>
                <option value="<?php echo intval($value); ?>"
                    <?php echo ($value === $probeId) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($label); ?>
                </option>
                <?php endforeach; ?>
            </select>
        </div>
        <?php /* The column next to it is "Resolved": without saying which date
                 the period bounds, the filter reads as bearing on that one. */ ?>
        <div class="reflex-filter-field reflex-history-period"
             title="<?php echo htmlspecialchars(_T("The period bounds the date the alert opened, not its resolution.", "reflex"), ENT_QUOTES, 'UTF-8'); ?>">
            <label for="reflex-history-range"><?php echo htmlspecialchars(_T("Opened between", "reflex")); ?></label>
            <div class="reflex-range">
                <input type="text" id="reflex-history-range" class="reflex-range-input" readonly
                       placeholder="<?php echo htmlspecialchars(_T("All dates", "reflex"), ENT_QUOTES, 'UTF-8'); ?>"
                       value="<?php echo htmlspecialchars($rangeText, ENT_QUOTES, 'UTF-8'); ?>" />
                <button type="button" class="reflex-range-clear" id="reflex-history-range-clear"
                        title="<?php echo htmlspecialchars(_T("Clear the period", "reflex"), ENT_QUOTES, 'UTF-8'); ?>"
                        aria-label="<?php echo htmlspecialchars(_T("Clear the period", "reflex"), ENT_QUOTES, 'UTF-8'); ?>">&times;</button>
            </div>
            <input type="hidden" id="reflex-history-from" value="<?php echo htmlspecialchars($openedFrom, ENT_QUOTES, 'UTF-8'); ?>" />
            <input type="hidden" id="reflex-history-to" value="<?php echo htmlspecialchars($openedTo, ENT_QUOTES, 'UTF-8'); ?>" />
        </div>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter($ajaxUrl);
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>

<script>
function reflexHistoryUrl() {
    var severity = document.getElementById('reflex-history-severity').value;
    var probeId = document.getElementById('reflex-history-probe').value;
    var openedFrom = document.getElementById('reflex-history-from').value;
    var openedTo = document.getElementById('reflex-history-to').value;
    var url = '<?php echo urlStrRedirect("reflex/reflex/ajaxAlertsHistory"); ?>';
    url += '&severity=' + encodeURIComponent(severity);
    url += '&opened_from=' + encodeURIComponent(openedFrom);
    url += '&opened_to=' + encodeURIComponent(openedTo);
    url += '&probe_id=' + encodeURIComponent(probeId);
    return url;
}
<?php echo ReflexHelper::ajaxListScript('reflexHistoryUrl', 'reflexUpdateHistoryFilter'); ?>
// One field, one calendar. First click sets the start; a second click on the
// same day keeps it alone, on a later day sets the end, earlier moves the start.
(function ($) {
    var $range = $('#reflex-history-range');
    var $from = $('#reflex-history-from');
    var $to = $('#reflex-history-to');
    var lang = <?php echo json_encode($uiLang, JSON_HEX_TAG); ?>;
    var anchor = null;
    var saved = null;

    function iso(date) {
        return $.datepicker.formatDate('yy-mm-dd', date);
    }

    function shown(value) {
        return value ? $.datepicker.formatDate('dd/mm/yy', $.datepicker.parseDate('yy-mm-dd', value)) : '';
    }

    function refresh() {
        var from = $from.val(), to = $to.val();
        if (!from && !to) {
            $range.val('');
        } else if (from === to) {
            $range.val(shown(from));
        } else {
            $range.val((shown(from) + ' → ' + shown(to)).trim());
        }
    }

    function names(options, dates) {
        var fmt = new Intl.DateTimeFormat(lang, options);
        return dates.map(function (d) {
            var text = fmt.format(d).replace('.', '');
            return text.charAt(0).toUpperCase() + text.slice(1);
        });
    }

    var regional = {firstDay: lang.indexOf('en') === 0 ? 0 : 1};
    try {
        var months = [], days = [];
        for (var m = 0; m < 12; m++) { months.push(new Date(2026, m, 1)); }
        for (var d = 4; d < 11; d++) { days.push(new Date(2026, 0, d)); }
        regional.monthNames = names({month: 'long'}, months);
        regional.dayNames = names({weekday: 'long'}, days);
        regional.dayNamesMin = names({weekday: 'short'}, days).map(function (n) { return n.slice(0, 2); });
    } catch (e) {}

    $range.datepicker($.extend(regional, {
        dateFormat: 'dd/mm/yy',
        prevText: <?php echo json_encode(_T("Previous month", "reflex"), JSON_HEX_TAG); ?>,
        nextText: <?php echo json_encode(_T("Next month", "reflex"), JSON_HEX_TAG); ?>,
        beforeShow: function (input, inst) {
            saved = {from: $from.val(), to: $to.val()};
            anchor = null;
            inst.dpDiv.addClass('reflex-range-picker');
            var start = $from.val() || $to.val();
            return {defaultDate: start ? $.datepicker.parseDate('yy-mm-dd', start) : null};
        },
        beforeShowDay: function (date) {
            var day = iso(date);
            var lo = anchor !== null ? anchor : $from.val();
            var hi = anchor !== null ? anchor : ($to.val() || lo);
            if (!lo || day < lo || day > hi) {
                return [true, ''];
            }
            var cls = 'reflex-range-in';
            if (day === lo) { cls += ' reflex-range-start'; }
            if (day === hi) { cls += ' reflex-range-end'; }
            return [true, cls];
        },
        onSelect: function (text, inst) {
            var day = iso($.datepicker.parseDate('dd/mm/yy', text));
            var keepOpen = false;
            if (anchor === null || day < anchor) {
                anchor = day;
                $from.val(day);
                $to.val('');
                keepOpen = true;
            } else {
                $from.val(anchor);
                $to.val(day);
                anchor = null;
            }
            refresh();
            if (keepOpen) {
                inst.inline = true;
                setTimeout(function () { inst.inline = false; }, 0);
            }
        },
        onClose: function (text, inst) {
            inst.dpDiv.removeClass('reflex-range-picker');
            if (anchor !== null) {
                $from.val(saved.from);
                $to.val(saved.to);
                anchor = null;
            }
            refresh();
            if ($from.val() !== saved.from || $to.val() !== saved.to) {
                reflexUpdateHistoryFilter();
            }
        }
    }));

    // Focus alone does not reopen it once the field has kept the focus.
    $range.on('click', function () {
        $range.datepicker('show');
    });

    $('#reflex-history-range-clear').on('click', function () {
        if ($from.val() || $to.val()) {
            $from.val('');
            $to.val('');
            refresh();
            reflexUpdateHistoryFilter();
        }
    });
})(jQuery);
</script>
