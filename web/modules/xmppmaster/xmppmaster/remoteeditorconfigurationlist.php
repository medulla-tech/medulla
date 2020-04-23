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
 *  file xmppmaster/remoteeditorconfiguration.php
 */
?>
<style type='text/css'>
textarea {
    width:90% ;
    height:150px;
    margin:auto;
    display:block;
}

body{
    font-family: Georgia;
    font-size: 11pt;
}

/*h2{
    text-align: center;
}*/

#global{
  width:100%;
  height:700px;
}
#droite, #gauche {
    display: inline-block;
    vertical-align: top;
    border-width:1px;
    border-style:dotted;
    border-color:black;
}

.download{
    /*display : none;*/
    /*background: url('modules/xmppmaster/graph/img/browserdownload.png') no-repeat;*/
    cursor:pointer;
    border: none;
}

.fileshow {
    overflow:auto;
    height:85%;
}

#gauche {
    width:49%;
    height:90%;
}

#droite {
    width: 49%;
    height:90%;
}

.titlebrowser{
    vertical-align:middle;
    height:5%;
    text-align: center;
    padding-top:5px;
}

.currentdir{
    vertical-align:middle;
    height:5%;
    text-align: left;
    padding-top:5px;
    padding-left:45px;
}

.piedbrowser{
    vertical-align:bottom;
    height:5%;
    text-align: center;
    padding-top:5px;
    color: blue;
}

ul.leftdir, ul.rightdir {
    list-style-image: url('modules/xmppmaster/graph/img/closedir.png');
    padding-right:25px;
    cursor: pointer;
}
ul.leftfile, ul.rightfile {
    list-style-image: url('modules/xmppmaster/graph/img/file1.png');
    padding-right:25px;
    cursor: pointer;
}
.fileselect{
    margin-left  : 250px;
    margin-right : 250px;
}

.marge {
    margin-bottom:20px;
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


if(isset($_GET['jid']))
{
  $ma['hostname'] = (isset($_GET['hostname'])) ? $_GET['hostname'] : '';
  $ma['jid'] = (isset($_GET['jid'])) ? $_GET['jid'] : '';
  $machine = $ma['hostname'];
}

else{
  $uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
  $machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
  $ma = xmlrpc_getMachinefromjid($machine);
}
$tab = explode("/",$machine);
$p = new PageGenerator(_T("Edit config file", 'xmppmaster')." on ". $ma['hostname']);
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require_once("modules/dyngroup/includes/utilities.php");
include_once('modules/pulse2/includes/menu_actionaudit.php');

    $result = xmlrpc_remotefileeditaction($ma['jid'], array('action' => 'listconfigfile'));
    if ($result['numerror'] != 0){
        echo "fin de script php sur error boite de dialog todo";
    }
    //print_r($result['result']);
?>

<form method="post" id="Form">
    <table cellspacing="0">
        <tr>
            <td class="label" width="40%" style = "text-align: right;">
                Select a config file
            </td>
            <td>
                <select name="namefileconf" id="namefileconf">
                    <?php
                        foreach($result['result']  as $dd){
                            if ($dd == $_GET['name']){
                                printf ('<option value="%s" selected>%s</option>', $dd, $dd );
                            }
                            else{
                                printf ('<option value="%s" >%s</option>', $dd, $dd );
                            }
                        }
                    ?>
                </select>
            </td>
        </tr>
        </table>
    <textarea rows="15"
              id="resultat"
              spellcheck="false"
              style = "height : 460px;
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
    <br>
    <button style="color:#FFFFFF;background-color: #000000;" id="savefile" class="btn btn-small">save file</button>
</form>
        <!-- dialog box Transfert directory -->
        <div id="dialog-confirm-save-conf" title="Confirm Saving Configuration">
            <div>
                <span style="float:left; margin:12px 12px 20px 0;">
                    <span id="dialogmsg">
                    </span>
                </span>
            </div>
        </div>

<script type="text/javascript">
    function save(){
        jQuery.post( "modules/xmppmaster/xmppmaster/ajaxxmppremoteaction.php",
                    {
                        "file" : jQuery('#namefileconf option:selected').text(),
                        "action" : 'save',
                        "machine" : "<? echo $ma['jid']; ?>",
                        'content' : jQuery('#resultat').val()
                    },
                    function(data) {
                        //jQuery('#resultat').val(data['result']);
                        var action = "<?php
                        if(isset($_GET['agenttype'])){
                          if($_GET['agenttype'] == 'relayserver')
                            echo 'xmppRelaysList';
                          else
                            echo 'xmppMachinesList';
                        }
                        else{
                          echo 'index';
                        }
                        ?>";

                        document.location.href="main.php?module=base&submod=computers&action="+action;
                    });
    }
    function loadconffile(param){
        //valeurselect = jQuery('#namefileconf option:selected').text()
        jQuery.post( "modules/xmppmaster/xmppmaster/ajaxxmppremoteaction.php",
            {
                "file" : param,
                "action" : 'loadfile',
                "machine" : "<? echo $ma['jid']; ?>"
            },
            function(data) {
                jQuery('#resultat').text(data['result']);
            });
    }

    jQuery( '#namefileconf').change(function() {
        loadconffile(jQuery('#namefileconf option:selected').text());
    });

    jQuery( "#savefile" ).click(function(event) {
        event.preventDefault();
        msg="<p><b>" +
                "<?php echo _T("Save Configuration", 'xmppmaster')."</p></b><p style=' margin-left: 30px;' >"._T("File :", 'xmppmaster'); ?>"+
            "</p>"+
            "<p style=' margin-left: 60px;' >" + jQuery('#namefileconf').val() + "</p>"
        jQuery("#dialogmsg").html(msg);

        jQuery( function() {
            jQuery( "#dialog-confirm-save-conf" ).dialog({
            resizable: false,
            height: "auto",
            width: 600,
            modal: true,
            buttons: [
                {
                    id: "my-button",
                    text: "Confirm",
                    'class':'btnPrimary',
                    style:"color:#FFFFFF;background-color: #000000;",
                    click:function() {
                        save();
                        jQuery( this ).dialog( "close" );
                    }
                },
                {
                    id: "my-buttoncancel",
                    text: "Cancel",
                    'class':'btnPrimary',
                    style:"color:#FFFFFF;background-color: #000000;",
                    click:function() {
                        jQuery( this ).dialog( "close" );
                    }
                }
            ]
            });
        } );
    });

    jQuery( document ).ready(function() {
        var file = "<?php echo $_GET['name'];?>"

        if(typeof(file) == "undefined"){
          jQuery("#namefileconf").prop("selectedIndex", 0).attr("selected", "selected");
          console.log(jQuery("#namefileconf").prop("selectedIndex", 0))
        }
        else{
          jQuery("#namefileconf option:contains('"+file+"')").attr("selected", "selected")
        }

        var md5 = "";
        var modification = false;
        loadconffile(jQuery('#namefileconf option:selected').text());
    });

</script>
