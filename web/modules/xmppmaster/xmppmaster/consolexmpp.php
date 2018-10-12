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
 * file : xmppmaster/consolexmpp.php
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
    $machine  = isset($_POST['Machine']) ? $_POST['Machine'] : "";
    $command = isset($_POST['command']) ? $_POST['command'] : "";
    $tab = explode("/",$machine);
    $uiduniq = uniqid ("shellcommande");
    $recherche = false;

    if ($machine == "")
        $p = new PageGenerator(_T("Console Agent Relay Server", 'xmppmaster'));
    else
        $p = new PageGenerator(_T("Console", 'xmppmaster')." $machine");
    $p->setSideMenu($sidemenu);
    $p->display();


    $imss = xmlrpc_getListPresenceRelay();
    $elt = array();
    $elt_values = array();
    $resultrelay = array();
    foreach (range(0, count($imss)-1) as $i) {
        $elt_values[$i] = $imss[$i]['jid'];
        $elt[$i]  = $imss[$i]['type']." : ".$imss[$i]['hostname'];
        $resultrelay[] = array( 'name' =>  $elt[$i],
                                'jid' => $elt_values[$i]);
    }

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
            xmlrpc_runXmppCommand("plugin_asynchromeremoteshell", $machine, array($tabdata));
            $recherche = true;
        }

?>

<form method="post" id="Form">
    <table cellspacing="0">
    <input  type="hidden" id="machine" value="<? echo $machine; ?>" name="Machine"/>


        <tr>
            <td class="label" width="40%" style = "text-align: right;">
                Select a machine
            </td>
            <td>
                <select name="Machine" id="Machine">
                    <?php
                        foreach($resultrelay  as $dd){
                            printf ('<option value="%s" >%s</option>', $dd['jid'], $dd['name'] );
                        }
                    ?>
                </select>
            </td>
        </tr>

        <tr>
            <td class="label" width="40%" style = "text-align: right;">Shell command</td>
            <td>
                <span id="container_input_command">
                    <input value="<? echo $command; ?>"
                        title="<? echo _T("return key to start your order", 'xmppmaster'); ?>"
                        name="command"
                        id="command"
                        type="text"
                        size="23"
                        placeholder=""
                        data-regexp="/.+/"
                        autocomplete="off" />
                </span>
            </td>
        </tr>

        <tr>
            <td class="label" width="40%" style = "text-align: right;"><br></td>
            <td><img id="imagewait" src="graph/ajax_loading.gif" alt="" /><span>Command result : </span><span><? echo $command; ?></span></td>
        </tr>

        <tr>
            <td class="label" width="40%" style = "text-align: right;">Error Code :</td>
            <td><span id="codereturn"></span></td>
        </tr>



    </table>
    <textarea rows="15"
              id="resultat"
              spellcheck="false"
              style = "height : 400px;
                       background : black;
                       color : white;
                       FONT-SIZE : 15px;
                       font-family : 'Courier New', Courier, monospace;
                       border:10px solid ;
                       padding : 15px;
                       border-width:1px;
                       border-radius: 25px;
                       border-color:#FFFF00;
                       box-shadow: 6px 6px 0px #6E6E6E;"
    ></textarea>


    <!--<button class="btn btn-small">submit</button>-->
</form>


<script type="text/javascript">
    jQuery( document ).ready(function() {

    jQuery( "#imagewait" ).hide();
    calldata = function() {
        jQuery.get( "modules/xmppmaster/xmppmaster/xmppremotecmdshell.php",{
                        "command" : jQuery( "#command" ).val(),
                        "machine" : jQuery( "#machine" ).val(),
                        "uidunique" : "<? echo $uiduniq; ?>"
                    },
                    function( data ) {
                        if(data['stop'] == true){
                            jQuery( "#resultat" ).text( data['result'] );
                            jQuery( "#codereturn" ).text( data['codereturn'] );
                            jQuery( "#imagewait" ).hide();
                        }else
                        {
                            setTimeout(calldata, 5000)
                        }
                    });
}
<?php
    if ($recherche == true){
        echo "var uniqid = \"".$uiduniq."\";";
        echo "var recherche = true;";
        echo "var x = setTimeout(calldata, 2000);";
        echo 'jQuery( "#imagewait" ).show();';
    }
?>
    });
</script>
