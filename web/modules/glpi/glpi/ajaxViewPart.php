<?
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

    // Get current part inventory
    $inv = getLastMachineGlpiPart($uuid, $part, $start, $end, $filter, $hide_win_updates);
    $itemCount = countLastMachineGlpiPart($uuid, $part, $filter, $hide_win_updates);

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
    if (in_array($part, $simpleTableParts)) {
        $key = array();
        $val = array();
        foreach(array_keys($all) as $k) {
            $key[] = _T($k, 'glpi');
            $val[] = $all[$k][0];
        }
        $n = new ListInfos($key, _T("Properties", "glpi"));
        $n->addExtraInfo($val, _T("Value", "glpi"));
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
        'Memories' => _T('Memories', "glpi"),
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

_T('name', 'glpi');
_T('comments', 'glpi');
_T('ifaddr', 'glpi');
_T('ifmac', 'glpi');
_T('netmask', 'glpi');
_T('gateway', 'glpi');
_T('subnet', 'glpi');
_T('type', 'glpi');
_T('designation', 'glpi');
_T('specif_default', 'glpi');
_T('frequence', 'glpi');
_T('bandwidth', 'glpi');
_T('is_writer', 'glpi');
_T('interface', 'glpi');
_T('comment', 'glpi');

_T('processor', 'glpi');
_T('ram', 'glpi');
_T('hdd', 'glpi');
_T('iface', 'glpi');
_T('drive', 'glpi');
_T('gfxcard', 'glpi');
_T('sndcard', 'glpi');
_T('pci', 'glpi');

?>

</table>
