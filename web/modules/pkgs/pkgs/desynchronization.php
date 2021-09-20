<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/package_api.php");

$packageuuid =  base64_decode ( $_GET['pid']);
$label = base64_decode ( $_GET['plabel']);
$version = base64_decode ( $_GET['pversion']);
//interoge la table syncthingsync
$infopackage = xmlrpc_pkgs_get_info_synchro_packageid($packageuuid);

$nosynchrolist = $infopackage[0];
$relayserverlist =  $infopackage[1];

if(isset($_POST['package']))
{
  xmlrpc_delete_from_pending($packageuuid, []);
  header("Location: " . urlStrRedirect("pkgs/pkgs/pending", array('deletependingsuccess' => 'package', 'name'=>$label)));
}
else if(isset($_POST['jid']))
{
  xmlrpc_delete_from_pending($packageuuid, $_POST['relays']);

  $relaylist = [];
  foreach($_POST['relays'] as $relay){
    $relaylist[] = explode('@', $relay)[0];
  }
  header("Location: " . urlStrRedirect("pkgs/pkgs/pending", array('deletependingsuccess' => 'jid', 'jids'=>implode(', ', $relaylist), 'name'=>$label)));
}
else{
  if(isExpertMode()){
    $fg = new PopupForm(_T("Delete Pending", "pkgs"));
    $actionsList = new SelectItem('pending-select','loadForm');
    //$actionsList->setElements([_T('Remove package '.$label.' from pending', 'pkgs'), _T('Remove specific jids from '.$label.' package pending','pkgs'), _T('Clean all pendings','pkgs')]);
    $actionsList->setElements([_T('Remove package '.$label.' from pending', 'pkgs'), _T('Remove specific jids from '.$label.' package pending','pkgs')]);
    //$actionsList->setElementsVal(['package', 'jid', 'all']);
    $actionsList->setElementsVal(['package', 'jid']);
    $actionsList->setSelected('package');
    $fg->add($actionsList);
    $fg->display();

    /*
    // keep it if we want to restore the option 'all' easilly
    echo '<div id="all" class="spaced">';
    $fall = new PopupForm(_T('Clean all pendings','pkgs'));
    $fall->addValidateButton("all");
    $fall->addCancelButton("bback");
    $fall->display();
    echo '</div>';*/

    echo '<div id="package" class="spaced">';
    $fpackage = new PopupForm(_T('Remove package '.$label.' from pending', 'pkgs'));
    $fpackage->addValidateButton("package");
    $fpackage->addCancelButton("bback");
    $fpackage->display();
    echo '</div>';

    echo '<div id="jid" class="spaced">';
    $fjid = new PopupForm(_T('Remove specific jids from '.$label.' package pending', 'pkgs'));
    $fjid->addValidateButton("jid");

    foreach($nosynchrolist as $relay){
      $fjid->add(new CheckboxTpl('relays[]', explode("@", $relay['relayserver_jid'])[0], ""), ['value'=>'value="'.$relay['relayserver_jid'].'"']);
    }

  $fjid->addCancelButton("bback");
  $fjid->display();
  echo '</div>';
  ?>
  <script>
  var option = jQuery("#pending-select").val();
  jQuery("#package").show();
  //jQuery("#all").hide();
  jQuery("#jid").hide();
  jQuery("#pending-select").on('change', );

  function loadForm(){
    var option = jQuery("#pending-select").val();
    if(option == 'package'){
      jQuery("#package").show();
      //jQuery("#all").hide();
      jQuery("#jid").hide();
    }
    else if(option == 'all'){
      jQuery("#package").hide();
      //jQuery("#all").show();
      jQuery("#jid").hide();
    }
    else if(option == 'jid'){
      jQuery("#package").hide();
      //jQuery("#all").hide();
      jQuery("#jid").show();
    }
  }
  </script>
<? }// End expert mode
  else{
    $f = new PopupForm(_T("Delete the $name from pending", 'pkgs'));
    $f->addValidateButton("package");
    $f->addCancelButton("bback");
    $f->display();
  }
}?>

<style>
.spaced h2{
  margin-bottom:5px;
  margin-top:5px;
}
</style>
