<?php
/*
 * (c) 2016 Siveo, http://www.siveo.net
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
 */

?>
<style type='text/css'>
textarea        {
width:50% ;
height:150px;
margin:auto; /* exemple pour centrer */
display:block;/* pour effectivement centrer ! */
}
</style>


<?
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");


function searchjiddeploy($jid, $struct){
    $datadeploy = array();
    foreach ( $struct as $chatroomdeploy => $differentmachine){
        $jidrelayserver = "";
        $jidmachine = "";
        foreach ( $differentmachine as $uniquehostname => $infomachine){
            if ($infomachine['agenttype']  == "relayserver"){
                $jidrelayserver =  $infomachine['jid'];
            }
            if ($infomachine['agenttype']  == "machine" && $infomachine['jid'] == $jid){
                $jidmachine = $infomachine['jid'];
            }
        }
        if ($jidrelayserver!="" &&  $jidmachine !=""){
            $datadeploy[]=$jidrelayserver;
            $datadeploy[]=$jidmachine;
            return $datadeploy;
        }
    }
    return $datadeploy;
}


$p = new PageGenerator(_T("Console", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/xmppmaster/includes/xmlrpc.php");
$oo = json_decode(xmlrpc_getListPresenceAgent(), true);
$listdespackage = xmlrpc_getListPackage();

//
$struct=array();
 foreach ($oo as $k => $v) {
    // $hostname = $oo[$k]['information']['info']['hostname'];
    $struct[$oo[$k]['deployment']][$k]['jid']=$oo[$k]['fromjid'];
    $struct[$oo[$k]['deployment']][$k]['hostname'] = $oo[$k]['information']['info']['hostname'];
    $struct[$oo[$k]['deployment']][$k]['agenttype'] = $oo[$k]['agenttype'];
    $struct[$oo[$k]['deployment']][$k]['ipconnection'] = $oo[$k]['ipconnection'];
    $struct[$oo[$k]['deployment']][$k]['plateform'] = $oo[$k]['information']['info']['plateform'];
    $struct[$oo[$k]['deployment']][$k]['os'] = $oo[$k]['information']['info']['os'];
    $struct[$oo[$k]['deployment']][$k]['processortype'] = $oo[$k]['information']['info']['hardtype'];
    $struct[$oo[$k]['deployment']][$k]['users'] = $oo[$k]['information']['users'];
    foreach ($oo[$k]['information']['listipinfo'] as $dede)
    {
        $struct[$oo[$k]['deployment']][$k]['macaddress'][] = $dede['macaddress'];
        $struct[$oo[$k]['deployment']][$k]['ipaddress'][] = $dede['ipaddress'];
    }
 }


  if (   isset($_POST['bvalid']) &&
        isset($_POST['package']) &&
        isset($_POST['Machine']) &&
        trim($_POST['Machine'])!= "" &&
        trim($_POST['package'])!= ""
        ){
        // searchip
        //
        $jid = searchjiddeploy($_POST['Machine'],$struct);
        if (count($jid)==2)
        {

        echo "deploy pckage ". $_POST['package']." on machine ".$jid[1]." from RS". $jid[0];
        echo "<br>";
        echo xmlrpc_runXmppDeployment( $jid[0], $jid[1], $_POST['package'], 40);
        }
 }else
 {
    $result="";
 }


 //list of machines
 foreach ( $struct as $chatroomdeploy => $differentmachine){
 // deployment chatroom $k
    foreach ( $differentmachine as $uniquehostname => $infomachine){
        if ($infomachine['agenttype']  == "machine"){
            // add the machine to the list
            // $infomachine['jid'] and $infomachine['hostname'] and $infomachine['192.168.56.2']
            $elt_values[] = $infomachine['jid'];
            $elt_afficher[] = $infomachine['hostname'];
            $elt_ip[] = $infomachine['ipconnection'];
        }
    }
 }

$f = new ValidatingForm();
        $f->push(new Table());
        $imss = new SelectItem("Machine");
        $imss->setElements($elt_afficher);
        $imss->setElementsVal($elt_values);

        $f->add(
            new TrFormElement(_T("Select a machine", "xmppmaster"), $imss)
        );

        $imss = new SelectItem("package");
        $imss->setElements($listdespackage);
        $imss->setElementsVal($listdespackage);

        $f->add(
            new TrFormElement(_T("Select a package", "xmppmaster"), $imss)
        );
        $f->pop();
        $f->addValidateButton("bvalid");
        $f->display();



?>
