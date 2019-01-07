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
 *  file xmppfilesbrowsing.php
 */
?>
<?php
    echo '<link rel="stylesheet" href="jsframework/lib/pluginjqueryjtree/themes/default/style.min.css" />'."\n".
    '<script src="jsframework/lib/pluginjqueryjtree/jstree.min.js"></script>'."\n";
?>

<style type='text/css'>
textarea {
        width:50% ;
        height:150px;
        margin:auto;
        display:block;
}

body{
        font-family: Georgia;
        font-size: 11pt;
}

#global{
        width:100%;
        height:800px;
}

#gauche {
        width:35%;
        height:90%;
}

#droite {
        width: 64%;
        height:90%;
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

#fileshowremote {
        width: 50%;
        height:100%;
        overflow:auto;
}

#fileshowlocal {
        width: 100%;
        height:100%;
        overflow:auto;
}

#directoryremote{
        width: 50%;
        height:100%;
        overflow:auto;
        padding-botton:15px;
        float:left;
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


 ul.rightfile.li {
        background-color:#C0C0C0;
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
.Localdestination{
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background: url('modules/xmppmaster/graph/img/browserdownload.png');
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        opacity:1;
        Font-Weight : Bold ;
        font-size : 15px;
}
.Localdestination:hover {
        Font-Weight : Bold ;
        font-size : 15px;
}
.delete{
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/xmppmaster/graph/img/button_cancel.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        Font-Weight : Bold ;
        font-size : 15px;
}
.delete:hover{
        Font-Weight : Bold ;
        font-size : 15px;
}
.pop{
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/xmppmaster/graph/img/rewind.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        Font-Weight : Bold ;
        font-size : 15px;
}
.pop:hover{
        Font-Weight : Bold ;
        font-size : 15px;
}
.ombremultiple {
        /*width:100%;*/
        background-color:#ECECEC;
        padding:5px;
        box-shadow:2px 2px 2px gray,
        -1px -1px 2px white;
}
.ombretable1 {
        /*width:100%;*/
        background-color:#ECECEC;
        box-shadow:2px 2px 2px gray,
        -1px -1px 2px white;
}

.guaca a {
    padding: 0px 0px 5px 22px;
    margin: 0 0px 0 0px;
    background-image: url("modules/base/graph/computers/guaca.png");
    background-repeat: no-repeat;
    background-position: left top;
    line-height: 18px;
    text-decoration: none;
    color: #FFF;
}

.quick a {
    padding: 0px 0px 5px 22px;
    margin: 0 0px 0 0px;
    background-image: url("modules/base/graph/computers/quick.png");
    background-repeat: no-repeat;
    background-position: left top;
    line-height: 18px;
    text-decoration: none;
    color: #FFF;
}

.console a {
    padding: 3px 0px 5px 22px;
    margin: 0 0px 0 0px;
    background-image: url("modules/base/graph/computers/console.png");
    background-repeat: no-repeat;
    background-position: left top;
    line-height: 18px;
    text-decoration: none;
    color: #FFF;
}
</style>

<?
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
$machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
$ma = xmlrpc_getMachinefromjid($machine);

$tab = explode("/",$machine);
$p = new PageGenerator(_T("File manager", 'xmppmaster')." on ". $ma['hostname']);
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require_once("modules/dyngroup/includes/utilities.php");
include_once('modules/pulse2/includes/menu_actionaudit.php');
echo "<br><br><br>";

// creation repertoire namemachine si non existe.
// et recuperation pathcurent pour cette machine eg /var/lib/pulse2/transfertfiles
// /machine25pulse
$lifdirlocal = xmlrpc_localfilesystem("");
$filecurentdir = xmlrpc_create_local_dir_transfert($lifdirlocal['path_abs_current'], $ma['hostname']);
$curentdir = $filecurentdir['path_abs_current'];

echo '<script type="text/javascript">';

if (stristr($ma['platform'], "win")) {

    echo 'var seperator = "\\\\";';
    echo 'var os = "win";';
}
else{
    echo 'var seperator = "/";';
    if (stristr($ma['platform'], "darwin")){
        echo 'var os = "darwin";';
    }
    else{
        echo 'var os = "linux";';
    }
}
echo '</script>';
?>

<?php
    $lifdirstr = xmlrpc_remotefilesystem("@", $machine);
    $lifdirremote = json_decode($lifdirstr, true);
    if (isset($lifdirremote['err'])){
        if ( $lifdirremote['err'] == 'Timeout Error'){
            $msg = sprintf(_T("Sorry, the remote machine [%s] takes too long to answer.", "xmppmaster"), $machine);
        }else{
            $msg = sprintf(_T("Error : %s", "xmppmaster"), $machine);
        }
            echo '<h2 style="color : red;">';
            echo "$msg";
            echo "</h2>";
            exit;
    }
    $datatree = $lifdirremote['data']['strjsonhierarchy'];
    // cherche local directory

printf ('
<form>
    <input id ="path_abs_current_local" type="hidden" name="path_abs_current_local" value="%s">
    <input id ="parentdirlocal" type="hidden" name="parentdirlocal" value="%s">
</form>' ,$lifdirlocal['path_abs_current'],$lifdirlocal['parentdir']);
$rootfilesystem = $lifdirremote['data']['rootfilesystem'];

$rootfilesystempath = $rootfilesystem;
if ($rootfilesystem[1] == ":"){
    $rootfilesystempath =substr($lifdirremote['data']['rootfilesystem'],2);
}

printf ('
<form>
    <input id ="path_abs_current_remote" type="hidden" name="path_abs_current_remote" value="%s">
    <input id ="parentdirremote" type="hidden" name="parentdirremote" value="%s">
    <input id ="rootfilesystem" type="hidden" name="rootfilesystem" value="%s">
    <input id ="rootfilesystempath" type="hidden" name="rootfilesystempath" value="%s">
</form>' ,
            $lifdirremote['data']['path_abs_current'],
            $lifdirremote['data']['parentdir'],
            $lifdirremote['data']['rootfilesystem'],
            $rootfilesystempath);
?>

<div id="messageaction">
    <span></span>
</div>

<div id="global">
    <table>
        <caption style = " caption-side : top;
                           text-align : left;
                           Font-Weight : Bold ;
                           font-size : 17px;" ><?php echo sprintf(_T('Downloads basket', 'xmppmaster')); ?>
        </caption>

        <tr>
            <td style = "width:10%; font-size : 15px; Font-Weight : Bold ;"><?php echo sprintf(_T('Folders', 'xmppmaster')); ?>:</td>
            <td id="filedirectory" colspan="2" style = "font-size : 14px; Font-Weight : Bold ;"></td>
            <td style = "width:10%;">
            <span id="poplistdirectory" title="<?php echo sprintf(_T('Remove last folder', 'xmppmaster')); ?>" class="pop" ></span>
                <span id="deletelistdirectory" title="<?php echo sprintf(_T('Remove all folders', 'xmppmaster')); ?>" class="delete" ></span>
            </td>
        </tr>

        <tr>
            <td style = "width:10%;font-size : 15px; Font-Weight : Bold ;"><?php echo sprintf(_T('Files', 'xmppmaster')); ?>:</td>
            <td id="filelist" colspan="2" style = "font-size : 14px; Font-Weight : Bold ;"></td>
            <td style = "width:10%;">
            <span  id="poplistfile" title="<?php echo sprintf(_T('Remove last file', 'xmppmaster')); ?>"  class="pop" ></span>
                <span  id="deletelistfile" title="<?php echo sprintf(_T('Remove all files', 'xmppmaster')); ?>"  class="delete" ></span>
            </td>
        </tr>

        <tr>
            <td style = "text-align:left; width:10%;Font-Weight : Bold ;font-size : 15px;"><?php echo sprintf(_T('Downloads basket to', 'xmppmaster')); ?></td>
            <td id="dest_string" colspan="2" style = "text-align:left;font-size : 17px;Font-Weight : Bold ; ">dest :</td>
            <td style = "text-align:left; width:15px;">
                <span id="downloadlist" title="<?php echo sprintf(_T('Download list selection', 'xmppmaster')); ?>" class="Localdestination" ></span>
            </td>
        </tr>
    </table>
    <br>
    <div id="gauche">
        <table style = "width:100%;
                        height:100%;
                        padding:0px;
                        border-spacing: 5px 5px;
                        border-collapse :separate;"
                        class="ombremultiple">
            <tr style="height: 100%;">
                <td class = "ombremultiple" style="vertical-align : top; height:600px; Font-Weight : Bold;font-size : 15px;" >
                    <div id="fileshowlocal" class="fileshow" >
                        <?php  echo '<div style=" Font-Weight : Bold;
                                                  font-size : 15px;">'.
                                                  sprintf(_T('Local folder', 'xmppmaster')).'
                                                  : <span  style=" Font-Weight : Bold;
                                                                               Font-size : 15px;"
                        id=\'localcurrrent\'>'.$lifdirlocal['path_abs_current'] ."</span></div>";

                        echo '<ul id="leftdirdata" class="leftdir">';
                        echo '</ul>';
                        ?>
                    </div>
                </td>
            </tr>

            </table>
       <div class ="piedbrowser"><h2></h2></div>
    </div>

    <div id="droite">
        <table style = "width:100%;
                        height:100%;
                        padding:0px;
                        border-spacing: 5px 5px;
                        border-collapse :separate;"
                        class="ombremultiple">
            <tr>
                <td class="enplacementcss ombremultiple">
                    <span style="Font-Weight : Bold; font-size : 15px;"><?php echo sprintf(_T('Remote tree view', 'xmppmaster')); ?>: </span><br>
                    <span style="Font-Weight : Bold;
                    font-size : 15px;
                    text-align: right"><?php echo _T('root:', 'xmppmaster')." ".$rootfilesystempath; ?></span>
                </td>
                <td class="currentdircss ombremultiple" style="Font-Weight : Bold; font-size : 15px;">
                <?php echo sprintf(_T('Current path: ', 'xmppmaster')); ?>
                    <span id="cur" style="Font-Weight : Bold ;font-size : 15px;">
                            <? echo $lifdir['data']['path_abs_current']; ?>
                    </span>
                </td>
            </tr>

            <tr style="height: 100%;">
                <td style = " width:40%;vertical-align: top; height: 100%;"  class="ombremultiple" >
                    <div id ="directoryremote" style = " width:100%; height: 650px; overflow : auto;" ></div>
                </td>
                <td class="ombremultiple"  style = " width:60%; vertical-align: middle;"  >
                    <div id ="fileshowremote"
                        style = "padding-top:10px;
                                width:100%;
                                height: 600px;
                                overflow:auto;">
                    </div>
                </td>
            </tr>
        </table>
    </div>

    <div class ="piedbrowser">
        <form>
            <div>
            </div>
        </form>
    </div>
</div>


<div id="dialog-confirm-download-directory" title="Transfer Folder">
  <div>
    <span style="float:left; margin:12px 12px 20px 0;">
        <span id="dialogmsg">
        </span>
    </span>
  </div>
</div>

<div id="dialog-confirm-download-file" title="Transfer File">
  <div>
    <span style="float:left; margin:12px 12px 20px 0;">
        <span id="dialogmsg1">
        </span>
    </span>
  </div>
</div>

<!-- dialog box  Notify file-->
<div id="dialog-notification-download-file" >
  <div>
    <span style="float:left; padding:12px 12px 20px 0; background-color: #d9edf7; width: 95%; height:100%;">
        <span id="dialogmsg2">
        </span>
    </span>
  </div>
</div>

<script type="text/javascript">
    jQuery( document ).ready(function() {
        // variable list file select
        listfileusermachinejson = {"files" :[], "directory" : []};
        namemachine =  "<?php echo $ma['hostname']; ?>";
        login =  "<?php echo $_SESSION['login']; ?>";
        userkey =  login + "_" + namemachine;
        startlocal =  jQuery('input[name=path_abs_current_local]').val()+"/"+ namemachine;
        fileremote = false;
        filelocal  = false;
        taillefile = "";
        filenameremote = "";
        filenamelocal = "";
        timetmp ="";// le repertoire d'acceuil".
        user = "<?php echo $_SESSION['login']; ?>";
        jid = "<?php echo $ma['jid']; ?>";
        nameremotepath = "";
        absolutepath ="";
        init = 1;
        local(namemachine);
        remote("@");
        jQuery('#directoryremote')
            .on("changed.jstree", function (e, data) {
                if(data.selected.length) {
                    var pathlinux = data.instance.get_path(data.node, '/');
                    remote(pathlinux);
                }
            })
            .jstree({
                'core' : {
                    'multiple' : false,
                    'data' : [
                    <?php	echo $datatree; ?>
                    ]
                }
            })
            ;
            timetmp = user + "-" + datetimenow();
            jQuery('#dest_string').text(jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp + "/" );
            jQuery('#directoryremote').on('ready.jstree', function() {
                jQuery('#directoryremote').jstree("open_all");
            });
    });

    function del_list(type){
        // type "files" ou "directory"
        listfileusermachinejson[type].splice(0,listfileusermachinejson[type].length)
    }

    function pop_list(type){
        // type "files" ou "directory"
        listfileusermachinejson[type].pop()
    }

    function confirmation_information(data) {
        setTimeout(function() { affichedata(data); }, 2000);
    }

    function affichedata(data){
                jQuery("#dialogmsg2").html(data);
                jQuery( function() {
                    jQuery( "#dialog-notification-download-file" ).dialog({
                        resizable: false,
                        height: "auto",
                        width: 600,
                        modal: true,
                        buttons: [
                            {
                                id: "my-buttoncancel2",
                                text: "<?php echo sprintf(_T('Computer view', 'xmppmaster')); ?>",
                                'class':'btnPrimary',
                                style:"color:#FFFFFF;background-color: #000000;",
                                click:function() {
                                    jQuery( this ).dialog( "close" );
                                    window.location.href = "/mmc/main.php?module=base&submod=computers&action=index";
                                }
                            },
                            {
                                id: "my-buttonrefresh",
                                text: "<?php echo sprintf(_T('Refresh', 'xmppmaster')); ?>",
                                'class':'btnPrimary',
                                style:"color:#FFFFFF;background-color: #000000;",
                                click:function() {
                                    jQuery( this ).dialog( "close" );
                                    window.location.reload();
                                }
                            },
                            {
                                id: "my-buttonhistory",
                                text: "<?php echo sprintf(_T('History download', 'xmppmaster')); ?>",
                                'class':'btnPrimary',
                                style:"color:#FFFFFF;background-color: #000000;",
                                click:function() {
                                    jQuery( this ).dialog( "close" );
                                    window.location.href = "/mmc/main.php?module=base&submod=logview&action=logsdownload";
                                }
                            },
                            {
                                id: "my-buttonfilemanager",
                                text: "<?php echo sprintf(_T('File Manager', 'xmppmaster')); ?>",
                                'class':'btnPrimary',
                                style:"color:#FFFFFF;background-color: #000000;",
                                click:function() {
                                    jQuery( this ).dialog( "close" );
                                    window.location.href = "/mmc/main.php?module=xmppmaster&submod=xmppmaster&action=filesmanagers";
                                }
                            }
                        ]
                        });
                } );
    }

    function datetimenow(){
        var newdate = new Date();
        var moi      = "0" + (newdate.getMonth() +1 );
        var jour     = "0" + newdate.getDate();
        var heure    = "0" + (newdate.getHours());
        var minutes  = "0" + newdate.getMinutes();
        var secondes = "0" + newdate.getSeconds();
        var datetime = newdate.getFullYear() +
                                                "-" +
                                                moi.substr(-2) +
                                                "-" + jour.substr(-2) +
                                                "-" + heure.substr(-2) +
                                                ":" + minutes.substr(-2) +
                                                ":" + secondes.substr(-2);
        return datetime;
    }

    function local(selectdir){
        if (typeof selectdir == 'undefined'){
            var selectdir = "";
        }
        var path_abs_current_local = jQuery('input[name=path_abs_current_local]').val();
        if (typeof path_abs_current_local == 'undefined'){
            var path_abs_current_local = "";
        }
        var parentdirlocal = jQuery('input[name=parentdirlocal]').val();
        if (typeof parentdirlocal == 'undefined'){
            var parentdirlocal = "";
        }

        jQuery.get("modules/xmppmaster/xmppmaster/ajax_refresh_files_local.php",
                    {
                        "parentdirlocal" : parentdirlocal,
                        "path_abs_current_local" : path_abs_current_local,
                        "machine" : <?php echo '"'.$machine.'"'; ?>,
                        "os" : <?php echo '"'.$ma['platform'].'"'; ?>,
                        "selectdir" : selectdir
        } )
            .done(function( data ) {
                jQuery('input[name=path_abs_current_local]').val(data['path_abs_current']);
                timetmp = user + "-" + datetimenow();
                jQuery('#dest_string').text(jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp + "/" )
                jQuery('input[name=parentdirlocal]').val(data['parentdir']);
                jQuery("ul.leftdir").html(data['html']);
                jQuery('#localcurrrent').text(jQuery('input[name=path_abs_current_local]').val());
                jQuery("ul.leftdir > li").click(function() {
                    var dirsel = jQuery(this).text();
                    if (typeof dirsel == 'undefined'){
                        var dirsel = "";
                    }
                    //  recupere repertoire en local
                    local(dirsel);
                });
            })
    }

    function remote(selectdir){
        if (typeof selectdir == 'undefined'){
            var selectdir = "";
        }
        var path_abs_current_remote = jQuery('input[name=path_abs_current_remote]').val();
        if (typeof path_abs_current_remote == 'undefined'){
            var path_abs_current_remote = "";
        }
        var parentdirremote = jQuery('input[name=parentdirremote]').val();
        if (typeof parentdirremote == 'undefined'){
            var parentdirremote = "";
        }

       jQuery.get( "modules/xmppmaster/xmppmaster/ajax_refresh_files_remote.php",
                    {
                            "parentdirremote" : parentdirremote,
                            "path_abs_current_remote" : path_abs_current_remote,
                            "machine" : <?php echo '"'.$machine.'"'; ?>,
                            "os" : <?php echo '"'.$ma['platform'].'"'; ?>,
                            "selectdir" : selectdir
                     } ).done(function( data ) {
            jQuery( '#cur' ).text(data['path_abs_current']);
            jQuery('#fileshowremote').html(data['html']);
            jQuery('#path_abs_current_remote').val(data['path_abs_current']);
            jQuery('#parentdirremote').val(data['parentdir']);
            jQuery('#rootfilesystem').val(data['rootfilesystem']);
            jQuery("span.but").click(function() {
                if (jQuery(this).parent("li").find(':nth-child(1)').text() == "."){
                    var source = jQuery('input[name=path_abs_current_remote]').val();
                }
                else{

                    var source = jQuery('input[name=path_abs_current_remote]').val() + seperator + jQuery(this).parent("li").find(':nth-child(1)').text();
                }
                timetmp = user + "-" + datetimenow();
                jQuery( function() {
                        //addition objet au local storage
                        listfileusermachinejson['directory'].push(source)
                        var uniqueNames = [];
                        jQuery.each(listfileusermachinejson['directory'], function(i, el){
                            if(jQuery.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
                        });
                        listfileusermachinejson['directory'] = uniqueNames;
                        jQuery('#filedirectory').html(listfileusermachinejson['directory'].join(' ; '));
                });
            });
            jQuery(".download").click(function() {
                jQuery( function() {
                        listfileusermachinejson['files'].push(jQuery('input[name=path_abs_current_remote]').val() + seperator + filenameremote);
                        var uniqueNames = [];
                        jQuery.each(listfileusermachinejson['files'], function(i, el){
                            if(jQuery.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
                        });
                        listfileusermachinejson['files'] = uniqueNames;
                        jQuery('#filelist').html(listfileusermachinejson['files'].join(' ; '));
                } );
            });
            if (init == 1){
                jQuery(".rightfile LI").each(function(){
                    jQuery(this).css({'color': 'black', 'font-weight' : 'normal'});
                    jQuery(this).find(':nth-child(2)').hide();
                });
            }
            jQuery("ul.rightfile > li").click(function() {
                //  recupere file en remote
                fileremote = true;
                jQuery(".rightfile LI").each(function(){
                    jQuery(this).css({'color': 'black', 'font-weight' : 'normal','background-color' : '#C0C0C0',});
                    jQuery(this).find(':nth-child(2)').hide()
                });
                jQuery(this).css({ 'color' : 'blue', 'background-color' : 'lightblue', 'font-weight' : 'bold'});
                jQuery(this).find(':nth-child(2)').show()
                filenameremote = jQuery(this).find(':first').text();
                taillefile = jQuery(this).find(':last').text();
                filenamelocal = filenameremote ; // datetimenow() + "-" + filenameremote
                timetmp = user + "-" + datetimenow()
                nameremotepath = jQuery('input[name=path_abs_current_remote]').val() + seperator + filenameremote
                jQuery('#remotecurrrent').text(nameremotepath);
            });
        });
    }

    jQuery("#downloadlist").click(function() {
        var dir  = jQuery('#filedirectory').text().split(";")
        var file = jQuery('#filelist').text().split(";")
        msg = "<h1><?php echo sprintf(_T('Download from', 'xmppmaster')); ?>" + " " + namemachine + "</h1>"+
        "<p>"+
        "<?php echo sprintf(_T('Folders list', 'xmppmaster')); ?>" + " : " +
        "</p>";
        for (var i = 0; i < dir.length; i++) {
            msg = msg + "<p>" + dir[i] + "</p>";
        }
        msg = msg + "<br>";
        msg = msg + "<p>"+
        "<?php echo sprintf(_T('Files list', 'xmppmaster')); ?>" + " : " +
        "</p>";
        for (var i = 0; i < file.length; i++) {
            msg = msg + "<p>" + file[i] + "</p>";
        }
         msg = msg + "<br>";
        msg = msg + "<p>"+
        "<?php echo sprintf(_T('To local folder', 'xmppmaster')); ?>" + " : "+
        "</p>";
        msg = msg + "<br>";
        msg = msg + "<p>"+
        jQuery('#dest_string').text()+
        "</p>";
                jQuery("#dialogmsg").html(msg);

                jQuery( function() {
                    jQuery( "#dialog-confirm-download-directory" ).dialog({
                    resizable: false,
                    height: "auto",
                    width: 600,
                    modal: true,
                    buttons: [
                        {
                            id: "my-button",
                            text: "<?php echo sprintf(_T('Confirm', 'xmppmaster')); ?>",
                            'class':'btnPrimary',
                            style : "color:#FFFFFF; background-color: #000000;",
                            click:function() {
                            // call plugin de telechargement.
                            jQuery.get( "modules/xmppmaster/xmppmaster/ajaxxmppplugindownloadexpert.php",  {
                                        "dest"          : jQuery('#dest_string').text(),
                                        "directory"     : jQuery('#dest_string').text(),
                                        "listdirectory" : jQuery('#filedirectory').text(),
                                        "listfile"      : jQuery('#filelist').text(),
                                        "jidmachine"    : jid
                                        },function(data){
                                            jQuery('#dialog-notification-download-file').attr('title', '<?php echo sprintf(_T('The list (folder & files) copy has been requested successfully', 'xmppmaster')); ?>');
                                            confirmation_information(data);
                                        });
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
                });
    });

    jQuery("#deletelistdirectory").click(function() {
        jQuery('#filedirectory').html("");
        del_list("directory");
    });

    jQuery("#deletelistfile").click(function() {
        jQuery("#filelist").html("");
        del_list("files");
    });

    jQuery("#poplistdirectory").click(function() {
         pop_list("directory");
         jQuery('#filedirectory').html(listfileusermachinejson['directory'].join(' ; '));
    });

    jQuery("#poplistfile").click(function() {
        pop_list("files");
        jQuery('#filelist').html(listfileusermachinejson['files'].join(' ; '));
    });
    </script>
