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
 *  file xmppfilesbrowsingne.php
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
    margin-left  : 25px;
}

.fileshow {
    overflow:auto;
    height:85%;
}
#gauche {
    width:49%;
    height:45%;
}

#droite {
    width: 90%;
    height:90%;
}

#fileshowremote {
    width: 50%;
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
.download{
    /*display : none*/;
    /*background: url('modules/xmppmaster/graph/img/browserdownload.png') no-repeat;*/
    cursor:pointer;
    border: none;
}
ul.leftdir, ul.rightdir {
    list-style-image: url('modules/xmppmaster/graph/img/closedir.png');
    cursor: pointer;
    padding-right:25px;
}
ul.leftfile, ul.rightfile {
    list-style-image: url('modules/xmppmaster/graph/img/file1.png');
    cursor: pointer;
    padding-right:25px;
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

    if(isexpertmode())
    {
      $url = "xmppmaster/xmppmaster/xmppfilesbrowsing";
      $get = [];
      foreach($_GET as $key=>$value)
      {
        if(!in_array($key, ["module","submod", "action"]))
          $get[$key] = $value;
      }
      header("Location: " . urlStrRedirect($url, $get));
    }

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
// et recuperation pathcurent pour cette machine
// eg /var/lib/pulse2/transfertfiles/machine25pulse
$filecurentdir = xmlrpc_create_local_dir_transfert(xmlrpc_localfilesystem("")['path_abs_current'], $ma['hostname']);

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
    $lifdirstr = xmlrpc_remotefilesystem("@0@", $machine);
    $lifdir = json_decode($lifdirstr, true);


    $rootfilesystem = $lifdir['data']['rootfilesystem'];

    $rootfilesystempath = $rootfilesystem;

    if ($rootfilesystem[1] == ":"){
        $rootfilesystempath =substr($lifdir['data']['rootfilesystem'],2);
    }
    if (isset($lifdir['err'])){
        if ( $lifdir['err'] == 'Timeout Error'){
            $msg = sprintf(_T("Sorry, the remote machine [%s] takes too much time to answer.", "xmppmaster"), $machine);
        }else{
            $msg = sprintf(_T("Error : %s", "xmppmaster"), $machine);
        }
            echo '<h2 style="color : red;">';
            echo "$msg";
            echo "</h2>";
            exit;
    }
    $searchchar = array(':', '/', );
    $replacechar   = array( '", "children" : [', '{"text" : "');
    $datatree = str_replace ( $searchchar, $replacechar, $lifdir['data']['strjsonhierarchy'] );
    unset ($lifdir['data']['strjsonhierarchy']);
    //$datatree = $lifdir['data']['strjsonhierarchy'];
?>

<div id="messageaction">

</div>
<br>
<div id="global">

    <?php
    printf ('
    <form>
        <input id ="path_abs_current_local" type="hidden" name="path_abs_current_local" value="%s">
        <input id ="parentdirlocal" type="hidden" name="parentdirlocal" value="%s">
    </form>' ,$curentdir, $filecurentdir['parentdir']);
    ?>
       <div class ="piedbrowser"><h2></h2></div>

    <div id="droite">
         <div id ="directoryremote" class="fileshow"></div>
        <div id ="fileshowremote" class="fileshow"></div>
    </div>
    <div class ="piedbrowser">
        <form>
            <div>
               <!-- <input class="btnPrimary" id ="download" type="button" name="Dowload" value="<< Download <<">-->
            </div>
        </form>
    </div>
</div>

<div id="dialog-confirm-download-directory" title="Transfer Folder">

<!-- dialog box Transfert directory -->
  <div>
    <span style="float:left; margin:12px 12px 20px 0;">
        <span id="dialogmsg">
        </span>
    </span>
  </div>
</div>

<div id="dialog-confirm-download-file" title="Transfer File"><!-- dialog box Transfert File -->
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
    // diff between hour server/client
    var ladate = new Date();
    diff_hour = <?php echo date("H"); ?> - parseInt(ladate.getHours());
</script>

<script type="text/javascript">
    jQuery( document ).ready(function() {
        fileremote = false;
        filelocal  = false;
        filenameremote = "";
        filenamelocal = "";
        timetmp = "";
        taillefile ="";
        rootfilesystem     = ""; // "<?php echo str_replace ('\\' ,'\\\\',$rootfilesystem); ?>";
        rootfilesystempath = ""; //"<?php echo str_replace ('\\' ,'\\\\',$rootfilesystempath); ?>";
        jid = "<?php echo $ma['jid']; ?>";
        user = "<?php echo $_SESSION['login']; ?>";
        nameremotepath = "";
        absolutepath ="";
        init = 1;
        local();
        remote("@1@");
	jQuery('#directoryremote')
		.on("changed.jstree", function (e, data) {
			if(data.selected.length) {
                var pathlinux = data.instance.get_path(data.node,'/');
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
		});
	jQuery('#directoryremote').on('ready.jstree', function() {
                jQuery('#directoryremote').jstree("close_all");
        });
    });

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
                                text: "ok",
                                'class':'btnPrimary',
                                style:"color:#FFFFFF;background-color: #000000;",
                                click:function() {
                                    jQuery( this ).dialog( "close" );
                                    window.location.href = "/mmc/main.php?module=base&submod=computers&action=index";
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
        var heure    = "0" + (newdate.getHours() + diff_hour);
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

        jQuery( "#fileshowlocal" ).load(
                        "modules/xmppmaster/xmppmaster/ajaxxmpprefreshfileslocalne.php",
                        {
                            "parentdirlocal" : parentdirlocal,
                            "path_abs_current_local" : path_abs_current_local,
                            "machine" : <?php echo '"'.$machine.'"'; ?>,
                            "os" : <?php echo '"'.$ma['platform'].'"'; ?>,
                            "selectdir" : selectdir
                        },
                        function() {
        });
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

        console.log('call remote content :  ' +
                    "\nparentdirremote :" + parentdirremote+
                    "\npath_abs_current_remote : " + path_abs_current_remote+
                    "\nselectdir :" + selectdir);
        jQuery( "#fileshowremote" ).load(
                        "modules/xmppmaster/xmppmaster/ajaxxmpprefreshfilesremotene.php",
                        {
                            "parentdirremote" : parentdirremote,
                            "path_abs_current_remote" : path_abs_current_remote,
                            "machine" : <?php echo '"'.$machine.'"'; ?>,
                            "os" : <?php echo '"'.$ma['platform'].'"'; ?>,
                            "selectdir" : selectdir
                        },
                        function() {
            // REMOTE
            jQuery("ul.rightdir > li").find(':nth-child(1)').click(function() {
                fileremote = false;
                filenameremote = "";
                var dirsel = jQuery(this).text();
                if (typeof dirsel == 'undefined'){
                    var dirsel = "";
                }
                //remote(dirsel);
                jQuery('#dirremote').text(jQuery(this).text());
            });

        jQuery("span.but").click(function() {
                if (jQuery(this).parent("li").find(':nth-child(1)').text() == "."){
                    var source = jQuery('input[name=path_abs_current_remote]').val();
                }
                else{
                    var source = jQuery('input[name=path_abs_current_remote]').val() + seperator + jQuery(this).parent("li").find(':nth-child(1)').text();
                }
                timetmp = user + "-" + datetimenow();

                msg="<p><b>" +
                        "<?php echo _T("Copy remote folder", 'xmppmaster'); ?>"+
                    "</p>"+
                    "<p style=' margin-left: 60px;' >" + source + "</p>"+
                    "<p>"+
                    "<?php echo _T("to local folder", 'xmppmaster'); ?>" +
                    "</p>"+
                    "<p style=' margin-left: 60px;'>"+
                        jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp +"/"+
                    "</p>"
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
                            text: "Confirm",
                            'class':'btnPrimary',
                            style:"color:#FFFFFF;background-color: #000000;",
                            click:function() {
                                jQuery.get( "modules/xmppmaster/xmppmaster/ajaxxmppplugindownload.php",  {
                                    dest : jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp+"/",
                                    src  : source,
                                    directory : jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp,
                                    "jidmachine" : jid }, function( data ) {
                                        //appel boit de dialog action bien prise en compte
                                        jQuery('#dialog-notification-download-file').attr('title', '<?php echo _T("The folder copy has been requested successfully", "xmppmaster"); ?>');
                                        confirmation_information(data);
                                        //jQuery("#messageaction").html(data); //action message afficher en haut de page
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
                } );
            });

            jQuery(".download").click(function() {
                msg="<p>" +
                    "<?php echo _T("Copy remote file", 'xmppmaster'); ?>"+
                        "</p>"+
                        "<p style=' margin-left: 60px;' >" +
                            jQuery('input[name=path_abs_current_remote]').val() + seperator + filenameremote +
                        "</p>"+
                        "<p>"+
                        "<?php echo _T("to local File", 'xmppmaster'); ?>" +
                        "</p>"+
                        "<p style=' margin-left: 60px;'>"+
                            jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp + "/" + filenamelocal+
                        "</p>"
                jQuery("#dialogmsg1").html(msg);
                jQuery( function() {
                    jQuery( "#dialog-confirm-download-file" ).dialog({
                        resizable: false,
                        height: "auto",
                        width: 600,
                        modal: true,
                        buttons: [
                            {
                                id: "my-button1",
                                text: "Confirm",
                                'class':'btnPrimary',
                                style:"color:#FFFFFF;background-color: #000000;",
                                click:function() {
                                    jQuery.get( "modules/xmppmaster/xmppmaster/ajaxxmppplugindownload.php",  {
                                            dest : jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp + "/" + filenamelocal,
                                            src : jQuery('input[name=path_abs_current_remote]').val() + seperator +  filenameremote,
                                            directory : jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp,
                                            "jidmachine" : jid }, function( data ) {
                                                jQuery('#dialog-notification-download-file').attr('title', '<?php echo _T("The file copy has been requested successfully", "xmppmaster"); ?>');
                                                confirmation_information(data);
                                                //jQuery("#messageaction").html(data); //action message afficher en haut de page
                                    });
                                    jQuery( this ).dialog( "close" );
                                }
                            },
                            {
                                id: "my-buttoncancel1",
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
                    jQuery(this).css({'color': 'black', 'font-weight' : 'normal','background-color' : 'white',});
                    jQuery(this).find(':nth-child(2)').hide();
                });
                jQuery(this).css({ 'color' : 'blue', 'background-color' : 'lightblue', 'font-weight' : 'bold'});
                jQuery(this).find(':nth-child(2)').show()
                filenameremote = jQuery(this).find(':first').text();
                taillefile = jQuery(this).find(':last').text();
                filenamelocal = filenameremote ; // datetimenow() + "-" + filenameremote
                timetmp = user + "-" + datetimenow();
                nameremotepath = jQuery('input[name=path_abs_current_remote]').val() + seperator + filenameremote
                jQuery('#remotecurrrent').text(nameremotepath);
            });
        });
    }
</script>
