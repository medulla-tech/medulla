<?php
/*
 *  (c) 2016 siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net.
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

// require("modules/xmppmaster/xmppmaster/localSidebar.php");
// require("graph/navbar.inc.php");
//require_once('modules/xmppmaster/includes/xmlrpc.inc.php');

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
require("graph/navbar.inc.php");
//require("localSidebar.php");

$p = new PageGenerator(_T("Console", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/xmppmaster/includes/xmlrpc.php");

/*
echo "<pre>";
//print_r(xmlrpc_getListPresenceMachine());
print_r($_GET );
print_r($_POST );
echo "</pre>";*/


 if (   isset($_POST['bvalid']) &&
        isset($_POST['command']) && 
        isset($_POST['Machine'])&&
        trim($_POST['Machine'])!= "" &&
        trim($_POST['command'])!= ""
        ){
        $_POST['result']='';
        $result = xmlrpc_xmppcommand(trim($_POST['command']),trim($_POST['Machine']));
 }else
 {
    $result="";
 }
//  echo "<pre>";
// print_r($result);
// echo "</pre>";
 
        $f = new ValidatingForm();
        $f->push(new Table());
        $imss = xmlrpc_getListPresenceMachine();
        $elt = array();
        $elt_values = array();
        foreach (range(0, count($imss)-1) as $i) {
           $elt_values[$i] =$imss[$i]['jid'];
          $elt[$i]  =$imss[$i]['type']." : ".$imss[$i]['hostname'];
        }
 
        $imss = new SelectItem("Machine");
        $imss->setElements($elt);
        $imss->setElementsVal($elt_values);

        $f->add(
            new TrFormElement(_T("Select an machine", "xmppmaster"), $imss)
        );

        $e=new InputTpl('command');
        $f->add(
            new TrFormElement(_T("commande shell", "xmppmaster"), $e)
        );
        if ( isset($_POST['result'])){
            $f->add(
                        new TrFormElement("<br>",  new SpanElement(_T("Resul command", "xmppmaster")." : ". trim($_POST['command'])))
                    );
        }

        $f->pop();
        if ( isset($_POST['result'])){
            $ear = new TextareaTpl('result');
            $ear->setCols(190);
            if (array_key_exists('result', $result['data'])) {
                $f->add(
                    new TrFormElement
                    (
                        "",
                        $ear
                    ),
                    array("value" => htmlspecialchars($result['data']['result']))
                );
            }
            else{
                $f->add(
                        new TrFormElement
                        (
                            "",
                            $ear
                        ),
                        array("value" => htmlspecialchars($result['data']['msg']))
                    );
            }
        }
        
        $f->push(new Table());
        if ($result['ret'] != 0){
            $result['ret']=' <font color="red">'.$result['ret'].'</font>';
        }
        
        $f->add(
                    new TrFormElement("",  new SpanElement(_T("Code Return : ", "xmppmaster").$result['ret']))
                );
                $f->addValidateButton("bvalid");
        $f->pop();
        $f->display();
?>
