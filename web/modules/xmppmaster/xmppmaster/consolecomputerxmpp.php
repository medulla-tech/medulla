<?php
/*
 * (c) 2016-2018 Siveo, http://www.siveo.net
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
 * file : consolecomputerxmpp.php
 */
?>
<style type='text/css'>
textarea {
    width:50% ;
    height:150px;
    margin:auto;   /* exemple pour centrer */
    display:block; /* pour effectivement centrer ! */
}
.shadow
{
  -moz-box-shadow: 4px 4px 10px #888;  
  -webkit-box-shadow: 4px 4px 10px #888;  
  box-shadow:4px 4px 6px #888;
}
 
 li.folder a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/folder.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.folderg a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/folder.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.console a {
        padding: 3px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/console.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.consoleg a {
        padding: 3px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/console.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.quick a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/quick.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.guaca a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/guaca.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.guacag a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/guaca.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.quickg a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/quick.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
</style>
<?
    require("modules/base/computers/localSidebar.php");
    require("graph/navbar.inc.php");
    require_once("modules/xmppmaster/includes/xmlrpc.php");

    require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
    require_once("modules/dyngroup/includes/utilities.php");
    include_once('modules/pulse2/includes/menu_actionaudit.php');
    $timeout = isset($_POST['timeout']) ? $_POST['timeout'] : 10 ; 
    $uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
    $machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
    $command = isset($_POST['command']) ? $_POST['command'] : "";
    $uiduniq = uniqid ("shellcommande");
    $resultcommand = "";
    $errorcode = "";
    $p = new PageGenerator(_T("Console", 'xmppmaster')." $machine");
    $p->setSideMenu($sidemenu);
    $p->display();

    echo "OS version :" . xmlrpc_getMachinefromjid($machine)['platform'];
    if (
        isset($_POST['command']) &&
        isset($_POST['Machine']) &&
        trim($_POST['Machine'])!= "" &&
        trim($_POST['command'])!= ""
        ){
            $_POST['result']='';
            $tabdata = array(
                                "command" => $command,
                                "machine" => $machine,
                                "uidunique" => $uiduniq
            );
            $re =  xmlrpc_remotecommandshell($command,$machine, intval($timeout));
            $ss = json_decode($re, true);
            if (isset($ss['err'])){
                if ( $ss['err'] == 'Timeout Error'){
                    $msg = sprintf(_T("Sorry, the remote machine [%s] takes too much time to answer.", "xmppmaster"), $machine);
                }else{
                    $msg = sprintf(_T("Error : %s", "xmppmaster"), $machine);
                }
                    new NotifyWidgetFailure($msg);
                #   exit;
                $resultcommand = $ss['err'];
                $errorcode = -1;
            }
            else{
                //$ss = json_decode($re, true);
                foreach(  $ss['result'] as $line){
                    $resultcommand = $resultcommand . $line;
                }
                $errorcode = $ss['code'];
                $recherche = true;
            }
        }
?>
<form>
    timeout (between 10s and 60s):
    <input type="number" id="timeout1" name="timeout1" value="<? echo $timeout; ?>" min="10" max="60">
</form>

<form method="post" id="Form">

    <table cellspacing="0">
    <input  type="hidden" id="machine" value="<? echo $machine; ?>" name="Machine"/>
    <input  type="hidden" id="timeout" value="<? echo $timeout; ?>" name="timeout"/>

        <tr>
            <td class="label" width="40%" style = "text-align: right;">Shell command</td>
            <td>
                <span id="container_input_command">
                    <input value="<? echo $command; ?>" 
                        name="command" 
                        style = "width : 400px;"
                        id="command" 
                        type="text" 
                        size="23"  
                        placeholder=""
                        data-regexp="/.+/" 
                        autocomplete="off" 
                        title="<? echo _T("Press return key to start your command", 'xmppmaster');  ?>"/>
                </span>
            </td>
        </tr>
        <?php
        if($resultcommand != ""){
            echo '
            <tr>
                <td class="label" width="40%" style = "text-align: right;"><br></td>
                <td>
                    <span>Command result : </span><span>'.$command.'</span>
                </td>
            </tr>';
        } 
            if ($errorcode != ""){
                echo'<tr>
                    <td class="label" width="40%" style = "text-align: right;">Error Code :</td>
                    <td>
                        <span id="codereturn">'.$errorcode.'</span>
                    </td>
                </tr>';
            }
        ?>
        
    </table>
    <?php 
        if ($resultcommand != ""){
            echo '<textarea rows="15"
                id="resultat" 
                spellcheck="false" 
                style = "height : 400px;
                        background : black;
                        color : white;
                        FONT-SIZE : 15px;
                        font-family : \'Courier New\', Courier, monospace;
                        border:10px solid ;
                        padding : 15px;
                        border-width:1px;
                        border-radius: 25px;
                        border-color:#FFFF00;
                        box-shadow: 6px 6px 0px #6E6E6E;" >'.
                        $resultcommand.
                        '</textarea>';
        }
    ?>
    <!-- si on veut un boutton submit-->
    <!--<button class="btn btn-small">submit</button>-->
</form>
<script type="text/javascript">
       jQuery( document ).ready(function() {
            jQuery( "#timeout1" ).change(function() {
                jQuery("#timeout").val(jQuery( "#timeout1" ).val())
            });
        });
</script>
