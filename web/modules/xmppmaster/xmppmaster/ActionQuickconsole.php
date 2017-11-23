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



$uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
$machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
$cmdsend  = isset($_GET['customcmd']) ? $_GET['customcmd'] : $_POST['customcmd'];
$namecmd  = isset($_GET['namecmd']) ? $_GET['namecmd'] : $_POST['namecmd'];
$os  = isset($_GET['os']) ? $_GET['os'] : $_POST['os'];
$user  = isset($_GET['user']) ? $_GET['user'] : $_POST['user'];
$description  = isset($_GET['$description']) ? $_GET['$description'] : $_POST['$description'];
    $tab = explode("/", $machine);

    $p = new PageGenerator(_T("Send custom command to", 'xmppmaster')." $tab[1]");
    $p->setSideMenu($sidemenu);
    $p->display();

    if ($_GET['presencemachinexmpp']){

    }
    $qacomand =array();
    $mm = array();
    $os_up_case = strtoupper ($_GET['os']);
    if ($_GET['presencemachinexmpp']){
        if (strpos ($os_up_case, "WINDOW") !== false){
            $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "windows" );
        }
        else{
            if (strpos ($os_up_case, "LINUX") !== false){
                $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "linux" );
            }
            else{
                if (strpos ($os_up_case, "MACOS") !== false){
                    $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "macos" );
                }
            }
        }
    }

    echo "<div style = 'text-align: center;'>
    <hr>";
    echo'<br><br>
            <select id="select">';
            foreach($qacomand['command'] as $tabblecommand){
                if ($namecmd == $tabblecommand['namecmd']){
                    echo '<option value="'.$cmdsend.'" selected>'.$tabblecommand['namecmd'].'</option>';
                }
                else{
                    echo '<option value="'.$tabblecommand['customcmd'].'">'.$tabblecommand['namecmd'].'</option>';
                }

                $mm[] =  "'".$tabblecommand['namecmd']."': {
                    'description' : '".addslashes( $tabblecommand['description'] )."',
                    'customcmd' : '".$tabblecommand['customcmd']."',
                    'os' : '".$tabblecommand['os']."',
                    'user' : '".$tabblecommand['user']."'}";
                };
            echo'</select>
        ';
    echo "</div>";

echo'
<form method="post" id="Form">
        <input  type="hidden" value="'.$machine.'" name="Machine"/>
        <input  type="hidden" value="'.$uuid.'" name="objectUUID"/>
        <input  type="hidden" value="'.$cmdsend.'" name="customcmd"/>
        <input  type="hidden" value="'.$namecmd.'" name="namecmd"/>
        <input  type="hidden" value="'.$os.'" name="os"/>
        <input  type="hidden" value="'.$user.'" name="user"/>
        <input  type="hidden" value="'.$description.'" name="description"/>
        <input  id="command1" type="hidden" value="'.$cmdsend.'" name="command"/>

    <div width="70%" style = "text-align: center;">
        <input type="submit" name="bvalid" value="Confirm" class="btnPrimary"  />
    </div>
    <hr>
    <div width="70%" style = "text-align: center;">
       <span>Command result :</span><span id="cmdsendshow">'.$cmdsend.'</span>
    <textarea name="result" id="result" rows="6" cols="190"  />'.$result['data']['result'].'</textarea>
<br>
<span>Return code : '.$result['ret'].'</span></div>
</form>
';

?>
<script type="text/javascript">
    <?
     if ($_GET['presencemachinexmpp']){
        echo 'var myObject = {';
            echo implode(",", $mm);
            echo '};';
        echo"
        jQuery(function() {
            var t = jQuery('#select option:selected').text();
            jQuery('#namecmd').val(t);
            jQuery('#customcmd').val(myObject[t].customcmd);
            jQuery('#description').val(myObject[t].description);
            jQuery('#os').val(myObject[t].os);
            jQuery('#user').val(myObject[t].user);
            jQuery('#command').text(myObject[t].customcmd);
            jQuery('#command1').val(myObject[t].customcmd);
            jQuery('#cmdsendshow').text(myObject[t].customcmd);
        });

        jQuery( '#buttoncmd' ).click(function() {
            jQuery( '#formcmdcustom' ).submit();
        });

        jQuery('#select').on('change', function() {
            var t = jQuery('#select option:selected').text();
            jQuery('#namecmd').val(t);
            jQuery('#customcmd').val(myObject[t].customcmd);
            jQuery('#description').val(myObject[t].description);
            jQuery('#os').val(myObject[t].os);
            jQuery('#user').val(myObject[t].user);
            jQuery('#command').text(myObject[t].customcmd);
            jQuery('#command1').val(myObject[t].customcmd);
            jQuery('#cmdsendshow').text(myObject[t].customcmd);
        });
    ";
    }
    ?>
</script>
