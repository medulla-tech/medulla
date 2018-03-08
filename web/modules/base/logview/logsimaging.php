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
 * File : logsimaging.php
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
| sessionname | varchar(20)      | YES  |     |                   |                |
| how         | varchar(255)     | YES  |     | ""                |                |
| who         | varchar(45)      | YES  |     | ""                |                |
| why         | varchar(255)     | YES  |     | ""                |                |
| priority    | int(11)          | YES  |     | 0                 |                |
+-------------+------------------+------+-----+-------------------+----------------+
key criterium for search
'Menu',
'Post-imaging script creation',
'creation',
'edition'
'deletion ',
'Multicast',
'Backup',
'Image',
'WOL',
'deletion',
'Master',
'Menu',
'server',
'Manual',
'Multicast',
'Start',
'Postinstall',
'Configuration',
'Clone',
'Iso',
'Add',
'Edit',
'Group',
'delete',
'Service',
'Image',
From user (Acteur): Normalement utilisateur loggué à Pulse (pour MMC), Agent Machine, Master, ARS
Action: L'action
Module: Le module
Text: Détail
How: Le contexte: par exemple, lors d'un déploiement, planifié, etc.
Who: Nom du groupe ou de la machine
Why: Groupe ou machine
*/
?>
<script src="https://cdn.datatables.net/buttons/1.4.2/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/1.4.2/js/buttons.flash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.32/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.32/vfs_fonts.js"></script>
<script src="https://cdn.datatables.net/buttons/1.4.2/js/buttons.html5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/1.4.2/js/buttons.print.min.js"></script>
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

        function DateTimeTplnew($name, $label = null){
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
    function SelectItemlabeltitle($idElt, $label = null, $title = null, $jsFunc = null, $style = null) {
        $this->title = $title;
        $this->label = $label;
        parent::SelectItem($idElt, $jsFunc, $style);
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
    $p = new PageGenerator(_("Imaging Logs"));
    $p->setSideMenu($sidemenu);
    $p->display();
    $filterlogs = "Imaging";
    $headercolumn= "date@fromuser@who@text";
?>

<script type="text/javascript">

var filterlogs = <?php echo "'$filterlogs'";?>;

function encodeurl(){
    var critere = filterlogs +
                    "|" + jQuery('#criterionssearch option:selected').val() +
                    "|" + jQuery('#criterionssearch1 option:selected').val() +
                    "|" + jQuery('#criterionssearch2 option:selected').val() +
                    "|" + jQuery('#criterionssearch3 option:selected').val();
                    //+
                    //"|" + jQuery('#criterionssearch4 option:selected').val();

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
        jQuery("p").click(function(){
            searchlogs( encodeurl());
        //jQuery('#tablelog').DataTable().ajax.reload(null, false).draw();
        });
    });

    function searchlogs(url){
        jQuery('#tablelog').DataTable({
        'retrieve': true,
        "iDisplayLength": <?php echo $maxperpage; ?>,
        "lengthMenu" : [[10 ,20 ,30 ,40 ,50 ,75 ,100 ], [10, 20, 30, 40, 50 ,75 ,100 ]],
        "dom": '<"top"lfi>rt<"bottom"Bp><"clear">',
        buttons: [
        { extend: 'copy', className: 'btn btn-primary', text: <?php echo _('Copy to clipboard', logs); ?>},
        { extend: 'csv', className: 'btn btn-primary',  text: <?php echo _('Save to csv file', logs); ?> },
        { extend: 'excel', className: 'btn btn-primary',  text: <?php echo _('Save to Excel file', logs); ?> },
        { extend: 'print', className: 'btn btn-primary',  text: <?php echo _('Print logs', logs); ?>  }
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


$typecritere  =        array(
                                        _('Menu change','logs'),
                                        _('Post-imaging Script Creation','logs'),
                                        _('Master Creation','logs'),
                                        _('Master Edition','logs'),
                                        _('Master Deletion','logs'),
                                        _('Master Deployment Multicast','logs'),
                                        _('Backup Image creation','logs'),
                                        _('Image Deployment','logs'),
                                        _('WOL','logs'),
                                        _('Image Deletion','logs'),
                                        'Master',
                                        _('Menu'),
                                        _('Server'),
                                        _('Manual'),
                                        _('Multicast'),
                                        _('Start'),
                                        _('Postinstall'),
                                        _('Configuration'),
                                        _('Clone'),
                                        'Iso',
                                        'Add',
                                        _('Edit'),
                                        _('Group'),
                                        _('Delete'),
                                        _('Service'),
                                        _('Image'),
                                        _('Quick Action'),
                                        _('no criteria selected','logs'));

$typecritereval  =        array(
                                        'Menu',
                                        'Post-imaging script creation',
                                        'creation',
                                        'edition',
                                        'deletion',
                                        'Multicast',
                                        'Backup',
                                        'Image',
                                        'WOL',
                                        'deletion',
                                        'Master',
                                        'Menu',
                                        'server',
                                        'Manual',
                                        'Multicast',
                                        'Start',
                                        'Postinstall',
                                        'Configuration',
                                        'Clone',
                                        'Iso',
                                        'Add',
                                        'Edit',
                                        'Group',
                                        'delete',
                                        'Service',
                                        'Image',
                                        'QuickAction',
                                        'None');


$start_date =   new DateTimeTplnew('start_date', "Start Date");
$end_date   =   new DateTimeTplnew('end_date', "End Date");


$modules = new SelectItemlabeltitle("criterionssearch", "criterions", "critere search");
$modules->setElements($typecritere);
$modules->setSelected("None");
$modules->setElementsVal($typecritereval);

$modules1 = new SelectItemlabeltitle("criterionssearch1", "criterions", "critere search");
$modules1->setElements($typecritere);
$modules1->setSelected("None");
$modules1->setElementsVal($typecritereval);

$modules2 = new SelectItemlabeltitle("criterionssearch2", "criterions", "critere search");
$modules2->setElements($typecritere);
$modules2->setSelected("None");
$modules2->setElementsVal($typecritereval);

$modules3 = new SelectItemlabeltitle("criterionssearch3", "criterions", "critere search");
$modules3->setElements($typecritere);
$modules3->setSelected("None");
$modules3->setElementsVal($typecritereval);

// $modules4 = new SelectItemlabeltitle("criterionssearch4", "criterions", "critere search");
// $modules4->setElements($typecritere);
// $modules4->setSelected("None");
// $modules4->setElementsVal($typecritereval);

?>
</style>


<div style="overflow-x:auto;">
    <table border="1" cellspacing="0" cellpadding="5" class="listinfos">
        <thead>
            <tr>
                <th><?php echo $start_date->display(); ?></th>
                <th><?php echo $end_date->display(); ?></th>
                <th><?php echo $modules->display(); ?></th>
                <th><?php echo $modules1->display(); ?></th>
                <th><?php echo $modules2->display(); ?></th>
                <th><?php echo $modules3->display(); ?></th>
		<th><p class="btnPrimary">Filter logs</p></th>
            <!--    <th><?php //echo $modules4->display(); ?></th>-->
            </tr>
        </thead>
     </table>
</div>

<br>

<table id="tablelog" width="100%" border="1" cellspacing="0" cellpadding="1" class="listinfos">
        <thead>
            <tr>
                <th style="width: 12%;">date</th>
                <th style="width: 7%;">user</th>
                <th style="width: 7%;">who</th>
         <!--
                <th style="width: 6%;">type</th>
                <th style="width: 6%;">action</th>
                <th style="width: 6%;">module</th>

                <th style="width: 6%;">how</th>

                <th style="width: 6%;">why</th>

                <th style="width: 6%;">priority</th>
                <th style="width: 6%;">touser</th>
                <th style="width: 6%;">sessionname</th>
        -->
                <th>text</th>
            </tr>
        </thead>

    </table>
