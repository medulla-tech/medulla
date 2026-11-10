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
 * Reflex Module - Tooltips carried by a value
 */

/**
 * Tooltips rendered as the framework renders the ones on column headers: a
 * jQuery UI bubble fed by a `mydata` attribute. A plain `title` is not shown.
 */
class ReflexTip
{
    public static function on($html, $lines)
    {
        $text = array();
        foreach ((array) $lines as $line) {
            $line = trim((string) $line);
            if ($line !== '') {
                $text[] = htmlspecialchars($line, ENT_QUOTES, 'UTF-8');
            }
        }
        if (empty($text)) {
            return $html;
        }
        // Encoded twice: the browser decodes the attribute once, and the script
        // writes what is left as the markup of the bubble.
        $bubble = htmlentities(
            '<div class="column-tooltip__text">' . implode('<br>', $text) . '</div>',
            ENT_QUOTES,
            'UTF-8'
        );
        // `infomach` is the console-wide mark of a value carrying a bubble.
        return '<span class="infomach reflex-tip" mydata="' . $bubble . '">' . $html . '</span>';
    }

    public static function acknowledgement($html, $user, $at, $comment)
    {
        $user = trim((string) $user);
        $comment = trim((string) $comment);
        if ($user === '' && $comment === '') {
            return $html;
        }
        $who = ($user === '')
            ? _T("Acknowledged", "reflex")
            : sprintf(_T("Acknowledged by %s", "reflex"), $user);
        $when = ReflexHelper::plainDate($at);
        if ($when !== '') {
            $who .= ' - ' . $when;
        }
        return self::on($html, array($who, $comment));
    }

    // A guest clock drifts: a machine two hours behind reports measures that look
    // two hours old. Everything is judged on the server timestamp, so the drift
    // costs nothing functionally, but it is a real defect of the machine.
    // The backend already compared the two timestamps and hands over its verdict.
    public static function reportedClockDrift($drift, $seconds, $note = '')
    {
        $seconds = (int) $seconds;
        if (empty($drift) || $seconds === 0) {
            return '';
        }
        return self::driftMark($seconds, $note);
    }

    private static function driftMark($seconds, $note = '')
    {
        $duration = ReflexHelper::formatDuration(abs($seconds));
        $label = ($seconds < 0)
            ? sprintf(_T("Clock of this machine ahead by %s", "reflex"), $duration)
            : sprintf(_T("Clock of this machine behind by %s", "reflex"), $duration);
        return ' ' . self::on(
            '<span class="reflex-clock-drift">&#9888;</span>',
            array($label, $note)
        );
    }

    const TITLE_MARKERS = '.reflex-clock-drift, .reflex-adapted,'
        . ' .reflex-not-measurable, .reflex-state-excluded,'
        . ' .reflex-resolution-reason,'
        . ' .reflex-inherit-hint, .reflex-measure-warning,'
        . ' .reflex-measure-error, .reflex-measure-unavailable';

    public static function script()
    {
        return '<script>
jQuery(function() {
    if (!(jQuery.ui && jQuery.ui.tooltip)) { return; }
    var place = {
        position: { my: "center top+8", at: "center bottom", collision: "flipfit flipfit" }
    };
    jQuery(".reflex-tip").tooltip(jQuery.extend({
        items: "[mydata]",
        content: function() { return jQuery(this).attr("mydata"); }
    }, place));
    jQuery("' . self::TITLE_MARKERS . '").tooltip(place);
});
</script>';
    }
}
