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
require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/inventory/i18n_labels.php");
require_once("modules/base/includes/edit.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// =============================================================================
// ==================== GLPI DISPLAY PART FUNCTION =============================
// =============================================================================

function display_part($part, $get, $simpleTableParts, $displayNavBar = True, $partTitle = null) {
    $uuid = '';
    if (isset($get['uuid'])) {
        $uuid = $get['uuid'];
    } elseif (isset($get['objectUUID'])) {
        $uuid = $get['objectUUID'];
    }

    $filter = isset($get["filter"]) ? $get['filter'] : '';
    if (isset($get["start"])) {
        $start = $get["start"];
    } else {
        $start = 0;
    }

    global $maxperpage;
    $end = 100; // There is no need for multipaging in these parts

    $hide_win_updates = (isset($get['hide_win_updates'])) ? $get['hide_win_updates'] : False;
    $hide_win_updates = (strtolower($hide_win_updates) == 'true') ? True : False;
    $history_delta = (isset($get['history_delta'])) ? $get['history_delta'] : False;

    $options = array(
        'hide_win_updates' => $hide_win_updates,
        'history_delta' => $history_delta,
    );

    // Get current part inventory
    //$inv = getLastMachineInventoryPart2($uuid, $part, $start, $end, $filter, $options);
    $inv = getLastMachineInventoryPart2($part, array('uuid' => $uuid, 'filter' => $filter, 'min' => $start, 'max' => $end, 'software_filter' => '')); //'date' => $date,
    //$itemCount = countLastMachineGlpiPart($uuid, $part, $filter, $options);
    $itemCount = count($inv); // TODO: Calculate it from array

    if (!is_array($inv))
        $inv = array();

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

            $vals[1] = str_replace('@@FALSE_POSITIVE@@', _T(' (Not an antivirus)', 'inventory'), $vals[1]);
            $all[$vals[0]][$i] = '';
            if (!is_array($vals[1]) && $vals[1] != '') { // translatable fields
                $all[$vals[0]][$i] = _T($vals[1]);
            } elseif (is_array($vals[1])) { // editable fields
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
        foreach (array_keys($all) as $k) {
            $key[] = _T($k, 'inventory');
            if ($k == 'Serial Number') {
                $val[] = str_replace('@@WARRANTY_LINK_TEXT@@', _T('Click here to see this computer on manufacturer website', 'inventory'), $all[$k][0]);
            } else {
                /*
                 * if $all[$k][0] is an array, it's an editable value
                 * $editable = array(uniquename, type, value)
                 */
                if (is_array($all[$k][0])) {
                    $editable = $all[$k][0];
                    $val[] = sprintf('<label class="editableField" name="%s" data="%s" style="height:1em;">%s</label>', $editable[0], $editable[1], $editable[2])
                            . sprintf('<input type="text" class="editableField" name="%s" value="%s" style="display:none" />', $editable[0], $editable[2]);
                } else {
                    $val[] = $all[$k][0];
                }
            }
        }
        $n = new ListInfos($key, _T("Properties", "inventory"));
        $n->addExtraInfo($val, _T("Value", "inventory"));
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
        if (count($all) == 0 && $partTitle == null) {
            switch ($part) {
                case 'History':
                    printf('<p>%s</p>', _T('No record found for this period.', 'inventory'));
                    break;
                case 'Antivirus':
                    printf('<p>%s</p>', _T('Unable to detect any Antivirus software on this machine.', 'inventory'));
                    printf('<p>%s</p>', _T('Please ensure you are running GLPI with FusionInventory plugin and FusionInventory Agent on this client.', 'inventory'));
                    break;
                default:
                    printf('<p>%s</p>', _T('No record found.', 'inventory'));
            }
        }

        // Put datas in a ListInfos object
        foreach ($all as $k => $v) {
            if ($n == null) {
                $n = new OptimizedListInfos($v, _T($k, 'inventory'));
            } else {
                $n->addExtraInfo($v, _T($k, 'inventory'));
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
            if ($partTitle)
                printf("<h2>%s</h2>", $partTitle);

            // Display table with (or not) NavBar
            $n->display($displayNavBar, $displayNavBar);
            if ($partTitle)
                echo "<br />";
        }
    }
}

// =============================================================================


$filter = $_GET["filter"];
$from = $_GET['from'];

// Get the date set into the calendar
if ($_GET['date'] == _T('Date')) {
    $date = "";
} else {
    $date = $_GET['date'];
    // Put the date in a session to save it
    $_SESSION['__inventoryDate'] = $date;
}

// Check the status of the software_filter checkbox if in the Software page
if (isset($_GET['software_filter']) && $_GET['part'] == 'Software')
    $software_filter = $_GET['software_filter'] == 'true';
else
    $software_filter = "";

// Hide windows updates or not
if (isset($_GET['hide_win_updates']) && $_GET['part'] == 'Software')
    $hide_win_updates = $_GET['hide_win_updates'] == 'true';
else
    $hide_win_updates = "";

if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;

if ($_GET['uuid'] != '') {

    $table = $_GET['part'];

    if (in_array($_GET['part'], array('Summary', 'Hardware', 'Storage', 'Network'))) {
        // GLPI Display mode

        $simpleTableParts = array('Summary');

        $part = $_GET['part'];

        if ($part == 'Hardware') {
            $hardwareParts = array(
                'Processors' => _T('Processors', "inventory"),
                'Memory' => _T('Memory', "inventory"),
                'Drives' => _T('Storage', "inventory"),
                'Controllers' => _T('Controllers', "inventory"),
                'NetworkCards' => _T('Network Cards', "inventory"),
                'Storage' => _T('Drives', "inventory"),
                'GraphicCards' => _T('Graphic Cards', "inventory"),
                'SoundCards' => _T('Sound Cards', "inventory"),
                'Others' => _T('Others', "inventory"), // Not implemented
            );

            foreach ($hardwareParts as $part => $title) {
                display_part($part, $_GET, $simpleTableParts, False, $title);
            }
        } else {
            display_part($part, $_GET, $simpleTableParts);
        }
    } else {
        $graph = getInventoryGraph($table);
        $inv = getLastMachineInventoryPart($table, array('uuid' => $_GET["uuid"], 'filter' => $filter, 'min' => $start, 'max' => ($start + $maxperpage), 'date' => $date, 'software_filter' => $software_filter, 'hide_win_updates' => $hide_win_updates));
        $count = countLastMachineInventoryPart($table, array('uuid' => $_GET["uuid"], 'filter' => $filter, 'date' => $date, 'software_filter' => $software_filter, 'hide_win_updates' => $hide_win_updates));

        /* display everything else in separated tables */
        $n = null;
        $h = array();

        $index = 0;
        if ($count > 0 and is_array($inv) and is_array($inv[0]) and is_array($inv[0][1])) {
            foreach ($inv[0][1] as $def) {
                foreach ($def as $k => $v) {
                    $h[$k][$index] = $v;
                }
                $index+=1;
            }
        }

        $disabled_columns = (isExpertMode() ? array() : getInventoryEM($table));
        $disabled_columns[] = 'id';
        $disabled_columns[] = 'timestamp';
        $disabled_columns[] = 'Icon';

        /* Delete these both lines because Type and Application columns will be removed from database */
        $disabled_columns[] = 'Type';
        $disabled_columns[] = 'Application';

        /* Generate icon => <img src="data:image/jpg;base64,DATA"> */
        if (isset($h['Icon'])) {
            $index = 0;
            foreach ($h['Icon'] as $v) {
                if ($v != '') {
                    $h['Icon'][$index] = '<IMG src="data:image/jpeg;base64,' . $v . '">';
                }
                $index+=1;
            }
            $n = new OptimizedListInfos($h['Icon'], '');
        }

        /*
         * $k is header title of inventory tab
         * corresponding to tables in DB
         * Use an array to display friendly names
         * instead of Ugly table name
         */
        
	function __sort($a, $b){
	 
	 $__order = array('Path','Value','Company','ProductName','ProductVersion');
	 if (array_search($a, $__order) === FALSE && array_search($b, $__order) === FALSE)
	   return 0;
	 if (array_search($a, $__order) === FALSE)
	   return -1;
	 if (array_search($b, $__order) === FALSE)
	   return 1;
	// print (array_search($a, $__order) .' - '. array_search($b, $__order) );
	 if (array_search($a, $__order) < array_search($b, $__order) )
	   return -1;
	 else
	   return 1;
	}
	// Sorting Columns
    uksort($h,'__sort');
    // If Path, Value are present (Registry) and sort lines by Paths
    if (isset( $h['Path'], $h['Value'] ))//&& in_array('Value',$h) )
        array_multisort($h['Path'],$h['Value']);

	foreach ($h as $k => $v) {
            /*
             * If a machine has many IP Adresses, they are stored like this
             * in database (separated by a slash):
             * x.x.x.x/x.x.x.x/x.x.x.x
             *
             * For machines with many IPs, display is very awful,
             * So search & replace slashes by \r\n
             */

            if ($k == 'IpAddress') {
                foreach ($v as &$ipaddr) {
                    $ipaddr = str_replace("/", "\r\n", $ipaddr);
                }
            }

            if (!in_array($k, $disabled_columns)) {
                // Replace Database table names by human names
                $k = ($tabTitles[$k] != NULL) ? $tabTitles[$k] : $k;
                if (in_array($k, $graph) && count($v) > 1) {
                    $type = ucfirst($_GET['part']);
                    # TODO should give the tab in the from param
                    $nhead = $k . " <a href='main.php?module=inventory&submod=inventory&action=graphs&type=$type&from=$from&field=$k";
                    foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
                        $nhead .= "&$get=" . $_GET[$get];
                    }
                    $nhead .= "' alt='graph'><img src='modules/inventory/img/graph.png'/></a>";
                    $k = $nhead;
                } else {
                    $k = _T($k, 'inventory');
                }

                if ($n == null) {
                    $n = new OptimizedListInfos($v, $k);
		    //print_r($k);
                } else {
                    $n->addExtraInfo($v, $k);
                }
            }
        }
        print "<div style=\"overflow: auto\">";
        if ($n != null) {
            $n->setTableHeaderPadding(1);
            $n->setItemCount($count);
            $n->setNavBar(new AjaxNavBar($count, $filter));
            $n->start = 0;
            $n->end = $maxperpage;
            $n->display();
        }
        print "</div>";
        ?><a href='<?php echo urlStr("inventory/inventory/csv", array('table' => $table, 'uuid' => $_GET["uuid"])) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a>

        <?php
    }
} else {
    $display = $_GET['part'];
    $machines = getLastMachineInventoryPart($display, array('gid' => $_GET["gid"], 'filter' => $filter, 'min' => $start, 'max' => ($start + $maxperpage), 'date' => $date, 'software_filter' => $software_filter, 'hide_win_updates' => $hide_win_updates));
    $count = countLastMachineInventoryPart($display, array('gid' => $_GET["gid"], 'filter' => $filter, 'date' => $date, 'software_filter' => $software_filter, 'hide_win_updates' => $hide_win_updates));

    $result = array();
    $index = 0;
    $params = array();
    foreach ($machines as $machine) {
        $name = $machine[0];
        if (count($machine[1]) == 0) {
            $result['Machine'][$index] = $name;
            $index += 1;
        }
        foreach ($machine[1] as $element) {
            $result['Machine'][$index] = $name;
            foreach ($element as $head => $val) {
                if ($head != 'id' && $head != 'timestamp') {
                    $result[$head][$index] = $val;
                }
            }
            $index += 1;
        }
        $params[] = array('hostname' => $machine[0], 'uuid' => $machine[2]);
    }
    $n = null;

    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($display));
    $disabled_columns[] = 'id';
    $disabled_columns[] = 'timestamp';
    $disabled_columns[] = 'Icon';

    /* Delete these both lines because Type and Application columns will be removed from database */
    $disabled_columns[] = 'Type';
    $disabled_columns[] = 'Application';

    /* Generate icon => <img src="data:image/jpg;base64,DATA"> */
    if (isset($result['Icon'])) {
        $index = 0;
        foreach ($result['Icon'] as $v) {
            if ($v != '') {
                $result['Icon'][$index] = '<IMG src="data:image/jpeg;base64,' . $v . '">';
            }
            $index+=1;
        }
        $n = new OptimizedListInfos($result['Icon'], '');
    }

    $graph = getInventoryGraph($display);
    /*
     * $head is header title of inventory tab
     * corresponding to tables in DB
     * Use an array to display friendly names
     * instead of Ugly table name
     */
    foreach ($result as $head => $vals) {
        /*
         * If a machine has many IP Adresses, they are stored like this
         * in database (separated by a slash):
         * x.x.x.x/x.x.x.x/x.x.x.x
         *
         * For machines with many IPs, display is very awful,
         * So search & replace slashes by \r\n
         */

        if ($head == 'IpAddress') {
            foreach ($vals as &$ipaddr) {
                $ipaddr = str_replace("/", "\r\n", $ipaddr);
            }
        }

        // Replace Database table names by human names
        $head = ($tabTitles[$head] != NULL) ? $tabTitles[$head] : $head;
        if (!in_array($head, $disabled_columns)) {
            if (in_array($head, $graph) && count($vals) > 1) {
                $type = ucfirst($_GET['part']);
                # TODO should give the tab in the from param
                $nhead = $head . " <a href='main.php?module=inventory&submod=inventory&action=graphs&type=$type&from=$from&field=$head";
                foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
                    $nhead .= "&$get=" . $_GET[$get];
                }
                $nhead .= "' alt='graph'><img src='modules/inventory/img/graph.png'/></a>";
                $head = $nhead;
            } else {
                $head = _T($head, 'inventory');
            }
            if ($n == null) {
                $n = new OptimizedListInfos($vals, $head);
            } else {
                $n->addExtraInfo($vals, $head);
            }
        }
    }

    print "<div style=\"overflow: auto\">";
    if ($n != null) {
        $n->addActionItem(new ActionItem(_T("View", "inventory"), "invtabs", "display", "inventory", "base", "computers"));
        $n->addActionItem(new ActionPopupItem(_T("Informations", "inventory"), "infos", "info", "inventory", "inventory", "inventory"));
        $n->setParamInfo($params);
        $n->setTableHeaderPadding(1);
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $maxperpage;
        $n->display();
    }
    print "</div>";
    ?><a href='<?php echo urlStr("inventory/inventory/csv", array('table' => $display, 'gid' => $_GET["gid"], 'filter' => $_GET['filter'])) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a><?php
}
?>

