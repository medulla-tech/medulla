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
}

.download{
    display : none;
    background: url('modules/xmppmaster/graph/img/browserdownload.png') no-repeat;
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

</style>

<?
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
/*
print_r($_GET);
print_r($_POST);*/
$uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
$machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
$ma = xmlrpc_getMachinefromjid($machine);

$tab = explode("/",$machine);
$p = new PageGenerator(_T("xmpp files browser", 'xmppmaster')." : ". $ma['hostname']." (".$ma['platform']. ")"); 
$p->setSideMenu($sidemenu);
$p->display();
// creation repertoire namemachine si non existe.
// et recuperation pathcurent pour cette machine eg /var/lib/pulse2/transfertfiles/machine25pulse
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
<div id="messageaction">

</div>
<br>
<div id="global">

    <div id="gauche">
        <div class ="titlebrowser"><h2><?php echo _T("File Serveur Pulse", 'xmppmaster'); ?></h2></div>
        <div class ="currentdir">
            <h2 id="localcurrentdir">Name Directory: <span id="dirlocal"></span></h2>
        </div>
            <div id="fileshowlocal" class="fileshow">
             <?php
                printf ('
                <form>
                    <input id ="path_abs_current_local" type="hidden" name="path_abs_current_local" value="%s">
                    <input id ="parentdirlocal" type="hidden" name="parentdirlocal" value="%s">
                </form>' ,$curentdir, $filecurentdir['parentdir']);
                ?>
            </div>
       <div class ="piedbrowser"><h2></h2></div>
    </div>

   <div id="droite">
        <div class ="titlebrowser">
            <h2>
                <?php echo _T("Files Machines", 'xmppmaster')." : ". $ma['hostname']." [".$ma['platform']."]"; ?>
            </h2>
        </div>
        <div class ="currentdir">
            <h2 id="remotecurrentdir">Name Directory: <span id="dirremote"></span>
            </h2>
        </div>
            <div id ="fileshowremote" class="fileshow">
            </div>
    </div>

    <div class ="piedbrowser"> 
        <form>
            <div>
                <!--<input  class="btnPrimary" id ="download" type="button" name="Dowload" value="<< Download <<"> -->
            </div>
        </form> 
    </div>
</div>

<script type="text/javascript">
    jQuery( document ).ready(function() {
        fileremote = false;
        filelocal  = false;
        taillefile = "";
        filenameremote = "";
        filenamelocal = "";
        timetmp ="";// le repertoire d'acceuil".
        user = "<?php echo $_SESSION['login']; ?>";
        jid = "<?php echo $ma['jid']; ?>";
        nameremotepath = "";
        jQuery("#download").hide(200)
        local();
        remote();
    });

    function datetimenow(){
        var newdate = new Date();
        var moi      = "0" + (newdate.getMonth() +1 );
        var jour     = "0" + newdate.getDate();
        var heure    = "0" + newdate.getHours();
        var minutes  = "0" + newdate.getMinutes();
        var secondes = "0" + newdate.getSeconds();
        var datetime = newdate.getFullYear() +
                                                "-" + 
                                                moi.substr(-2)+ 
                                                "-"+ jour.substr(-2)+ 
                                                "-"+ heure.substr(-2)+
                                                ":"+ minutes.substr(-2)+
                                                ":"+ secondes.substr(-2);
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
                        "modules/xmppmaster/xmppmaster/ajaxxmpprefrechfileslocal.php",
                        {
                            "parentdirlocal" : parentdirlocal,
                            "path_abs_current_local" : path_abs_current_local,
                            "machine" : <?php echo '"'.$machine.'"'; ?>,
                            "os" : <?php echo '"'.$ma['platform'].'"'; ?>,
                            "selectdir" : selectdir
                        },
                        function() {
        // LOCAL
            jQuery("ul.leftdir > li").click(function() {
                var dirsel = jQuery(this).text();
                if (typeof dirsel == 'undefined'){
                    var dirsel = "";
                }
                //  recupere repertoire en local
                local(dirsel);
                jQuery('#dirlocal').text(jQuery(this).text());
            });
            // on ne peut pas selectionner un fichier juste le repertoire de copie.
            // le fichier dest aura le meme nom que le fichier scr 
            // jQuery("ul.leftfile > li").click(function() {
            // recupere file en local
            // alert(jQuery(this).text());
            // });
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

        jQuery( "#fileshowremote" ).load(
                        "modules/xmppmaster/xmppmaster/ajaxxmpprefrechfilesremote.php",
                        {
                            "parentdirremote" : parentdirremote,
                            "path_abs_current_remote" : path_abs_current_remote,
                            "machine" : <?php echo '"'.$machine.'"'; ?>,
                            "os" : <?php echo '"'.$ma['platform'].'"'; ?>,
                            "selectdir" : selectdir
                        },
                        function() {
            // REMOTE
            jQuery("ul.rightdir > li").click(function() {
                fileremote = false;
                filenameremote = "";
                var dirsel = jQuery(this).text();
                if (typeof dirsel == 'undefined'){
                    var dirsel = "";
                }
                remote(dirsel);
                jQuery('#dirremote').text(jQuery(this).text());
            });
            jQuery(".download").click(function() {
                if (fileremote){
                    // fichier pas repertoire.
                    // alert(jQuery('input[name=path_abs_current_remote]').val());
                    var responce_user = confirm("<?php echo _T("Copy Remote File", 'xmppmaster'); ?> : " +
                                                jQuery('input[name=path_abs_current_remote]').val() + seperator + filenameremote+
                                                "\nto\n " + "<?php echo _T("Local File : ", 'xmppmaster'); ?> : "+
                                                jQuery('input[name=path_abs_current_local]').val()+"/"+timetmp+"/"+filenamelocal);

                    if (responce_user == true) {
                        jQuery.get( "modules/xmppmaster/xmppmaster/ajaxxmppplugindownload.php",  {
                                dest : jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp + "/" + filenamelocal,
                                src : jQuery('input[name=path_abs_current_remote]').val() + seperator +  filenameremote,
                                directory : jQuery('input[name=path_abs_current_local]').val() + "/" + timetmp,
                                "jidmachine" : jid }, function( data ) {
                                jQuery("#messageaction").text(data);
                        });
                    }
                }
            });
            jQuery("ul.rightfile > li").click(function() {
                //  recupere file en remote
                fileremote = true;
                jQuery(".rightfile LI").each(function(){ 
                    jQuery(this).css({'color': 'black', 'font-weight' : 'normal'});
                    jQuery(this).find(':nth-child(2)').hide()
                });
                jQuery(this).css({ 'color' : 'blue', 'font-weight' : 'bold'});
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
</script>
