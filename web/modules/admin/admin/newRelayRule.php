<?php
/*
 * (c) 2020 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 *
 */


require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");


if(isset($_POST['bconfirm'])){
  $relay_id = htmlentities($_POST['relay_id']);
  $rule_id = htmlentities($_POST['rule']);
  $order = htmlentities($_POST['rule_order']);
  // Originaly regex and subject were inverted
  $subject = htmlentities($_POST['regex']);

  $result = xmlrpc_add_rule_to_relay($relay_id, $rule_id, $order, $subject);

  if($result['status'] == 'success'){
    new NotifyWidgetSuccess(_T('Rule added to relay '.$_GET['hostname'], "admin"));
  }
  else{
    new NotifyWidgetFailure(_T('The rule has not been added to relay '.$_GET['hostname'], "admin"));
  }


  if(isset($_GET['prev_action'])){
    $action = htmlentities($_GET['prev_action']);
    $id = htmlentities($_GET['rule']);

    $params = [
      'id'=>$id,
      'jid'=>htmlentities($_GET['jid']),
      'hostname'=>htmlentities($_GET['hostname']),
    ];
    header("Location: " . urlStrRedirect("admin/admin/$action", $params));
  }
  else{
    header("Location: " . urlStrRedirect("admin/admin/rules_tabs", $_GET));
  }


exit;
}

$prev_action = (isset($_GET['prev_action'])) ? htmlentities($_GET['prev_action']) : "rules_tabs";
$rulesList = xmlrpc_get_rules_list(-1, -1, "");
$relaysList = xmlrpc_get_minimal_relays_list();

$f = new ValidatingForm();
$f->push(new Table());

//Get rules list
$rules = new SelectItem("rule");
$rules->setElements($rulesList['datas']['description']);
$rules->setElementsVal($rulesList['datas']['id']);
if(isset($_GET['prev_action']))
  $rules->setSelected($_GET['id']);

$new_rule_order = xmlrpc_new_rule_order_relay($_GET['id']);

// General infos for cluster
$f->add(new TrFormElement(_T("Rule", "admin"), $rules));
$hidden = new HiddenTpl('rule_order');
$f->add($hidden, ['value'=>$new_rule_order, 'hide'=>true]);

$relays = new SelectItem("relay_id");
$relays->setElements($relaysList['hostname']);
$relays->setElementsVal($relaysList['id']);
if(!isset($_GET['prev_action']))
  $relays->setSelected($_GET['id']);
$f->add(new TrFormElement(_T("Relays", "admin"), $relays));

$regex = new InputTpl("regex");
$regex->setAttributCustom('title="A few subject examples:
Chooses ARS based on network address:
^55\.33\.250\.0\/24$ -> Associates all machines which are in the 55.33.250.0/24 subnet to the specified relay server
^55\.171\.?[0-2]?[0-5]?[0-5].*\.0\/24$ -> Associates all machines which are in the 55.171.XXX.0/24 subnet to the specified relay server
Chooses ARS based on netmask:
255.255.255.255 -> Associates all machines having a netmask of 255.255.255.255 to the specifies relay server
Chooses ARS based on hostname:
^win10.*$ -> Associates all machines having a hostname starting with win10 to the specified relay server"');
$f->add(new TrFormElement(_T("Subject", "admin"), $regex));
$f->add(new TrFormElement(_T("Check regex", "admin"), new TextareaTpl("subject")));
$f->add(new TrFormElement(_T("Matching Result", "admin"), new SpanElement('<div id="temp"></div><div id="result"></div>')));

$f->addValidateButton("bconfirm", _T("Edit", "admin"), ['prev_action'=> $prev_action]);
$f->display();

$fontsize = 1.3;
?>
<style>
#result{
  font-size: 1.5em;
}
#temp{
  display:none;
}
</style>

<script>
jQuery(function(){
  //jQuery(".btnPrimary").prop("disabled", true);
  jQuery("#regex, #subject").on("click change", function(){
    subject = jQuery("#subject").val();
    regex_str = jQuery("#regex").val();
    regex = new RegExp(regex_str, 'gi');

    // ^win10\-.*$
    // ^win10\-[0-9]*$
    /*
    win10-5 win10-1 win10 win10-e
    win10-aa
    */
    //console.log("test : "+regex.test(subject))


    matches = false;
    found = ""

    found = subject.replace(regex, function(x){
      red = Math.floor(Math.random() * 256);
      green = Math.floor(Math.random() * 256);
      blue = Math.floor(Math.random() * 256);
      return '<span class="matched" style="font-size:1.2em;color:rgb('+red+','+green+','+blue+')">'+x+'</span>';
    });
    jQuery("#temp").html(found);
    jQuery("#temp").children('.matched').remove();

    result = jQuery("#temp").text()
    if(regex_str != ""){
      if(subject != ""){
        if(result == ""){
          matches = true;
        }
      }
    }

    if(matches){
      //jQuery(".btnPrimary").prop("disabled", false);
      jQuery("#result").html("Valid => "+found)
    }
    else{
      //jQuery(".btnPrimary").prop("disabled", true);
      jQuery("#result").html("Invalid => "+found)
    }

  });


});


</script>
