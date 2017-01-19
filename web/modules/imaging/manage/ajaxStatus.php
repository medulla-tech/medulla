<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
 * (c) 2015 Siveo, http://http://www.siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* common ajax includes */
require("../includes/ajaxcommon.inc.php");

if (in_array("glpi", $_SESSION['supportModList'])) {
    require_once("../../glpi/includes/xmlrpc.php");
}



$t = new TitleElement(_T("Status", "imaging"), 3);
$t->display();

$customMenu_count = xmlrpc_getCustomMenuCount($location);
//$customMenu_count = xmlrpc_getCustomMenuCountdashboard($location);

$namelocation = xmlrpc_getLocationName(getCurrentLocation());
$gg = xmlrpc_getCustomMenubylocation($location);

if (in_array("glpi", $_SESSION['supportModList'])) {
    foreach ($gg as &$entry){
        $computersummary=getLastMachineGlpiPart($entry[0], 'Summary');
        foreach ($computersummary[0] as $val){
            switch($val[0]){
                case "Computer Name":
                    $entry['realname']=$val[1][2];
                    break;
                case "Entity (Location)":
                        $entry['newlocation']=$val[1];
                        break;
                case "os image":
                        $entry['OS'] = $val[1];
                        break;
                case "Domain":
                    $entry['Domain']  = $val[1];
                    break;
                    
                case " Service Pack":
                    $entry['ServicePack']  = $val[1];
                    break;
                case "Model / Type":
                    $part = explode("/",$val[1] );
                    $entry['Model']  = $part[0];
                    $entry['type']  = $part[0];
                    break;
            }
            $entry['creationEntity'] =  $namelocation;
        }
    }
}


$dede= xmlrpc_getComputersWithImageInEntity(getCurrentLocation());
//smm = xmlrpc_getMyMenuProfile(58);