</table>

<script type="text/javascript">
    /* ==> CODE TO DISABLE
     jQuery('tbody tr td:not(.action)').click(function() {
     jQuery('#param').val(jQuery(this).text());
     pushSearch();
     });
     */
</script>

<?php
/**  to get i18n labels... */
// Yes/No translation hack
_T('Yes', 'inventory');
_T('No', 'inventory');
_T('Name', 'inventory');
_T('Network Type', 'inventory');
_T('MAC Address', 'inventory');
_T('IP', 'inventory');
_T('Netmask', 'inventory');
_T('Gateway', 'inventory');
_T('Device', 'inventory');
_T('Mount Point', 'inventory');
_T('Filesystem', 'inventory');
_T('Size', 'inventory');
_T('Free Size', 'inventory');
_T('Supplier', 'inventory');
_T('Invoice Number', 'inventory');
_T('Date Of Purchase', 'inventory');
_T('Warranty End Date', 'inventory');
_T('Vendor', 'inventory');
_T('Name', 'inventory');
_T('Version', 'inventory');
_T('Computer Name', 'inventory');
_T('Description', 'inventory');
_T('Entity (Location)', 'inventory');
_T('Entity', 'inventory');
_T('Location', 'inventory');
_T('Last Logged User', 'inventory');
_T('OS', 'inventory');
_T('Operating System', 'inventory');
_T('Computer Type', 'inventory');
_T('Model / Type', 'inventory');
_T('Model', 'inventory');
_T('Manufacturer', 'inventory');
_T('Serial Number', 'inventory');
_T('Frequency', 'inventory');
_T('Type', 'inventory');
_T('Size', 'inventory');
_T('Bandwidth', 'inventory');
_T('Writer', 'inventory');
_T('Memory', 'inventory');
_T('Comment', 'inventory');
_T('Date', 'inventory');
_T('User', 'inventory');
_T('Category', 'inventory');
_T('Action', 'inventory');
_T('Today', 'inventory');
_T('Last 7 days', 'inventory');
_T('Last 30 days', 'inventory');
_T('All', 'inventory');
_T('Service Pack', 'inventory');
_T('Windows Key', 'inventory');
_T('Domain', 'inventory');
_T('State', 'inventory');
_T('Unknown', 'inventory');
_T('Inventory Number', 'inventory');
// From Antivirus tab
_T('Enabled', 'inventory');
_T('Up-to-date', 'inventory');
?>
