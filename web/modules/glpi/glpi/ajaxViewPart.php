<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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

/* Get GLPI xmlrpc includes */
require_once("modules/glpi/includes/xmlrpc.php");

/*
 * Display Glpi Inventory part infos (Summary, Hardware, Network, etc..)
 *
 * @param part: Part to display
 * @type part: string
 * @param get: $_GET array
 * @type get: array
 * @param simpleTableParts: part who are displayed in a simple table
 * @type simpleTableParts: array
 * @param displayNavBar: Should NavBar will be displayed ?
 * @type displayNavBar: Boolean
 * @param partTitle: Should we display a Title to part ?
 * @type: null or string
 */
function display_part($part, $get, $simpleTableParts, $displayNavBar = True, $partTitle = null) {
    $uuid = '';
    if (isset($get['uuid'])) {
        $uuid = $get['uuid'];
    }
    elseif (isset($get['objectUUID'])) {
        $uuid = $get['objectUUID'];
    }

    $maxperpage = (isset($get['maxperpage'])) ? $get['maxperpage'] : 0;
    $filter = isset($get["filter"]) ? $get['filter'] : '';
    if (isset($get["start"])) { $start = $get["start"]; } else { $start = 0; }
    $end = $start + $maxperpage;

    $hide_win_updates = (isset($get['hide_win_updates'])) ? $get['hide_win_updates'] : False;
    $hide_win_updates = (strtolower($hide_win_updates) == 'true') ? True : False;
    $history_delta = (isset($get['history_delta'])) ? $get['history_delta'] : False;

    $options = array(
        'hide_win_updates' => $hide_win_updates,
        'history_delta' => $history_delta,
    );

    // Get current part inventory
    $inv = getLastMachineGlpiPart($uuid, $part, $start, $end, $filter, $options);
    $itemCount = countLastMachineGlpiPart($uuid, $part, $filter, $options);

    if (!is_array($inv)) $inv = array();

    // this piece of code re-format inventory array
    // $all variable will contain part's inventory
    $all = array();
    $i = 0;
    foreach ($inv as $line) {
        foreach ($line as $vals) {
            $all[$vals[0]][$i] = $vals[1];
        }
        $i++;
    }

    /*
     * simpleTableParts are parts who are *not* displayed
     * in a multi-line table
     */

    // Simple table
    $name = 'computer_name';
    $value = 'JC-' . $uuid;
    setGlpiEditableValue($uuid, $name, $value);
    if (in_array($part, $simpleTableParts)) {
        $key = array();
        $val = array();
        foreach(array_keys($all) as $k) {
            $key[] = _T($k, 'glpi');
            if ($k == 'Serial Number') {
                $val[] = str_replace('@@WARRANTY_LINK_TEXT@@', _T('Click here to see this computer on manufacturer website', 'glpi'), $all[$k][0]);
            }
            else {
                /*
                 * if $all[$k][0] is an array, it's an editable value
                 * $editable = array(uniquename, type, value)
                 */
                if (is_array($all[$k][0])) {
                    $editable = $all[$k][0];
                    $val[] = sprintf('<label name="%s" data="%s">%s</label>', $editable[0], $editable[1], $editable[2]);
                }
                else {
                    $val[] = $all[$k][0];
                }
            }
        }
        $n = new ListInfos($key, _T("Properties", "glpi"));
        $n->addExtraInfo($val, _T("Value", "glpi"));
        /*
         * $_GET['maxperpage'] is set to 10 by default
         * If there is more than 10 elements, they don't be displayed
         * So setRowsPerPage equal to number of elements to display
         */
        $n->setRowsPerPage(count($all));
        $n->drawTable(0);
    }
    // Multi-line table
    else {
        $n = null;

        // Put datas in a ListInfos object
        foreach ($all as $k => $v) {
            if ($n == null) {
                $n = new OptimizedListInfos($v, _T($k, 'glpi'));
            }
            else {
                $n->addExtraInfo($v, _T($k, 'glpi'));
            }
        }

        // display table
        if ($n) {
            $n->setItemCount($itemCount);
            $n->setNavBar(new AjaxNavBar($itemCount, $filter));
            $n->disableFirstColumnActionLink();
            $n->setTableHeaderPadding(1);
            $n->start = 0;
            $n->end = $itemCount;

            // Display a title (it happens in Hardware tab)
            if ($partTitle) printf("<h2>%s</h2>", $partTitle);

            // Display table with (or not) NavBar
            $n->display($displayNavBar, $displayNavBar);
            if ($partTitle) echo "<br />";
        }
    }
}

if (!isset($simpleTableParts)) $simpleTableParts = array();
$part = $_GET['part'];

if ($part == 'Hardware') {
    $hardwareParts = array(
        'Processors' => _T('Processors', "glpi"),
        'Memory' => _T('Memory', "glpi"),
        'Harddrives' => _T('Hard Drives', "glpi"),
        'Controllers' => _T('Controllers', "glpi"),
        'NetworkCards' => _T('Network Cards', "glpi"),
        'Drives' => _T('Drives', "glpi"),
        'GraphicCards' => _T('Graphic Cards', "glpi"),
        'SoundCards' => _T('Sound Cards', "glpi"),
        'Others' => _T('Others', "glpi"),
    );

    foreach ($hardwareParts as $part => $title) {
        display_part($part, $_GET, $simpleTableParts, False, $title);
    }
}
else {
    display_part($part, $_GET, $simpleTableParts);
}

/**  to get i18n labels... */

_T('Name', 'glpi');
_T('Network Type', 'glpi');
_T('MAC Address', 'glpi');
_T('IP', 'glpi');
_T('Netmask', 'glpi');
_T('Gateway', 'glpi');
_T('Device', 'glpi');
_T('Mount Point', 'glpi');
_T('Filesystem', 'glpi');
_T('Size', 'glpi');
_T('Free Size', 'glpi');
_T('Supplier', 'glpi');
_T('Invoice Number', 'glpi');
_T('Warranty End Date', 'glpi');
_T('Vendor', 'glpi');
_T('Name', 'glpi');
_T('Version', 'glpi');
_T('Computer Name', 'glpi');
_T('Description', 'glpi');
_T('Entity (Location)', 'glpi');
_T('Last Logged User', 'glpi');
_T('OS', 'glpi');
_T('Model / Type', 'glpi');
_T('Manufacturer', 'glpi');
_T('Serial Number', 'glpi');
_T('Frequency', 'glpi');
_T('Type', 'glpi');
_T('Size', 'glpi');
_T('Bandwidth', 'glpi');
_T('Writer', 'glpi');
_T('Memory', 'glpi');
_T('Comment', 'glpi');
_T('Date', 'glpi');
_T('User', 'glpi');
_T('Category', 'glpi');
_T('Action', 'glpi');
_T('Today', 'glpi');
_T('Last week', 'glpi');
_T('Last month', 'glpi');
_T('All', 'glpi');
_T('Service Pack', 'glpi');
_T('Domain', 'glpi');
_T('State', 'glpi');
_T('Inventory Number', 'glpi');

?>

</table>
<script type="text/javascript">
$$('tbody tr td:not(.action)').invoke('observe', 'click', function(event) {
    var tdValue = this.innerHTML.stripTags();
    $('param').value = tdValue.replace(/&nbsp;/g, ' ');
    pushSearch();
});
</script>
