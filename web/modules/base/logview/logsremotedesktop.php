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
 * File : logsbackup.php
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


Remote_desktop | service| Manual | User
Remote_desktop | Remote desktop control request | Manual | User
Remote_desktop | Reverse SSH start | Remote desktop control request | ARS
Remote_desktop | Reverse SSH stop | Remote desktop control request | ARS


From user (Acteur): Normalement utilisateur loggué à Pulse (pour MMC), Agent Machine, Master, ARS
Action: L'action
Module: Le module
Text: Détail
How: Le contexte: par exemple, lors d'un déploiement, planifié, etc.
Who: Nom du groupe ou de la machine
Why: Groupe ou machine

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
    $p = new PageGenerator(_T("Remote Desktop Logs","base"));
    $p->setSideMenu($sidemenu);
    $p->display();
    $filterlogs = "Remote_desktop";
    $headercolumn = "date@fromuser@who@text";
?>

<script type="text/javascript">

    var filterlogs = <?php echo "'$filterlogs'";?>;

    function encodeurl(){
        var selected = [];
        jQuery('#criteria-dropdown input:checked').each(function(){ selected.push(jQuery(this).val()); });
        var critere = filterlogs + "|" + (selected.length ? selected.join(",") : "None") + "|" + jQuery('#criteriadetail option:selected').val();
        uri = "modules/base/logview/ajax_Data_Logs.php"
        //QuickAction
        var param = {
            "start_date" : jQuery('#start_date').val(),
            "end_date"   : jQuery('#end_date').val(),
            "type" : "",
            "action" : "",
            "module" : critere,
            "user" : "",
            "how" : "",
            "who" : "",
            "why" : "",
            "headercolumn" : "<?php echo $headercolumn; ?>"
        }
        uri = uri +"?"+xwwwfurlenc(param)
        return uri
    }

    function xwwwfurlenc(srcjson){
        if(typeof srcjson !== "object")
        if(typeof console !== "undefined"){
            console.log("\"srcjson\" is not a JSON object");
            return null;
        }
        u = encodeURIComponent;
        var urljson = "";
        var keys = Object.keys(srcjson);
        for(var i=0; i <keys.length; i++){
            urljson += u(keys[i]) + "=" + u(srcjson[keys[i]]);
            if(i < (keys.length-1))urljson+="&";
        }
        return urljson;
    }

    jQuery(function(){
        jQuery('.log-filters').on('change', 'select, input', function(){
            searchlogs( encodeurl());
        });
        jQuery('.checkbox-dropdown-toggle').on('click', function(e){
            e.stopPropagation();
            jQuery(this).closest('.checkbox-dropdown').toggleClass('open');
        });
        jQuery(document).on('click', function(){ jQuery('.checkbox-dropdown').removeClass('open'); });
        jQuery('.checkbox-dropdown-clear').on('click', function(e){
            e.stopPropagation();
            var dd = jQuery(this).closest('.checkbox-dropdown');
            dd.find('input:checked').prop('checked', false);
            dd.find('.checkbox-dropdown-text').text('<?php echo addslashes(_T("No criteria selected", "base")); ?>');
            dd.removeClass('has-selection');
            searchlogs(encodeurl());
        });
        jQuery('.checkbox-dropdown-menu input[type="checkbox"]').on('change', function(){
            var dd = jQuery(this).closest('.checkbox-dropdown');
            var checked = dd.find('input:checked');
            var text = checked.length
                ? checked.length + ' <?php echo addslashes(_T("selected", "base")); ?>'
                : '<?php echo addslashes(_T("No criteria selected", "base")); ?>';
            dd.find('.checkbox-dropdown-text').text(text);
            dd.toggleClass('has-selection', checked.length > 0);
            searchlogs(encodeurl());
        });
    });
    function searchlogs(url){
        jQuery('#tablelog').DataTable({
                                'retrieve': true,
                                'createdRow': function(row) { jQuery('td', row).each(function() { this.title = this.textContent; }); },
                                "iDisplayLength": <?php echo $maxperpage; ?>,
                                "lengthMenu" : [[10 ,20 ,30 ,40 ,50 ,75 ,100 ], [10, 20, 30, 40, 50 ,75 ,100 ]],
                                "dom": '<"top"lfi>rt<"bottom"Bp><"clear">',
                                'order': [[ 0, "desc" ]],
                            "language": {
                                "search": "<?php echo _T('Search:', 'base'); ?>",
                                "lengthMenu": "<?php echo _T('Show _MENU_ entries', 'base'); ?>",
                                "info": "<?php echo _T('Showing _START_ to _END_ of _TOTAL_ entries', 'base'); ?>",
                                "infoEmpty": "<?php echo _T('No entries', 'base'); ?>",
                                "infoFiltered": "(<?php echo _T('filtered from _MAX_ total entries', 'base'); ?>)",
                                "zeroRecords": "<?php echo _T('No matching records found', 'base'); ?>",
                                "emptyTable": "<?php echo _T('No data available', 'base'); ?>",
                                "paginate": {
                                    "first": "<?php echo _T('First', 'base'); ?>",
                                    "previous": "<?php echo _T('Previous', 'base'); ?>",
                                    "next": "<?php echo _T('Next', 'base'); ?>",
                                    "last": "<?php echo _T('Last', 'base'); ?>"
                                }
                            },
                                buttons: [
                                { extend: 'copy', className: 'btn btn-primary', text: '<?php echo _T("Copy", "base"); ?>' },
                                { extend: 'csv', className: 'btn btn-primary',  text: '<?php echo _T("Export CSV", "base"); ?>' },
                                { extend: 'excel', className: 'btn btn-primary',  text: '<?php echo _T("Export Excel", "base"); ?>' },
                                { extend: 'print', className: 'btn btn-primary',  text: '<?php echo _T("Print", "base"); ?>' }
                                ]
                            } )
                            .ajax.url(
                                url
                            )
                            .load();
    }

    jQuery(function(){
        searchlogs("modules/base/logview/ajax_Data_Logs.php?start_date=&end_date=&type=&action=&module=<?php echo $filterlogs; ?>%7CNone&user=&how=&who=&why=&headercolumn=<?php echo $headercolumn; ?>")
    } );
    </script>

