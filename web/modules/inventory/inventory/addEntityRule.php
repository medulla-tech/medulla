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
require_once("modules/inventory/includes/addentityrule.inc.php");
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");


$params1 = array('min' => 0,'filters' => array());
$entity=getLocationAll($params1);

function locationtoid($entity,$valeur){
    foreach($entity['data'] as $val )
    {
        if( $val['Label'] == $valeur) return  $val['id'];
    }
}

$entityroot=$entity['data'][0]['Label'];
$entityidroot = 1;
//echo $entityroot;

$operatorType=operatorTagAll();
if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;
$params = array(
    'min' => $start,
    'max' => $start + $maxperpage,
    'filters' => ''
);

if (isset($_GET["filter"]) && $_GET["filter"])
    $params['filters']= $_GET["filter"];
 
// Receiving form data
if (isset($_POST['bconfirm'])){
    if (!isset($_GET['numRule'])){
   
        addEntityRule($_POST);
        if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The entity rule has been added successfully.", "inventory"));
    }
    else{
        addEntityRule($_POST);
        header('location: main.php?module=base&submod=computers&action=entityRules');
    }
}

$rule=array();
$datarule = parse_file_rule($params);
if (isset($_GET['numRule'])){
    $regle = $_GET['numRule'];
    //edition rule mode
    foreach ($datarule['data'] as $val ){
        //echo $val['numRule'];
        if($val['numRule'] == $regle){
            $rule[]=$val;
            $exitrule = True;
        }
    }
}
else{
    // add rule mode    
    $rule[]= array( "operand1"   => "Network/IP",
                    "operand2"   => "/.*/",
                    "entitie"    => $entityroot,
                    "aggregator" => "",
                    "operator"   => "match",
                    "actif"      => 1,
                    "numRule"    => $datarule['nb_regle']+1 );
}

if (!isset($regle)){
    $newnumRule = $datarule['nb_regle']+1;
}
else{
    $newnumRule = $regle;
}

$p = new PageGenerator(_T("Add rule", 'inventory'));
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm();
$f->push(new Table());
$f->add(
    new TrFormElement(_T("Active", "inventory"), new CheckboxTpl('active')), array("value" => ($rule[0]['actif'] == 1 ? 'checked' : ''))
);

$selectOperatorType=new SelectItemtitle("operator[]",_T('selection from this item','inventory')."\n".);
$selectOperatorType->setElements($operatorType);
$selectOperatorType->setElementsVal($operatorType);

$aggregator_select = new SelectItemtitle("aggregator",_T('aggregator a rule','inventory')."\n".
                                                      _T('AND all rules TRUE select entitie','inventory')."\n".
                                                      _T('OR one rule TRUE select entitie','inventory')."\n".
                                                      _T('NONE rule TRUE select entitie','inventory'));
$aggregator_select->setElements(array('AND', 'OR','NONE'));
$aggregator_select->setElementsVal(array('AND', 'OR',''));
$f->add(
    new TrFormElement(_T('Aggregator','inventory'), $aggregator_select),
    array("value" =>$rule[0]['aggregator'] )//,"required" => True
);
// or sans aggregator
//$f->add(new HiddenTpl("aggregator"), array("value" => "", "hide" => True));

$operator_select = new SelectItemtitle("operators[]", 
                                                    _T('Match','inventory').":\n".
                                                    _T(' regular expression','inventory')."\n".
                                                    _T(' special characters must be escaped in regular expressions','inventory')."\n".
                                                    _T(' .^$*+?()[{\|')."\n".
                                                    _T(' not start with word   /^(?!my string).*$/','inventory')."\n".
                                                    _T(' start with my string /^my string.*$/','inventory')."\n".
                                                    _T(' does not contain /^((?!my string).)*$/','inventory')."\n".
                                                    _T(' egal to or contains','inventory')."/my string/"."\n".
                                                    _T(' finishes by  /.*(my string)$/','inventory')."\n\n".
                                                    _T('Equal or noequal','inventory').":\n".
                                                    _T(' strictly equal or inequality','inventory')."\n\n".
                                                    _T('Contains or NoContains','inventory').":\n".
                                                    _T(' has value or not','inventory')."\n\n".
                                                    _T('Starts by or Finishes','inventory').":\n".
                                                    _T(' begins or ends with value','inventory'));
$operators = array( "match"=> _T('matches (regex)', 'inventory'),
                    "equal"=> _T('equal', 'inventory'),
                    "noequal"=> _T('not equal', 'inventory'),
                    "contains"=> _T('contains', 'inventory'),
                    "nocontains"=> _T('not contains', 'inventory'),
                    "starts"=> _T('starts by', 'inventory'),
                    "finishes"=> _T('finishes by', 'inventory')
);
$operator_select->setElements(array_values($operators));        
$operator_select->setElementsVal(array_keys($operators));

$locations_select = new SelectItemtitle("target_location[]",_T('entities list','inventory'));
$location_list = array();
foreach ($entity['data'] as $location){
    $location_list[$location['id']] = $location['Label'];
}
$locations_select->setElements(array_values($location_list));
$locations_select->setElementsVal(array_keys($location_list));

$pattern_input = new InputTplTitle('patterns[]',_T('regular expression or value','inventory')."\n".
                                    _T('must not contain space character','inventory')."\n");

for ($i = 0 ; $i < count($rule); $i++) {
    // Fields//$criteria_select,
    $fields = array(
        new SpanElement("<br>"),
        $locations_select,
        new SpanElement("<br>"),
        $selectOperatorType,
        new SpanElement("<br>"),
        $operator_select,
        new SpanElement("<br>"),
        $pattern_input,
        new SpanElement("<br>"),
        new buttonTpl2('removeLine',_T('Remove', 'inventory'),'removeLine')
    );

$values = array(
    "",
    locationtoid($entity,$rule[$i]['entitie']),
    "",
    $rule[$i]['operand1'],
    "",
    $rule[$i]['operator'],
    "",
    $rule[$i]['operand2'],"");

    $f->add(
        new TrFormElement(_T('Criterion','inventory'), new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
}

// Add line button
$addEntityRightBtn = new buttonTpl2('addLine',_T('Add criterion','inventory'));
$addEntityRightBtn->setClass('btnPrimary');
$f->add(
    new TrFormElement('', $addEntityRightBtn),
    array()
);

    $f->add(new HiddenTpl("numRuleadd"), array("value" => $newnumRule, "hide" => True));
$f->pop();
$f->addValidateButton("bconfirm");
$f->display();
?>

<script type="text/javascript">
jQuery(function(){

    modelLine = jQuery('.removeLine:first').parents('tr:first').clone();

     // Remove line button
     jQuery('.removeLine').click(function(){
         if (jQuery('.removeLine').length > 1)
             jQuery(this).parents('tr:first').remove();
     });

     // Add line button
     jQuery('#addLine').click(function(){
        var newline = modelLine.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find('input[type=text]').val('');
         newline.find('textarea').val('');

         newline.find('.removeLine').click(function(){
            if (jQuery('.removeLine').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });
    jQuery('#operators').on('change', function() {
        console.log( this.value );
    });
});
window.toto=1;
</script>