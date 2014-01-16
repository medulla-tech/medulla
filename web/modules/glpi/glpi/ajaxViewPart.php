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
            /*
             * If $vals[1] is an empty string or an array, don't use the _T() function
             * Empty fields are replaced by a trademark text by transifex
             * if it's an array, it's an editable field
             */

            $vals[1] = str_replace('@@FALSE_POSITIVE@@', _T(' (Not an antivirus)', 'glpi'), $vals[1]);
            $all[$vals[0]][$i] = '';
            if (!is_array($vals[1]) && $vals[1] != '') { // translatable fields
                $all[$vals[0]][$i] = _T($vals[1]);
            }
            elseif (is_array($vals[1])) { // editable fields
                $all[$vals[0]][$i] = $vals[1];
            }
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
                    $val[] = sprintf('<label class="editableField" name="%s" data="%s" style="height:1em;">%s</label>', $editable[0], $editable[1], $editable[2])
                             .sprintf('<input type="text" class="editableField" name="%s" value="%s" style="display:none" />', $editable[0], $editable[2]);
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

        // If nothing found, display a "nothing found" message
        // except on Hardware tab (identified by $partTitle == null) => display nothing
        if (count($all) == 0 && $partTitle == null)  {
            switch($part) {
            case 'History':
                printf('<p>%s</p>', _T('No record found for this period.', 'glpi'));
                break;
            case 'Antivirus':
                printf('<p>%s</p>', _T('Unable to detect any Antivirus software on this machine.', 'glpi'));
                printf('<p>%s</p>', _T('Please ensure you are running GLPI with FusionInventory plugin and FusionInventory Agent on this client.', 'glpi'));
                break;
            default:
                printf('<p>%s</p>', _T('No record found.', 'glpi'));
            }
        }

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

// Yes/No translation hack
_T('Yes', 'glpi');
_T('No', 'glpi');
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
_T('Date Of Purchase', 'glpi');
_T('Warranty End Date', 'glpi');
_T('Vendor', 'glpi');
_T('Name', 'glpi');
_T('Version', 'glpi');
_T('Computer Name', 'glpi');
_T('Description', 'glpi');
_T('Entity (Location)', 'glpi');
_T('Entity', 'glpi');
_T('Location', 'glpi');
_T('Last Logged User', 'glpi');
_T('OS', 'glpi');
_T('Operating System', 'glpi');
_T('Computer Type', 'glpi');
_T('Model / Type', 'glpi');
_T('Model', 'glpi');
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
_T('Last 7 days', 'glpi');
_T('Last 30 days', 'glpi');
_T('All', 'glpi');
_T('Service Pack', 'glpi');
_T('Windows Key', 'glpi');
_T('Domain', 'glpi');
_T('State', 'glpi');
_T('Unknown', 'glpi');
_T('Inventory Number', 'glpi');
// From Antivirus tab
_T('Enabled', 'glpi');
_T('Up-to-date', 'glpi');

?>

</table>
<script type="text/javascript">
// TODO: To remove
jQuery('tbody tr td:not(.action)').on('click',function(){
    jQuery('#param').val(jQuery(this).text().replace(/&nbsp;/g, ' '));
    pushSearch();
});

// Editable fields label click
jQuery('label.editableField').on('click',function(){
    var name = jQuery(this).attr('name');
    var value = jQuery(this).text();
    // corresponding input
    var input = jQuery('input.editableField[name="'+name+'"]').first();
    jQuery(this).hide();
    input.val(value).show().focus();
});

jQuery('input.editableField').bind('keyup focusout',function(e){
    // If we receive a keycode (keyup), it must be #13 [return]
    if (e.keyCode != null && e.keyCode != 13) return;

    var name = jQuery(this).attr('name');
    var value = jQuery(this).val();
    var input = jQuery(this);

    // Special case: computername regex
    var cname_regex = /^([a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9])$/;
    if (name=='computer_name' && !cname_regex.test(value)) {
        alert('<?php print(_T('Invalid hostname','glpi')); ?>');
        return;
    }

    // Posting ajax request
    jQuery.get('<?php echo urlStrRedirect("base/computers/ajaxSetGlpiEditableValue")?>&uuid=<?php echo quickGet('uuid'); ?>&name='+name+'&value='+value).success(function(){
        var label = jQuery('label.editableField[name="'+name+'"]').first();
        label.html(value).show();
        input.hide();
    });
});


</script>
