<?php
/**
 *
 * (c) 2015-2017 Siveo, http://http://www.siveo.net
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
 * File : logsmobile.php
 */

 /*
 this page show logs table
+-------------+------------------+------+-----+-------------------+----------------+
| Field       | Type             | Null | Key | Default           | Extra          |
+-------------+------------------+------+-----+-------------------+----------------+
| date        | timestamp        | NO   |     | CURRENT_TIMESTAMP |                |
| fromuser    | varchar(45)      | YES  |     | NULL              |                |
| touser      | varchar(45)      | YES  |     | NULL              |                |
| action      | varchar(45)      | YES  |     | NULL              |                |
| type        | varchar(6)       | NO   |     | noset             |                |
| module      | varchar(45)      | YES  |     |                   |                |
| text        | varchar(255)     | NO   |     | NULL              |                |
| sessionname | varchar(45)      | YES  |     |                   |                |
| how         | varchar(255)     | YES  |     | ""                |                |
| who         | varchar(45)      | YES  |     | ""                |                |
| why         | varchar(255)     | YES  |     | ""                |                |
| priority    | int(11)          | YES  |     | 0                 |                |
+-------------+------------------+------+-----+-------------------+----------------+
key criterium for search

Mobile
Device
Configuration
Group
Quick Action
Deployment
User
Message
Push Message
*/
?>
<script src="jsframework/lib/plugin.jquery-ui/datatable/js/dataTables.buttons.min.js"></script>
<script src="jsframework/lib/plugin.jquery-ui/datatable/js/buttons.flash.min.js"></script>
<script src="jsframework/lib/jszip.min.js"></script>
<script src="jsframework/lib/pdfmake.min.js"></script>
<script src="jsframework/lib/vfs_fonts.js"></script>
<script src="jsframework/lib/plugin.jquery-ui/datatable/js/buttons.html5.min.js"></script>
<script src="jsframework/lib/plugin.jquery-ui/datatable/js/buttons.print.min.js"></script>


