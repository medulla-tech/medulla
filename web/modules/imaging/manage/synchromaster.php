<?php
/*
 * (c) 2015 Siveo, http://http://www.siveo.net
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
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/post_install_script.php');
// recuperation pid des process
$process  = xmlrpc_checkProcessCloneMasterToLocation("/bin/bash /usr/bin/synch-masters");
$nbprocess = count($process);
$processsinfos = array();
$z=xmlrpc_statusReadFile ("/tmp/synch-masters.out");
$location = getCurrentLocation();
list($list, $values) = getEntitiesSelectableElements();
    foreach($z as $line ){
        $dede = explode(" ",$line);
        $startpointlocation[$list[$dede[1]]];
        $processsinfos[$dede[0]]['startpoint']=array_pop(explode('>',$list['UUID'.$dede[1]]));
        $processsinfos[$dede[0]]['endpoint']=array_pop(explode('>',$list['UUID'.$dede[2]]));
    }

if( $nbprocess == 0){
    header("Location: " . urlStrRedirect("imaging/manage/master"));
    exit;
}
$p = new PageGenerator(sprintf(_T("Master copy: %s", "imaging"), $_GET['label']));
$sidemenu->forceActiveItem("master");
$p->setSideMenu($sidemenu);
$p->display();
echo "$desc";
$tab=array();
$tabjavascript="var ArrayProcesslog = '";
foreach($process as $log){
    $tab[] = "synch_masters_".$log.".log";
}

$str=implode(",", $tab) ;
$tabjavascript.=$str."';";
echo '<div style="color: blue;font-size: 16px;" id="msg">';
echo _T("Copy of master Not Started", "imaging");
echo '</div>';
for ($i=0;$i<$nbprocess;$i++){
    echo '<div id="ab'.$process[$i].'">';
    echo _T("Copy of master", "imaging").$_GET['label']. " from ".$processsinfos[$process[$i]]['startpoint']." to ".$processsinfos[$process[$i]]['endpoint'];
    echo '</div>';
    echo '<div>';
    echo '<p style="color: blue;" id="po'.$process[$i].'">';
    echo "Not Started";
    echo "</p>";
    echo'<progress id="pb'.$process[$i].'" 
     max="100" value="0" form="form-id">0%</progress>
     <span id="bb'.$process[$i].'"></span>';
    echo '</div>';
    echo "<br>";
}
echo '<script type="text/javascript">';
echo '
function strtotab(chaine){
    var reg=new RegExp("[ ]+", "g");
    var tableau=chaine.split(reg);
    tableau.pop();
    tableau.shift();
    return tableau;
}';

echo $tabjavascript;
echo 'console.log(ArrayProcesslog);';
echo 'para = JSON.stringify(ArrayProcesslog);';
echo'
var interval = setInterval(function() {
        var request = jQuery.ajax({
            url: "modules/imaging/manage/ajaxcheckprogressbar.php",
            type: "GET",
            data: {"params": ArrayProcesslog}
    });

    request.done(function(msg) {
        var regUrl = new RegExp("[a-zA-Z._-]", "gi");
        var t = JSON.parse(msg)        
        var keyvaleur=Object.keys(t)
        var terminer=new Array();
        for(var i= 0; i < keyvaleur.length; i++){
            console.log(t[keyvaleur[i]]);
            console.log(keyvaleur[i]);
            var numprocess =  keyvaleur[i].replace(regUrl,"");
            bb="#bb"+ numprocess
            jQuery(bb).text(t[keyvaleur[i]])
            var tableau = strtotab(t[keyvaleur[i]]);
            tableau[1] = tableau[1].replace(/(\s+)?.$/, "")
            po="#po"+ numprocess
            if (tableau[1] == 100 ){
                jQuery(po).text("'._T("Complete", "imaging").'");
            }
            else{
                jQuery(po).text("'._T("In progress", "imaging").'");
            }
            pb="#pb"+ numprocess
            jQuery(pb).attr("value",tableau[1]);
            terminer.push(tableau[1])
        }
        var finih_clone = 1;
        for (var i= 0; i < terminer.length; i++){
            if (terminer[i] != 100){
                finih_clone= 0;
                break;
            }
        }
        if ( finih_clone == 1 ){
            jQuery("#msg").text("'._T("Copy of master complete", "imaging").'");
        }
        else{
            jQuery("#msg").text("'._T("Copy of master In progress", "imaging").'");
        }
  });
},3000);';
echo '</script>';
?>