//$ffffff = xmlrpc_getMyMenuProfile(58);
//imaging.getMyMenuProfile('58',)
$global_status = xmlrpc_getGlobalStatus($location);
if (!empty($global_status)) {
    $disk_info = format_disk_info($global_status['disk_info']);
    $health = format_health($global_status['uptime'], $global_status['mem_info']);
    $short_status = $global_status['short_status'];
    ?>
<style>
a.info{
position:relative;
z-index:24;
color:#000;
text-decoration:none
}
 
a.info:hover{
z-index:25;
background-color:#FFF
}
 
a.info span{
display: none
}
 
a.info:hover span{
display:block;
position:absolute;
top:2em; left:2em; width:50em;
border:1px solid #000;
background-color:#E0FFFF;
color:#000;
text-align: justify;
font-weight:none;
padding:5px;
}
</style>

    <div class="status">
        <div class="status_block">
            <h3><?php echo _T('Space available on server', 'imaging') ?></h3>
            <?php echo $disk_info; ?>
        </div>
        <div class="status_block">
            <h3><?php echo _T('Load on server', 'imaging') ?></h3>
            <?php echo $health; ?>
        </div>
    </div>

    <div class="status">
        <!--<div class="status_block">
            <h3 style="display: inline"><?php echo _T('Synchronization state', 'imaging') ?> : </h3>
        <?php
        $led = new LedElement('green');
        $led->display();
        echo "&nbsp;" . _T("Up-to-date", "imaging");
        ?>

        </div>-->
        <div class="status_block">
            <?php //<a href=" echo urlStrRedirect("imaging/imaging/createCustomMenuStaticGroup"); &location=UUID1">ZZZ</a> ?>
            <h3><?php echo _T('Stats', 'imaging') ?> <?php echo _T('Entity', 'imaging') ?> <?php echo $namelocation; ?>  </h3>
        
            <p class="stat">
            <? $urlRedirect = urlStrRedirect("imaging/manage/creategroupcustonmenu")."&location=".$location; ?>
            <? $urlRedirectgroupimaging = urlStrRedirect("imaging/manage/creategroupcustonmenuimaging")."&location=".$location; ?>
                <img src="img/machines/icn_machinesList.gif" /> <strong>
                <?php echo $short_status['total']; ?></strong> <?php echo _T("client(s) registered", "imaging") ?>
                <?php
                    if (intval($customMenu_count) > 0){
                        echo "(".$customMenu_count; 
                        echo' <a class="info" href="#" id="boutoninformation1" class="lienstylebouton">';
                        echo _T("with custom menu", "imaging");
                        echo '
                        <span>Computer list with custom menu for entity '. $namelocation.'<br>';
                            $i=0;
                            foreach ($gg as $entry){
                                if (in_array("glpi", $_SESSION['supportModList'])) {
                                    if ($entry[1] != $entry['realname']){
                                        echo "[ ". $entry[1]."(".$entry['realname'].") ]";
                                    }
                                    else{
                                        echo "[". $entry[1]."]";
                                    }
                                }
                                else{
                                    echo "[". $entry[1]."]";
                                }
                                    if ($i == 5){
                                            echo "<br>";
                                            $i=0;
                                        }
                                        else {
                                            echo " ";
                                        }
                                        $i++;
                            }
                            echo '
                        </span>
                    </a>';
                    echo '<a  href="'. $urlRedirect .'">'; 
                    echo '<img src="img/machines/icn_machinesList.gif" title="create group "/>';
                    echo '</a>';
                    echo '<a href="'. $urlRedirectgroupimaging .'"  class="lienstylebouton boutoncreation">';
                    echo '<img src="img/machines/icn_machinesList.gif" title="create group imaging" />';
                    echo '</a>)';

                    echo '<div id="popupinformation1" title="Custom Menu">';
                    echo '<p>';
                            foreach ($gg as $entry){
                                if (in_array("glpi", $_SESSION['supportModList'])) {
                                    $param  = array();
                                    $param['tab']='tabbootmenu';
                                    $param['hostname']=$entry['realname'];
                                    $param['uuid']=$entry[0];
                                    $param['type']='';
                                    $param['target_uuid']=$entry[0];
                                    $param['target_name']=$entry['realname'];
                                    
                                    $urlRedirect = urlStrRedirect("base/computers/imgtabs",$param);
                                    if ( $entry['newlocation'] == $entry['creationEntity']){
                                        echo '<a href="'.$urlRedirect.'">'.'Boot menu '.$entry['realname'].'</a>';
                                    }
                                    else
                                    {
                                    echo  '<a href="'.$urlRedirect.'">'.'Warning Name ('. $entry['1'].' to '.$entry['realname'].') and entity ('.$entry['creationEntity'].' to '.$entry['newlocation'].')'.'</a>';
                                    }
                                }
                                else
                                {
                                    $param  = array();
                                    $param['tab']='tabbootmenu';
                                    $param['hostname']=$entry[1];
                                    $param['uuid']=$entry[0];
                                    $param['type']='';
                                    $param['target_uuid']=$entry[0];
                                    $param['target_name']=$entry[1];
                                    $urlRedirect = urlStrRedirect("base/computers/imgtabs",$param);
                                    echo '<a href="'.$urlRedirect.'">'.'Boot menu '.$entry['realname'].'</a>';
                                }
                        }
                    echo '</p>';
                    echo '</div>';
                    echo '<div id="popupconfirmationgroup" title="Attention !">
                        <p>The creation of an imaging group will reset the boot menus of all the machines in the group?</p>
                    </div>  ';
                echo '</p>';
            }
            ?>
            <p class="stat">
                <img src="img/machines/icn_machinesList.gif" />
                <strong> 
                    <?php echo $short_status['rescue']; ?>
                </strong>/<?php echo $short_status['total']; ?>
                    <?php
                        if (intval($short_status['rescue']) <= 0){
                            $text = _T("client have rescue image", "imaging");
                            echo $text;
                        }
                        else{
                            $text = _T("client(s) have rescue image(s)", "imaging");
                            echo '<a  class="info" href="#" id="boutoninformation" class="lienstylebouton">'.$text;
                            echo '<span>';
                            echo '<strong>ddd</strong><br>';
                            foreach ( $dede as $val){
                                if ( intval($val[3]) == 0){
                                    echo 'Client : ['.$val[1]."] has rescue Image : [". $val[2].'] '."<br>";
                                }
                            } 
                            echo '</span>';
                            echo '</a>';
                        }
                    ?>
            </p>
            <p class="stat">
                <img src="img/common/cd.png" />
                <? echo '<a href="'.'main.php?module=imaging&submod=manage&action=master'.'"'; ?>
                <strong><?php echo $short_status['master']." "; ?></strong>
                <?php echo _T("masters are available", "imaging").'</a>'; ?>
                <!--
                    <a id="kkk" href="#" >fffff</a>
                
                <a href="#" id="boutoninformation" class="lienstylebouton">Information</a>-->
                <!--
                    <div id="a_masquer" style="display:none">
                        Contenu de la div en question.
                    </div>
                -->
                <div id="popupinformation" title="client(s) have rescue image(s)">
                <p>

                <? 
                    foreach ( $dede as $val){
                        if ( intval($val[3]) == 0){
                            $parm=array();
                            $parm['tab'] = 'tabimages';
                            $parm['hostname'] = $val[1];
                            $parm['uuid'] = $val[0];
                            $parm['type'] = "";
                            $parm['target_uuid'] = $val[0];
                            $parm['target_name'] = $val[1];
                            $parm['namee'] = "llllllllll";
                            $urlRedirect = urlStrRedirect("base/computers/imgtabs",$parm);
                            echo '<a href="'.$urlRedirect.'">'.'Client : ['.$val[1]."] has rescue Image : [". $val[2].'] '."</a><br>";
                        }
                    } 
                ?>
                </p>
                </div>
            </p>
        </div>
    </div>
    
    <script type="text/javascript">

    jQuery(function () {

        // définition de la boîte de dialogue

        // la méthode jQuery dialog() permet de transformer un div en boîte de dialogue et de définir ses boutons

        jQuery( "#popupinformation" ).dialog({
            autoOpen: false,
            width: 400,
            buttons: [
                {
                    text: "OK",
                    click: function() {
                        jQuery( this ).dialog( "close" );
                    }
                }
            ]
        });

        // comportement du bouton devant ouvrir la boîte de dialogue

        jQuery( "#boutoninformation" ).click(function( event ) {
            // cette ligne est très importante pour empêcher les liens ou les boutons de rediriger
            // vers une autre page avant que l'usager ait cliqué dans le popup
            event.preventDefault();
            // affichage du popup
            jQuery( "#popupinformation" ).dialog( "open" );
        });
        
        jQuery( "#popupinformation1" ).dialog({
            autoOpen: false,
            width: 400,
            buttons: [
                {
                    text: "OK",
                    click: function() {
                        jQuery( this ).dialog( "close" );
                    }
                }
            ]
        });

        // comportement du bouton devant ouvrir la boîte de dialogue

        jQuery( "#boutoninformation1" ).click(function( event ) {
            // cette ligne est très importante pour empêcher les liens ou les boutons de rediriger
            // vers une autre page avant que l'usager ait cliqué dans le popup
            event.preventDefault();
            // affichage du popup
            jQuery( "#popupinformation1" ).dialog( "open" );
        });
        
  
        // définition de la boîte de dialogue

        // la méthode jQuery dialog() permet de transformer un div en boîte de dialogue et de définir ses boutons

        jQuery("#popupconfirmationgroup").dialog( {

            autoOpen: false,

            width: 400

        });
        jQuery(".boutoncreation").click(function(event) {

        // cette ligne est très importante pour empêcher les liens ou les boutons de rediriger

        // vers une autre page avant que l'usager ait cliqué dans le popup

        event.preventDefault();

        // retrouve l'attribut href du lien sur lequel on a cliqué

        var targetUrl = jQuery(this).attr("href");

        // on définit les boutons ici plutôt que plus haut puisqu'on a besoin de connaître l'URL de la page, qui n'était pas encore disponible sur le document.ready.

        jQuery("#popupconfirmationgroup").dialog({

            buttons: [

                {  

                    text: "Create Group",    

                    click: function () {

                        window.location.href = targetUrl;

                    }

                },

                {

                    text: "Cancel",

                    click: function () {

                        jQuery(this).dialog("close");

                    }

                }

            ]

        });

 

        // affichage du popup

        jQuery("#popupconfirmationgroup").dialog("open");

    });
 

});
    </script>




 <!--// regles de gestions affichage.
 // fichier /tmp/multicast.sh n'existe pas "ne pas afficher cadre Multicast Current Location"
 
 // fichier /tmp/multicast.sh existe
 // multicast lancer "affichage seulement bouton arrêt" voir aprés pour bar de progression
 // multicast non lancer "affichage seulement bouton stop"
 
 // cas extreme 
 // cas si  fichier /tmp/multicast.sh n'existe plus et /tmp/multicast.sh lancer normalement possible
 // stoper /tmp/multicast.sh
 
 // action bouton arret
 // 1)  stoper /tmp/multicast.sh
 // 2)  supprimer le fichier /tmp/multicast.sh
 // 3) regénéré les menus  unicast
 
 // action bouton marche
 // 1) start /tmp/multicast.sh
 
 // progress bar script ajaxcheckstatusmulticast appel toutes les 5 secondes xmlrpc_check_process_multicast_finish
 -->
 <?php
 $resultdisplay1 = array();
$scriptmulticast = 'multicast.sh';
$path="/tmp/";
$objprocess=array();
$objprocess['location']=$_GET['location'];

$objprocess['process'] = $path.$scriptmulticast;
$objprocess['process'] = $scriptmulticast;
if (!isset($_SESSION['PARAMMULTICAST'])){
    $objprocess['process'] = $scriptmulticast;
    $objprocess['process'] = $scriptmulticast;
    xmlrpc_stop_process_multicast ($objprocess);
    $objprocess['process'] = $path.$scriptmulticast;
    xmlrpc_clear_script_multicast($objprocess);
}
else{
    $tailleimagedisk=array();
    $objprocess['gid'] = $_SESSION['PARAMMULTICAST']['gid'];
    $objprocess['uuidmaster'] = $_SESSION['PARAMMULTICAST']['uuidmaster'];
    $objprocess['itemlabel'] = $_SESSION['PARAMMULTICAST']['itemlabel'];
    $objprocess['path'] = $path;
    $objprocess['scriptmulticast'] = $scriptmulticast;
    $resultdisplay = get_object_vars(json_decode(xmlrpc_check_process_multicast_finish($objprocess)));

    $arraytaille = get_object_vars($resultdisplay['sizeuser']);
    foreach($resultdisplay['partitionlist'] as $dd){
        $tailleimagedisk[]=$arraytaille[$dd];
    }
    $informationdisk = $resultdisplay['informations'];
    foreach ( $resultdisplay['partitionlist'] as $partition ){
        foreach($informationdisk as $valeur ){
            $pos = strpos($valeur, $partition);
            if  ($pos !== False && $pos == 0 ){
                $resultdisplay1[$partition] =  explode(" ",$valeur);
            }
        }
    }
}
$objprocess['process'] = $path.$scriptmulticast;
if (xmlrpc_muticast_script_exist($objprocess)){
echo '<script type="text/javascript">';
echo 'var locations = "'.$_GET['location'].'";';
echo 'var uuidmaster = "'.$_SESSION['PARAMMULTICAST']['uuidmaster'].'";';
echo 'var itemlabel = "'.$_SESSION['PARAMMULTICAST']['itemlabel'].'";';
echo 'var gid = "'.$_SESSION['PARAMMULTICAST']['gid'].'";';
echo 'var path = "'.$path.'";';
echo 'var scriptmulticast = "'.$scriptmulticast.'";';
echo 'var transfertbloctaille = 1024;';
echo '
function barprogress() {
        var request = jQuery.ajax({
            url: "modules/imaging/manage/ajaxcheckstatusmulticast.php",
            type: "GET",
            data: {"location" :locations,"gid":gid,"uuidmaster":uuidmaster,"itemlabel":itemlabel,"path": path,"scriptmulticast" : scriptmulticast}
    });
    request.done(function(msg) {
        var t = JSON.parse(msg)
        progressbar = "#"+ t["partionname"];
        tailleprogressbar = "#"+ t["partionname"]+"span";
        if ( t["indexpartition"] > 0 ){
            for( i=0 ; i< t["indexpartition"];i++){
                namepartition = t["partitionlist"][i]
                progressbar1 = "#"+ namepartition;
                //console.log(jQuery(progressbar1).attr("max"));
                jQuery(progressbar1).attr("value",jQuery(progressbar1).attr("max"));
            }
        }
        taille = t["bytesend"];
        console.log("taille " + taille + "   partition "  + t["partionname"] +"  finish " + t["finish"]+ " Complete "+  t["complete"])
        jQuery(progressbar).attr("value",taille);
        tailletransfert =  taille ;
        if(t["complete"]==true){
            jQuery("#complete").hide( "slow" );
            jQuery("#completespan").show( "slow");
        }
        if(t["finish"]==true){
//             jQuery("#complete").hide( "slow" );
//             jQuery("#completespan").show( "slow");
             clearInterval(interval);
        }
    });
}';
echo 'barprogress();';

echo'
var interval = setInterval(barprogress,2000);
 </script>';
    $charvaleur = array("+");//liste de caracteres remplacés dans le nom du  master
    echo '
        <div class="status" id="checkprocess">
        <div class="status_block">  ';
    // fichier /tmp/multicast.sh n'existe pas "ne pas afficher cadre Multicast Current Location"
    $objprocess['process'] = $scriptmulticast;
    if (xmlrpc_check_process_multicast($objprocess)){
        // "affichage bouton arrêt"
        // voir apres pour bar de progression
        $nom_master = str_replace($charvaleur, " ", $objprocess['itemlabel']);
          
        echo'<h3>'._T('Multicast Current Location', 'imaging').'</h3>';
        echo  "Master : ".$nom_master."<br>";
        echo '<form action="'; 
        echo urlStr("imaging/manage/multicastaction/");
        echo '" method="POST">';
        echo '<input name="multicast"  type="hidden" value="stop" />';
        echo '<input name="location"  type="hidden" value="'.$objprocess['location'].'" />';
        echo '<input name="process"  type="hidden" value="'.$scriptmulticast.'" />';
        echo '<input name="path" type="hidden" value="'.$path.'" />';
        echo '<span style="display:none;" id="completespan">Complete</span>';
        echo '<div id="complete">';
        echo '<input name="bgo" type="submit" class="btnPrimary"
        value="';
        echo _T("Stop multicast deploy", "imaging");
        echo '" /> ';
        echo '</div>';
        echo '</form>';
    }
    else{
        $nom_master = str_replace($charvaleur, " ", $objprocess['itemlabel']);
        echo "<h3>"._T('Multicast Current Location', 'imaging').'</h3>';
        echo  "Master : ".$nom_master."<br>";
        echo '<form action="'; 
        echo urlStr("imaging/manage/multicastaction/"); echo '" method="POST">';
        echo '<input name="multicast"  type="hidden" value="start" />';
        echo '<input name="location"  type="hidden" value="'.$objprocess['location'].'" />';
        echo '<input name="process"  type="hidden" value="'.$scriptmulticast.'" />';
        echo '<input name="path" type="hidden" value="'.$path.'" />
        <input name="bgo" type="submit" class="btnPrimary"
        value="';
        echo _T("Start multicast deploy", "imaging");
        echo '" />    
        </form>';
        echo "<br>";
        echo '<form action="'; 
        echo urlStr("imaging/manage/multicastaction/"); echo '" method="POST">';
        echo '<input name="multicast"  type="hidden" value="clear" />';
        echo '<input name="location"  type="hidden" value="'.$objprocess['location'].'" />';
        echo '<input name="process"  type="hidden" value="'.$scriptmulticast.'" />';
        echo '<input name="path" type="hidden" value="'.$path.'" />
        <input name="bgo" type="submit" class="btnPrimary"
        value="';
        echo _T("Clear multicast deploy", "imaging");
        echo '" />    
        </form>';
            }
        $index=0;
        foreach ( $resultdisplay['partitionlist'] as $partition ){
            echo "<p>";
                $tailledisk = intval($resultdisplay1[$partition][1]) * 512;
                $taillediskfMo =  round ($tailledisk /(1024*1024),2);
                echo '<strong>'.$resultdisplay1[$partition][0].'</strong>'.
                " Size [".$taillediskfMo." MB] ".
                " Type [".$resultdisplay1[$partition][2] ."] ";
              
                if (strcmp($resultdisplay1[$partition][3], "yes") == 1) echo "Bootable";
                echo " Space in use [".round ($tailleimagedisk[$index] /(1024*1024),2)." MB]";
                // Tranfer [";
                //echo '<span id='. $partition  .'span>'.' 0</span> bytes]';
                echo '<progress id="'.$partition.'" max="'.$tailleimagedisk[$index].'" value="0" form="form-id">0%</progress>';
            echo "</p>";
            $index=$index+1;
        }
    echo'
            </div>
        </div>';
}else{
    $objprocess['process'] = $scriptmulticast;
    if (xmlrpc_check_process_multicast($objprocess)){
        // if /tmp/multicast.sh is running then stoping
        $objprocess['process'] = $scriptmulticast;
        xmlrpc_stop_process_multicast ($objprocess);
        $objprocess['process'] = $path.$scriptmulticast;
        xmlrpc_clear_script_multicast($objprocess);
    }
}
?>
    <div class="spacer"></div>

    <h3 class="activity"><?php echo _T('Recent activity', 'imaging') ?></h3>

    <?php
    $ajax = new AjaxFilter("modules/imaging/manage/ajaxLogs.php", "container_logs", array(), "Logs");
    //$ajax->setRefresh(10000);
    $ajax->display();
    echo "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
} else {
    $e = new ErrorMessage(_T("Can't connect to the imaging server linked to the selected entity.", "imaging"));
    print $e->display();
}

require("../includes/ajaxcommon_bottom.inc.php");
?>
