<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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

$p = new PageGenerator(_T("Deployment logs for machine "." ".$hostname, 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();


?> 

<style>
.shadow
{
  -moz-box-shadow: 4px 4px 10px #888;  
  -webkit-box-shadow: 4px 4px 10px #888;  
  box-shadow:4px 4px 6px #888;
}
</style>


<?
  //recupere information deploie. for cmn_id
    $info = xmlrpc_getdeployfromcommandid($cmd_id, $uuid);
    if ($info['len'] == 0){
        echo _T("Wait for the deployment",'xmppmaster'). " "  . $cmd_id;
         //reload page
         echo'
            <script type="text/javascript">
            setTimeout(refresh, 10000);
            function  refresh(){
                jQuery( "#formpage" ).submit();
            }
        </script>
        ';
    }
    else{
        $sessionxmpp=$info['objectdeploy'][0]['sessionid'];
        $infodeploy = xmlrpc_getlinelogssession($sessionxmpp);
        $uuid=$info['objectdeploy'][0]['inventoryuuid'];
        $state=$info['objectdeploy'][0]['state'];
        $start=get_object_vars($info['objectdeploy'][0]['start'])['timestamp'];
        $result=$info['objectdeploy'][0]['result'];
        $resultatdeploy =json_decode($result, true);
        $host=$info['objectdeploy'][0]['host'];
        $jidmachine=$info['objectdeploy'][0]['jidmachine'];
        $jid_relay=$info['objectdeploy'][0]['jid_relay'];

        $datestart =  date("Y-m-d H:i:s", $start);
        echo "Start deployment : [".$infodeploy['len'] ." steps] " .$datestart;


       if (isset($resultatdeploy['descriptor']['info'])){
        echo "<br>";
        echo "<h2>Package</h2>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
                echo "<thead>";
                    echo "<tr>";
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Name</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Software</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Version</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Description</span>';
                        echo '</td>';
                    echo "</tr>";
                echo "</thead>";
                echo "<tbody>";
                    echo "<tr>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['description'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['name'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['software'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['version'];
                        echo "</td>";
                    echo "</tr>";
                echo "</tbody>";
            echo "</table>";
            echo '<br>';

      }
        echo "<br>";
        echo "<h2>Deployment phases</h2>";
        echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
            echo "<thead>";
                echo "<tr>";
                    echo '<td style="width: ;">';
                        echo '<span style=" padding-left: 32px;">START</span>';
                    echo '</td>';
                    echo '<td style="width: ;">';
                        echo '<span style=" padding-left: 32px;">STEP</span>';
                    echo '</td>';
                    echo '<td style="width: ;">';
                        echo '<span style=" padding-left: 32px;">DESCRIPTION</span>';
                    echo '</td>';
                echo "</tr>";
            echo "</thead>";
                echo "<tbody>";
        foreach($infodeploy['log'] as $line){
            //print_r($line);
            $startsteparray= get_object_vars( $line['date']);
            $datestartstep = date("Y-m-d H:i:s", $startsteparray['timestamp']);
            echo '<tr class="alternate">';
                echo "<td>";
                    echo $datestartstep;
                echo "</td>";
                echo "<td>";
                    echo $line['priority'];
                echo "</td>";
                echo "<td>";
                    echo $line['text'];
                echo "</td>";
            echo "</tr>";
        }
     echo "</tbody>";
    echo "</table>";

//echo "<pre>";
            //print_r($step);//$step['action'] $bodytag = str_replace("%body%", "black", "<body text='%body%'>");
            //echo "<pre>";

    if (isset($resultatdeploy['descriptor']['sequence'] )){
        echo "<br>";
        echo "<h2>Deployment result</h2>";
        foreach($resultatdeploy['descriptor']['sequence'] as $step){
            if($step['action'] == "action_pwd_packagecompleted"  )
                $actions = "Current directory is package directory";
            elseif ($step['action'] == "actionprocessscript"  )
                $actions = "Script Running in process";
            elseif ($step['action'] == "action_command_natif_shell"  )
                $actions = "Script Running in thread";
            elseif ($step['action'] == "actionerrorcompletedend"  )
                $actions =  "Deployment terminated on an error. Clean packages";
            elseif ($step['action'] == "actionsuccescompletedend"  )
                $actions = "Deployment terminated successfully. Clean package";
            elseif ($step['action'] == "actioncleaning"  )
                $actions = "Clean downloaded package";
            elseif ($step['action'] == "actionrestartbot"  )
                $actions = "Restart agent";
            else
                $actions = ltrim(str_replace("_"," ",substr($step['action'],6)));
            echo "<br>";
            if (isset($step['completed'])){
                echo '<h3 style="color:green;">STEP'." <strong>". $step['step'] . " [". $actions. "]</strong>" ."". "  </h3>";
            }
            else{
                echo '<h3 style="color:red;">STEP'." <strong>". $step['step'] . " [". $actions. "]</strong>" ."". '</h3>'; 
            }
            if (isset($step['completed'])){
                echo '<div class="shadow" 
                            style="  color:green;
                                       display: none;
                                        padding:0 10px;">';
                foreach($step as $keystep => $infostep){
                    if ($keystep != "step" and $keystep != "action" and  $keystep != "completed"){
                        if( strstr($keystep, "resultcommand")) {
                        echo "<pre>";
                            //echo nl2br($infostep);
                            echo $keystep." :".$infostep."<br>";
                        echo "</pre>";
                        }
                        else{
                            echo $keystep." :".$infostep."<br>";
                        }
                    }
                }
            }
            else{
                echo '<div class="shadow" style="  color:blue; display: none;
                                    font-size:10px;
                                    font-style: italic;
                                    padding:0 10px;">';
                foreach($step as $keystep => $infostep){
                    if ($keystep != "step" and $keystep != "action" and  $keystep != "completed")
                        echo $keystep." :".$infostep."<br>";
                    }
            }
                echo "</div>";
        }
    }
    else{
    //reload page
    echo'
            <script type="text/javascript">
            setTimeout(refresh, 10000);
            function  refresh(){
               // jQuery( "#formpage" ).submit();
            }
        </script>
        ';
    }
}
?>
<form id="formpage" action="<? echo $_SERVER['PHP_SELF']; ?>" METHODE="GET" >
    <input type="hidden" name="tab" value ="<? echo $tab; ?>" >
    <input type="hidden" name="module" value ="<? echo $module; ?>" >
    <input type="hidden" name="submod" value ="<? echo $submod; ?>" >
    <input type="hidden" name="action" value ="<? echo $action; ?>" >
    <input type="hidden" name="uuid" value ="<? echo $uuid; ?>" >
    <input type="hidden" name="hostname" value ="<? echo $hostname; ?>" >
    <input type="hidden" name="gid" value ="<? echo $gid; ?>" >
    <input type="hidden" name="cmd_id" value ="<? echo $cmd_id; ?>" >
    <input type="hidden" name="login" value ="<? echo $login; ?>" >
    <input type="hidden" name="mach" value ="1" >
</form>
<script type="text/javascript">
      jQuery( "h3" ).click(function() {
        jQuery(this).css('background-color','white')
        jQuery(this).next('div').toggle();
        });
</script>
<?
if ($gr_cmd_id){
    echo '
    <form id="formgroup" action="'.$_SERVER['PHP_SELF'].'" METHODE="GET" >
        <input type="hidden" name="tab" value ="'.$tab.'" >
        <input type="hidden" name="uuid" value ="'.$uuid.'" >
        <input type="hidden" name="gid" value ="'.$gid.'" >
        <input type="hidden" name="cmd_id" value ="'.$cmd_id.'" >
        <input type="hidden" name="login" value ="'.$login.'" >
        <input type="hidden" name="action" value ="viewlogs" >
        <input type="hidden" name="module" value ="xmppmaster" >
        <input type="hidden" name="submod" value ="xmppmaster" >
        <input type="submit" value ="group view" >
    </form>';
}



