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
textarea {
    width:50% ;
    height:150px;
    margin:auto;   /* exemple pour centrer */
    display:block; /* pour effectivement centrer ! */
}
</style>


<?
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
$uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
$machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );

$tab = explode("/",$machine);

$p = new PageGenerator(_T("Console", 'xmppmaster')." $tab[1]");
$p->setSideMenu($sidemenu);
$p->display();


 if (   isset($_POST['bvalid']) &&
        isset($_POST['command']) &&
        isset($_POST['Machine']) &&
        trim($_POST['Machine'])!= "" &&
        trim($_POST['command'])!= ""
        ){
        $_POST['result']='';
        $result = xmlrpc_runXmppCommand(trim($_POST['command']),trim($_POST['Machine']));
 }else
 {
    $result="";
 }
 
if ( $uuid != ""){
  
        $f = new ValidatingForm();
        $f->push(new Table());

        $f->add(new HiddenTpl('Machine'), array("value" => $machine, "hide" => True));

        $e=new InputTpl('command');
        $f->add(
            new TrFormElement(_T("Shell command", "xmppmaster"), $e)
        );
        if ( isset($_POST['result'])){
            $f->add(
                        new TrFormElement("<br>",  new SpanElement(_T("Command result", "xmppmaster")." : ". trim($_POST['command'])))
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
    }
?>
