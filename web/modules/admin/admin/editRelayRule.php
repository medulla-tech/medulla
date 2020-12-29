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

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");


if(isset($_POST['bconfirm'])){
  $selected_rule = htmlentities($_POST['selected_rule']);
  $rule_id = htmlentities($_POST['rule']);
  // Originaly regex and subject were inverted
  $subject = htmlentities($_POST['regex']);
  $hostname = (isset($_GET['hostname'])) ? $_GET['hostname'] : "";

  $result = xmlrpc_edit_rule_to_relay($selected_rule, $rule_id, $subject);
  if($result['status'] == 'success'){
    new NotifyWidgetSuccess(_T('Rule edited to relay '.$hostname, "admin"));
  }
  else{
    new NotifyWidgetFailure(_T('The rule has not been edited to relay '.$hostname, "admin"));
  }
header("Location: " . urlStrRedirect("admin/admin/rules_tabs", [
  'id'=>htmlentities($_GET['id']),
  'jid'=>htmlentities($_GET['jid']),
  'hostname'=>htmlentities($_GET['hostname']),
]));
exit;

$rulename = (isset($_GET['name'])) ? htmlentities($_GET['name']) : "";
$hostname = (isset($_GET['hostname'])) ? htmlentities($_GET['hostname']) : "";
$ruleid = (isset($_GET['rule_id'])) ? htmlentities($_GET['rule_id']) : 0;

$p = new PageGenerator(_T("Edit Rule $rulename on relay [$hostname]", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

$relayRule = xmlrpc_get_relay_rule($ruleid);
$rulesList = xmlrpc_get_rules_list(-1, -1, "");

$f = new ValidatingForm();
$f->push(new Table());

if($relayRule['status'] != "error"){
//Get rules list
$rules = new SelectItem("rule");
$rules->setElements($rulesList['datas']['description']);
$rules->setElementsVal($rulesList['datas']['id']);
$rules->setSelected($relayRule['datas']['rules_id']);

// General infos for cluster
$f->add(new TrFormElement(_T("Rule", "admin"), $rules));

$hidden = new HiddenTpl('selected_rule');
$f->add($hidden, ['value'=>$ruleid, 'hide'=>true]);
$regex = new InputTpl("regex");
$regex->setAttributCustom('title="A few subject examples:
Chooses ARS based on network address:
^55\.33\.250\.0\/24$ -> Associates all machines which are in the 55.33.250.0/24 subnet to the specified relay server
^55\.171\.?[0-2]?[0-5]?[0-5].*\.0\/24$ -> Associates all machines which are in the 55.171.XXX.0/24 subnet to the specified relay server
Chooses ARS based on netmask:
255.255.255.255 -> Associates all machines having a netmask of 255.255.255.255 to the specifies relay server
Chooses ARS based on hostname:
^win10.*$ -> Associates all machines having a hostname starting with win10 to the specified relay server"');
$f->add(new TrFormElement(_T("Subject", "admin"), $regex), ['value'=>$relayRule['datas']['subject']]);
$f->add(new TrFormElement(_T("Check regex", "admin"), new TextareaTpl("subject")));
$f->add(new TrFormElement(_T("Matching Result", "admin"), new SpanElement('<div id="temp"></div><div id="result"></div>')));

$f->addValidateButton("bconfirm", _T("Edit", "admin"));
$f->display();

}

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