<?php
    require("graph/navbar.inc.php");
    require("localSidebar.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
if ($maxperpage >= 100){
    $maxperpage = 100;
}
elseif($maxperpage >= 75){
    $maxperpage = 75;
}
elseif($maxperpage >= 50){
    $maxperpage = 50;
}

    class DateTimeTplnew extends DateTimeTpl{

        function __construct($name, $label = null){
            $this->label = $label;
            parent::__construct($name);
        }

        function display($arrParam = array()) {
            print "<label for=\"".$this->name."\">".$this->label."</label>\n";
            parent::display($arrParam);
        }
    }

class SelectItemlabeltitle extends SelectItem {
    var $title;
    /**
     * constructor
     */
    function __construct($idElt, $label = null, $title = null, $jsFunc = null, $style = null) {
        $this->title = $title;
        $this->label = $label;
        parent::__construct($idElt, $jsFunc, $style);
    }

    function to_string($paramArray = null) {
        $ret = "";
        if ($this->label){
            $ret = "<label for=\"".$this->id."\">".$this->label."</label>\n";
        }

        $ret .= "<select";
        if ($this->title){
            $ret .= " title=\"" . $this->title . "\"";
        }
        if ($this->style) {
            $ret .= " class=\"" . $this->style . "\"";
        }
        if ($this->jsFunc) {
            $ret .= " onchange=\"" . $this->jsFunc . "(";
            if ($this->jsFuncParams) {
                $ret .= implode(", ", $this->jsFuncParams);
            }
            $ret .= "); return false;\"";
        }
        $ret .= isset($paramArray["required"]) ? ' rel="required"' : '';
        $ret .= " name=\"" . $this->name . "\" id=\"" . $this->id . "\">\n";
        $ret .= $this->content_to_string($paramArray);
        $ret .= "</select>";
        return $ret;
    }
}
// ------------------------------------------------------------------------------------------------
    $p = new PageGenerator(_T("Mobile Device Logs", "base"));
    $p->setSideMenu($sidemenu);
    $p->display();

    $init_device   = isset($_GET['device'])   ? htmlspecialchars(trim($_GET['device']),   ENT_QUOTES, 'UTF-8') : '';
    $init_severity = isset($_GET['severity']) ? htmlspecialchars(trim($_GET['severity']), ENT_QUOTES, 'UTF-8') : '-1';

    $start_date = new DateTimeTplnew('start_date', _T("Start Date", "base"));
    $end_date   = new DateTimeTplnew('end_date',   _T("End Date",   "base"));

    $severity_labels = [
        '1' => _T('Error',   'base'),
        '2' => _T('Warning', 'base'),
        '3' => _T('Info',    'base'),
        '4' => _T('Debug',   'base'),
        '5' => _T('Verbose', 'base'),
    ];
?>

<script type="text/javascript">
var _logTable = null;

function buildLogsUrl() {
    var severities = [];
    jQuery('#severity-dropdown input:checked').each(function(){ severities.push(jQuery(this).val()); });
    return 'modules/base/logview/ajax_mobile_device_logs.php'
        + '?device='     + encodeURIComponent(jQuery('#log_device').val())
        + '&package='    + encodeURIComponent(jQuery('#log_package').val())
        + '&severity='   + encodeURIComponent(severities.length === 1 ? severities[0] : '-1')
        + '&start_date=' + encodeURIComponent(jQuery('#start_date').val())
        + '&end_date='   + encodeURIComponent(jQuery('#end_date').val())
        + '&pagesize=<?php echo (int)$maxperpage; ?>';
}

function reloadLogs() {
    if (_logTable) {
        _logTable.ajax.url(buildLogsUrl()).load();
    }
}

jQuery(function() {
    jQuery('.log-filters').on('change', 'select, input[type="text"]', function() { reloadLogs(); });

    jQuery('.checkbox-dropdown-toggle').on('click', function(e) {
        e.stopPropagation();
        jQuery(this).closest('.checkbox-dropdown').toggleClass('open');
    });
    jQuery(document).on('click', function() { jQuery('.checkbox-dropdown').removeClass('open'); });
    jQuery('.checkbox-dropdown-clear').on('click', function(e) {
        e.stopPropagation();
        var dd = jQuery(this).closest('.checkbox-dropdown');
        dd.find('input:checked').prop('checked', false);
        dd.find('.checkbox-dropdown-text').text('<?php echo addslashes(_T("No criteria selected", "base")); ?>');
        dd.removeClass('has-selection');
        reloadLogs();
    });
    jQuery('.checkbox-dropdown-menu input[type="checkbox"]').on('change', function() {
        var dd = jQuery(this).closest('.checkbox-dropdown');
        var checked = dd.find('input:checked');
        var text = checked.length
            ? checked.length + ' <?php echo addslashes(_T("selected", "base")); ?>'
            : '<?php echo addslashes(_T("No criteria selected", "base")); ?>';
        dd.find('.checkbox-dropdown-text').text(text);
        dd.toggleClass('has-selection', checked.length > 0);
        reloadLogs();
    });

    jQuery('#log_device, #log_package').on('keypress', function(e) {
        if (e.which === 13) reloadLogs();
    });

    _logTable = jQuery('#tablelog').DataTable({
        'retrieve': true,
        'ajax': buildLogsUrl(),
        'columns': [
            { 'title': '<?php echo addslashes(_T("Time",     "base")); ?>' },
            { 'title': '<?php echo addslashes(_T("Device",   "base")); ?>' },
            { 'title': '<?php echo addslashes(_T("Package",  "base")); ?>' },
            { 'title': '<?php echo addslashes(_T("Severity", "base")); ?>' },
            { 'title': '<?php echo addslashes(_T("Message",  "base")); ?>' }
        ],
        'createdRow': function(row) {
            jQuery('td', row).each(function() { this.title = this.textContent; });
        },
        'iDisplayLength': <?php echo (int)$maxperpage; ?>,
        'lengthMenu': [[10, 20, 30, 40, 50, 75, 100], [10, 20, 30, 40, 50, 75, 100]],
        'dom': '<"top"lfi>rt<"bottom"Bp><"clear">',
        'order': [[0, 'desc']],
        'language': {
            'search':      '<?php echo addslashes(_T("Search:", "base")); ?>',
            'lengthMenu':  '<?php echo addslashes(_T("Show _MENU_ entries", "base")); ?>',
            'info':        '<?php echo addslashes(_T("Showing _START_ to _END_ of _TOTAL_ entries", "base")); ?>',
            'infoEmpty':   '<?php echo addslashes(_T("No entries", "base")); ?>',
            'infoFiltered': '(<?php echo addslashes(_T("filtered from _MAX_ total entries", "base")); ?>)',
            'zeroRecords': '<?php echo addslashes(_T("No matching records found", "base")); ?>',
            'emptyTable':  '<?php echo addslashes(_T("No data available", "base")); ?>',
            'paginate': {
                'first':    '<?php echo addslashes(_T("First",    "base")); ?>',
                'previous': '<?php echo addslashes(_T("Previous", "base")); ?>',
                'next':     '<?php echo addslashes(_T("Next",     "base")); ?>',
                'last':     '<?php echo addslashes(_T("Last",     "base")); ?>'
            }
        },
        'buttons': [
            { extend: 'copy',  className: 'btn btn-primary', text: '<?php echo addslashes(_T("Copy",         "base")); ?>' },
            { extend: 'csv',   className: 'btn btn-primary', text: '<?php echo addslashes(_T("Export CSV",   "base")); ?>' },
            { extend: 'excel', className: 'btn btn-primary', text: '<?php echo addslashes(_T("Export Excel", "base")); ?>' },
            { extend: 'print', className: 'btn btn-primary', text: '<?php echo addslashes(_T("Print",        "base")); ?>' }
        ]
    });
});
</script>

<div class="log-filters">
    <div class="log-filter-item"><?php echo $start_date->display(array('value' => date('Y-m-d 00:00:00'))); ?></div>
    <div class="log-filter-item"><?php echo $end_date->display(array('value' => date('Y-m-d 23:59:59'))); ?></div>
    <div class="log-filter-item">
        <label><?php echo _T("Device", "base"); ?></label>
        <input type="text" class="searchfieldreal" id="log_device"
               value="<?php echo $init_device; ?>" />
    </div>
    <div class="log-filter-item">
        <label><?php echo _T("Package", "base"); ?></label>
        <input type="text" class="searchfieldreal" id="log_package" />
    </div>
    <div class="log-filter-item">
        <label><?php echo _T("Severity", "base"); ?></label>
        <div class="checkbox-dropdown" id="severity-dropdown">
            <div class="checkbox-dropdown-toggle">
                <span class="checkbox-dropdown-text"><?php echo _T("No criteria selected", "base"); ?></span>
                <span class="checkbox-dropdown-clear">&#10005;</span>
                <span>&#9660;</span>
            </div>
            <div class="checkbox-dropdown-menu">
                <?php foreach ($severity_labels as $val => $label): ?>
                <label>
                    <input type="checkbox" name="severity[]" value="<?php echo $val; ?>"
                           <?php echo ($init_severity === (string)$val) ? 'checked' : ''; ?>>
                    <?php echo $label; ?>
                </label>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
</div>

<table id="tablelog" class="listinfos">
    <thead>
        <tr>
            <th><?php echo _T("Time",     "base"); ?></th>
            <th><?php echo _T("Device",   "base"); ?></th>
            <th><?php echo _T("Package",  "base"); ?></th>
            <th><?php echo _T("Severity", "base"); ?></th>
            <th><?php echo _T("Message",  "base"); ?></th>
        </tr>
    </thead>
</table>
