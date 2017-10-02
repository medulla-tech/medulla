<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
 * File : logview/index.php
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
*/
?>

<?php
    require("graph/navbar.inc.php");
    require("localSidebar.inc.php");
    $p = new PageGenerator(_("Alls Logs"));
    $p->setSideMenu($sidemenu);
    $p->display();
?>


<script type="text/javascript">

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

 function encodeurl(){
            uri = "modules/base/logview/ajax_Data_Logs.php"
            var param = {
                "start_date" :  jQuery('#start_date').val(),
                "end_date"   : jQuery('#end_date').val(),
                "type" : jQuery('#type option:selected').val(),
                "module" : jQuery('#module option:selected').val(),
                "action" : jQuery('#action option:selected').val()
            }
            uri = uri +"?"+xwwwfurlenc(param)
            return uri
        }

    jQuery(function(){

        jQuery("p").click(function(){
            dede( encodeurl());
        //jQuery('#example').DataTable().ajax.reload(null, false).draw();
        });
    }); 
<?php

print '
function dede(url){
    
    jQuery(\'#example\').DataTable()
                        .ajax.url(
                            url
                        )
                        .load();
}

    jQuery(function(){
        dede("modules/base/logview/ajax_Data_Logs.php")
    } );
    </script>';

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

$yes_no  =        array(
                                        _T('Yes','imaging'),
                                        _T('No','imaging'));

$typelog  =        array(
                                        _T('MMC','logs'),
                                        _T('AMR','logs'),
                                        _T('AM','logs'),
                                        _T('ARS','logs'),
                                        _T('None','logs'));

 $typemodule  =        array(
                                        _T('deploy','logs'),
                                        _T('quickaction','logs'),
                                        _T('imaging','logs'),
                                        _T('backup','logs'),
                                        _T('inventory','logs'),
                                        _T('None','logs'));

$typeaction  =         array(
                                        _T('event AM','logs'),
                                        _T('event ARS','logs'),
                                        _T('event AMR','logs'),
                                        _T('None','logs'));
$typeactionval  =        array(
                                        _T('evt_AM','logs'),
                                        _T('evt_ARS','logs'),
                                        _T('evt_AMR','logs'),
                                        _T('None','logs'));

$start_date =   new DateTimeTplnew('start_date', "Start Date");
$end_date   =   new DateTimeTplnew('end_date', "End Date");

$type = new SelectItemlabeltitle("type", "Type", "Provenance du logs");
$type->setElements($typelog);
$type->setElementsVal($typelog);
$type->setSelected("None");

$modules = new SelectItemlabeltitle("module", "Modules", "quategory du log");
$modules->setElements($typemodule);
$modules->setSelected("None");
$modules->setElementsVal($typemodule);


$action = new SelectItemlabeltitle("action", "Actions", "Evenement ACTION");
$action->setElements($typeaction);
$action->setElementsVal($typeactionval);
$action->setSelected("None");
?>

<style>

.inline { display : inline; }

th {
    background-color: #e6e6e6;
    color: blue;
    padding: 10px;
    height: 20px;
}

.bouton5 {
	border-radius:12px 0 12px 0;
	background: Black;
	border:none;
	color:white;
	font:bold 12px Verdana;
	padding:6px 0px 6px 0px;
	margin-left: auto;

    margin-right: 15px;
    text-align: center;
    width : 200px;
}

/*div.container {
        width: 80%;
    }*/
/*table, th, td {
    border: 1px solid black;
}*/
/*table {
    width: 100%;
    border-collapse: collapse;
}
th {
    height: 30px;
}
th {
    text-align: left;
}
td {
    height: 50px;
    vertical-align: bottom;
}
th, td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
th {
    background-color: #4CAF50;
    color: white;
}
tr:nth-child(even) {
    background-color: #f2f2f2
}*/

th.libelle {
    height: 10px;
    padding: 5px;
    background-color: #00fF50;
    color: blue;
}

</style>
<?php
 
?>


<div style="overflow-x:auto;">
    <table>
        <thead>
            <tr>
                <th><?php echo $start_date->display(); ?></th>
                <th><?php echo $end_date->display(); ?></th>
                <th><?php echo $type->display(); ?></th>
                <th><?php echo $modules->display(); ?></th>
                <th><?php echo $action->display(); ?></th>
            </tr>
        </thead>
      
     </table>
</div>
<p class="bouton5">
  VOIR LES LOGS
</p>

<br>

<table id="example" class="display" width="100%" cellspacing="0">
        <thead>
            <tr>
                <th style="width: 12%;">date</th>
                <th style="width: 8%;">user</th>
                <th style="width: 6%;">who</th>
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
        <tfoot>
            <tr>
                <th style="width: 12%;">date</th>
                <th style="width: 8%;">user</th>
                <th style="width: 6%;">who</th>
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
        </tfoot>

    </table>