<?php

/*
Remote_desktop | service| Manual | User
Remote_desktop | Remote desktop control request | Manual | User
Remote_desktop | Reverse SSH start | Remote desktop control request | ARS
Remote_desktop | Reverse SSH stop | Remote desktop control request | ARS
*/

$typecritere  =        array(
                                        _T('Remote desktop service','base'),
                                        _T('Remote desktop control request','base'),
                                        _T('Reverse SSH','base'),
                                        _T("No criteria selected", "base"));

$typecritereval  =        array(
                                        'Service',
                                        'Sontrol',
                                        'Reverse SSH',
                                        'None');

$start_date =   new DateTimeTplnew('start_date', _T("Start Date", "base"));
$end_date   =   new DateTimeTplnew('end_date', _T("End Date", "base"));

?>



<div class="log-filters">
    <div class="log-filter-item"><?php echo $start_date->display(array('value' => date('Y-m-d 00:00:00'))); ?></div>
    <div class="log-filter-item"><?php echo $end_date->display(array('value' => date('Y-m-d 23:59:59'))); ?></div>
    <div class="log-filter-item">
        <label><?php echo _T("Criteria", "base"); ?></label>
        <div class="checkbox-dropdown" id="criteria-dropdown">
            <div class="checkbox-dropdown-toggle">
                <span class="checkbox-dropdown-text"><?php echo _T("No criteria selected", "base"); ?></span>
                <span class="checkbox-dropdown-clear">&#10005;</span>
                <span>&#9660;</span>
            </div>
            <div class="checkbox-dropdown-menu">
                <?php foreach ($typecritere as $i => $label): ?>
                    <?php if ($typecritereval[$i] !== 'None'): ?>
                    <label>
                        <input type="checkbox" name="criteria[]" value="<?php echo $typecritereval[$i]; ?>">
                        <?php echo $label; ?>
                    </label>
                    <?php endif; ?>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
</div>

<table id="tablelog" class="listinfos">
    <thead>
        <tr>
            <th><?php echo _('date'); ?></th>
            <th><?php echo _('user'); ?></th>
            <th><?php echo _('who'); ?></th>
            <th><?php echo _('text'); ?></th>
        </tr>
    </thead>
</table>
