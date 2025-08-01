<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

?>

<style>
    #LocationTitleStatus {
        margin-left: 15px;
    }

    a.info {
        position: relative;
        z-index: 24;
        color: #000;
        text-decoration: none
    }

    a.info:hover {
        z-index: 25;
        background-color: #FFF
    }

    a.info span {
        display: none
    }

    a.info:hover span {
        display: block;
        position: absolute;
        top: 2em;
        left: 2em;
        width: 50em;
        border: 1px solid #000;
        background-color: #E0FFFF;
        color: #000;
        text-align: justify;
        font-weight: none;
        padding: 5px;
    }

    #container_logs ul.navList {
        position: static !important;
        display: flex;
        gap: 1em;
        margin: 0;
        padding: 0;
    }

    .stat {
        display: flex;
        align-items: center;
        flex-direction: row;
        gap: 0.5em;
    }
</style>

<?php
require("../includes/ajaxcommon.inc.php");

if (in_array("glpi", $_SESSION['supportModList'])) {
    require_once("../../glpi/includes/xmlrpc.php");
}

$customMenu_count = xmlrpc_getCustomMenuCount($location);
$CurrentLocation = getCurrentLocation();


$namelocation = xmlrpc_getLocationName($CurrentLocation);
$machine_menu = xmlrpc_getCustomMenubylocation($location);

$arrayuuid = array();
foreach ($machine_menu as $entry) {
    // Add the modified UUID to the array
    $arrayuuid[] = trim(str_ireplace('uuid', '', $entry[0]));
}

$info = getMachineInfoImaging($arrayuuid);

// Merge the structures
foreach ($machine_menu as $item) {
    $idMachine = str_ireplace("uuid", "", $item[0]); // Assuming this corresponds to the id_machine in structure1
    $name = $item[1];
    $nicUuid = $item[2];

    // Find the corresponding machine in structure1
    foreach ($info as &$machine) {
        if ($machine['id_machine'] == $idMachine) {
            // Update the machine with new keys and values
            $machine['name'] = $name;
            $machine['nic_uuid'] = $nicUuid;
            break;
        }
    }
}
$dede = xmlrpc_getComputersWithImageInEntity($CurrentLocation);
?>
<?php
$global_status = xmlrpc_getGlobalStatus($location);
if (!empty($global_status)) {
    $disk_info = format_disk_info($global_status['disk_info']);
    $health = format_health($global_status['uptime'], $global_status['mem_info']);
    $short_status = $global_status['short_status'];
?>

    <div class="status_block">
        <h3><?php echo _T('Stats', 'imaging') ?> <?php echo _T('Entity', 'imaging') ?> <?php echo $namelocation; ?> </h3>
        <p class="stat">
            <?php $urlRedirect = urlStrRedirect("imaging/manage/creategroupcustonmenu") . "&location=" . $location; ?>
            <?php $urlRedirectgroupimaging = urlStrRedirect("imaging/manage/creategroupcustonmenuimaging") . "&location=" . $location; ?>
            <img src="img/other/machine_down.svg" width="25" height="25" /> <strong>
                <?php echo "<span>" . $short_status['total'] . "</span>"; ?></strong> <?php echo _T("client(s) registered", "imaging") ?>
            <?php
            if (intval($customMenu_count) > 0) {
                echo "(" . $customMenu_count;
                echo ' <a class="info" href="#" id="boutoninformation1" class="lienstylebouton">';
                echo _T("with custom menu", "imaging");
                echo '
                        <span>Computer list with custom menu for entity ' . $namelocation . '<br>';
                $i = 0;
                foreach ($info as $entry) {
                    if (in_array("glpi", $_SESSION['supportModList'])) {
                        if ($entry['name'] != $entry['realname']) {
                            echo "[ " . $entry['name'] . "(" . $entry['realname'] . ") ]";
                        } else {
                            echo "[" . $entry['name'] . "]";
                        }
                    } else {
                        echo "[" . $entry['name'] . "]";
                    }
                    if ($i == 5) {
                        echo "<br>";
                        $i = 0;
                    } else {
                        echo " ";
                    }
                    $i++;
                }
                echo '
                        </span>
                    </a>';
                echo '<a  href="' . $urlRedirect . '">';
                echo '<img src="img/other/machinegroup.svg" title="create group" width="25" height="25" />';
                echo '</a>';
                echo '<a href="' . $urlRedirectgroupimaging . '"  class="lienstylebouton boutoncreation">';
                echo '<img src="img/other/machinegroup.svg" title="create group imaging" width="25" height="25" />';
                echo '</a>)';

                echo '<div id="popupinformation1" title="Custom Menu">';
                echo '<p>';
                foreach ($info as $entry) {
                    if (in_array("glpi", $_SESSION['supportModList'])) {
                        $param  = array();
                        $param['tab'] = 'tabbootmenu';
                        $param['hostname'] = $entry['realname'];
                        $param['uuid'] = $entry['id_machine'];
                        $param['type'] = '';
                        $param['target_uuid'] = $entry['id_machine'];
                        $param['target_name'] = $entry['realname'];

                        $urlRedirect = urlStrRedirect("base/computers/imgtabs", $param);
                        if ($entry['newlocation'] == $entry['creationEntity']) {
                            echo '<a href="' . $urlRedirect . '">' . 'Boot menu ' . $entry['realname'] . '</a>';
                        } else {
                            echo  '<a href="' . $urlRedirect . '">' . 'Warning Name (' . $entry['1'] . ' to ' . $entry['realname'] . ') and entity (' . $entry['creationEntity'] . ' to ' . $entry['newlocation'] . ')' . '</a>';
                        }
                    } else {
                        $param  = array();
                        $param['tab'] = 'tabbootmenu';
                        $param['hostname'] = $entry['name'];
                        $param['uuid'] = $entry['id_machine'];
                        $param['type'] = '';
                        $param['target_uuid'] = $entry['id_machine'];
                        $param['target_name'] = $entry['name'];
                        $urlRedirect = urlStrRedirect("base/computers/imgtabs", $param);
                        echo '<a href="' . $urlRedirect . '">' . 'Boot menu ' . $entry['realname'] . '</a>';
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
            <img src="img/other/machine_down.svg" width="25" height="25" />
            <strong>
                <?php echo $short_status['rescue']; ?>
            </strong>/ <?php echo $short_status['total']; ?>
            <?php
            if (intval($short_status['rescue']) <= 0) {
                $text = _T("client have rescue image", "imaging");
                echo $text;
            } else {
                $text = _T("client(s) have rescue image(s)", "imaging");
                echo '<a  class="info" href="#" id="boutoninformation" class="lienstylebouton">' . $text;
                echo '<span>';
                echo '<strong>Clients with rescue images:</strong><br>';
                foreach ($dede as $val) {
                    if (intval($val[3]) == 0) {
                        echo 'Client : [' . $val[1] . "] has rescue Image : [" . $val[2] . '] ' . "<br>";
                    }
                }
                echo '</span>';
                echo '</a>';
            }
            ?>
        </p>

        <p class="stat">
            <img src="img/other/diskimage.svg" width="25" height="25" />
            <?php echo '<a href="' . 'main.php?module=imaging&submod=manage&action=master' . '"'; ?>
            <strong><?php echo $short_status['master'] . " "; ?></strong>
            <?php echo _T("masters are available", "imaging") . '</a>'; ?>
        <div id="popupinformation" title="client(s) have rescue image(s)">

            <?php
            foreach ($dede as $val) {
                if (intval($val[3]) == 0) {
                    $parm = array();
                    $parm['tab'] = 'tabimages';
                    $parm['hostname'] = $val[1];
                    $parm['uuid'] = $val[0];
                    $parm['type'] = "";
                    $parm['target_uuid'] = $val[0];
                    $parm['target_name'] = $val[1];
                    $parm['namee'] = "llllllllll";
                    $urlRedirect = urlStrRedirect("base/computers/imgtabs", $parm);
                    echo '<a href="' . $urlRedirect . '">' . 'Client : [' . $val[1] . "] has rescue Image : [" . $val[2] . '] ' . "</a><br>";
                }
            }
            ?>
        </div>
        <?php $url = urlStrRedirect("imaging/manage/groupimgtabs", ["location" => $location, "reset_defaultMenu" => 1, "target" => "all"]); ?>
        <p>
            <a href="<?php echo $url; ?>" style="color: #007bff; text-decoration: none;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">
                <?php echo _T("Reset all menu imaging from this entity", "imaging"); ?>
            </a>
        </p>
    </div>
    <!--termine cadre stat-->
    <script type="text/javascript">
        jQuery(function() {
            // définition de la boîte de dialogue
            // la méthode jQuery dialog() permet de transformer un div en boîte de dialogue et de définir ses boutons
            jQuery("#popupinformation").dialog({
                autoOpen: false,
                width: 400,
                buttons: [{
                    text: "OK",
                    click: function() {
                        jQuery(this).dialog("close");
                    }
                }]
            });

            // comportement du bouton devant ouvrir la boîte de dialogue
            jQuery("#boutoninformation").click(function(event) {
                // cette ligne est très importante pour empêcher les liens ou les boutons de rediriger
                // vers une autre page avant que l'usager ait cliqué dans le popup
                event.preventDefault();
                // affichage du popup
                jQuery("#popupinformation").dialog("open");
            });

            jQuery("#popupinformation1").dialog({
                autoOpen: false,
                width: 400,
                buttons: [{
                    text: "OK",
                    click: function() {
                        jQuery(this).dialog("close");
                    }
                }]
            });

            // comportement du bouton devant ouvrir la boîte de dialogue
            jQuery("#boutoninformation1").click(function(event) {
                // cette ligne est très importante pour empêcher les liens ou les boutons de rediriger
                // vers une autre page avant que l'usager ait cliqué dans le popup
                event.preventDefault();
                // affichage du popup
                jQuery("#popupinformation1").dialog("open");
            });

            // définition de la boîte de dialogue
            // la méthode jQuery dialog() permet de transformer un div en boîte de dialogue et de définir ses boutons
            jQuery("#popupconfirmationgroup").dialog({
                autoOpen: false,
                width: 400
            });
            jQuery(".boutoncreation").click(function(event) {
                // cette ligne est très importante pour empêcher les liens ou les boutons de rediriger vers une autre page avant que l'usager ait cliqué dans le popup
                event.preventDefault();
                // retrouve l'attribut href du lien sur lequel on a cliqué
                var targetUrl = jQuery(this).attr("href");
                // on définit les boutons ici plutôt que plus haut puisqu'on a besoin de connaître l'URL de la page, qui n'était pas encore disponible sur le document.ready.
                jQuery("#popupconfirmationgroup").dialog({
                    buttons: [{
                            text: "Create Group",
                            click: function() {
                                window.location.href = targetUrl;
                            }
                        },
                        {
                            text: "Cancel",
                            click: function() {
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
    $path = "/tmp/";
    $objprocess = array();
    $objprocess['location'] = $_GET['location'];

    $objprocess['process'] = $path . $scriptmulticast;
    $objprocess['process'] = $scriptmulticast;
    $informationsparameters = xmlrpc_GetMulticastMultiSessionParameters($_GET['location']);
    if (safeCount($informationsparameters) == 0) {
        $objprocess['process'] = $scriptmulticast;
        $objprocess['process'] = $scriptmulticast;
        xmlrpc_stop_process_multicast($objprocess);
        $objprocess['process'] = $path . $scriptmulticast;
        xmlrpc_clear_script_multicast($objprocess);
    } else {
        $tailleimagedisk = array();
        $objprocess['gid'] = $informationsparameters['gid'];
        $objprocess['uuidmaster'] = $informationsparameters['uuidmaster'];
        $objprocess['itemlabel'] = $informationsparameters['itemlabel'];
        $objprocess['path'] = $path;
        $objprocess['scriptmulticast'] = $scriptmulticast;
        $resultdisplay = get_object_vars(json_decode(xmlrpc_check_process_multicast_finish($objprocess)));

        $arraytaille = get_object_vars($resultdisplay['sizeuser']);
        foreach ($resultdisplay['partitionlist'] as $dd) {
            $tailleimagedisk[] = $arraytaille[$dd];
        }
        $informationdisk = $resultdisplay['informations'];
        foreach ($resultdisplay['partitionlist'] as $partition) {
            foreach ($informationdisk as $valeur) {
                $pos = strpos($valeur, $partition);
                if ($pos !== false && $pos == 0) {
                    $resultdisplay1[$partition] =  explode(" ", $valeur);
                }
            }
        }
    }
    $objprocess['process'] = $path . $scriptmulticast;
    if (xmlrpc_muticast_script_exist($objprocess)) {
        echo '<script type="text/javascript">';
        echo 'var locations = "' . $_GET['location'] . '";';
        echo 'var uuidmaster = "' . $informationsparameters['uuidmaster'] . '";';
        echo 'var itemlabel = "' . $informationsparameters['itemlabel'] . '";';
        echo 'var gid = "' . $informationsparameters['gid'] . '";';
        echo 'var path = "' . $path . '";';
        echo 'var scriptmulticast = "' . $scriptmulticast . '";';
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

        echo '
var interval = setInterval(barprogress,6000);
 </script>';
        $charvaleur = array("+"); //liste de caracteres remplacés dans le nom du  master
        echo '
        <div class="status" id="checkprocess">
        <div class="status_block">  ';
        // fichier /tmp/multicast.sh n'existe pas "ne pas afficher cadre Multicast Current Location"
        $objprocess['process'] = $scriptmulticast;
        if (xmlrpc_check_process_multicast($objprocess)) {
            // "affichage bouton arrêt"
            // voir apres pour bar de progression
            $nom_master = str_replace($charvaleur, " ", $objprocess['itemlabel']);

            echo '<h3>' . _T('Multicast Current Location', 'imaging') . '</h3>';
            echo  "Master : " . $nom_master . "<br>";
            echo '<form action="';
            echo urlStr("imaging/manage/multicastaction/");
            echo '" method="POST">';
            echo '<input name="multicast"  type="hidden" value="stop" />';
            echo '<input name="location"  type="hidden" value="' . $objprocess['location'] . '" />';
            echo '<input name="process"  type="hidden" value="' . $scriptmulticast . '" />';
            echo '<input name="path" type="hidden" value="' . $path . '" />';
            echo '<span style="display:none;" id="completespan">Complete</span>';
            echo '<div id="complete">';
            echo '<input name="bgo" type="submit" class="btnPrimary"
        value="';
            echo _T("Stop multicast deploy", "imaging");
            echo '" /> ';
            echo '</div>';
            echo '</form>';
        } else {
            $nom_master = str_replace($charvaleur, " ", $objprocess['itemlabel']);
            echo "<h3>" . _T('Multicast Current Location', 'imaging') . '</h3>';
            echo  "Master : " . $nom_master . "<br>";
            echo '<form action="';
            echo urlStr("imaging/manage/multicastaction/");
            echo '" method="POST">';
            echo '<input name="multicast"  type="hidden" value="start" />';
            echo '<input name="location"  type="hidden" value="' . $objprocess['location'] . '" />';
            echo '<input name="process"  type="hidden" value="' . $scriptmulticast . '" />';
            echo '<input name="path" type="hidden" value="' . $path . '" />
        <input name="bgo" type="submit" class="btnPrimary"
        value="';
            echo _T("Start multicast deploy", "imaging");
            echo '" />
        </form>';
            echo "<br>";
            echo '<form action="';
            echo urlStr("imaging/manage/multicastaction/");
            echo '" method="POST">';
            echo '<input name="multicast"  type="hidden" value="clear" />';
            echo '<input name="location"  type="hidden" value="' . $objprocess['location'] . '" />';
            echo '<input name="process"  type="hidden" value="' . $scriptmulticast . '" />';
            echo '<input name="path" type="hidden" value="' . $path . '" />
        <input name="bgo" type="submit" class="btnPrimary"
        value="';
            echo _T("Clear multicast deploy", "imaging");
            echo '" />
        </form>';
        }
        $index = 0;
        foreach ($resultdisplay['partitionlist'] as $partition) {
            echo "<p>";
            $tailledisk = intval($resultdisplay1[$partition][1]) * 512;
            $taillediskfMo =  round($tailledisk / (1024 * 1024), 2);
            echo '<strong>' . $resultdisplay1[$partition][0] . '</strong>' .
                " Size [" . $taillediskfMo . " MB] " .
                " Type [" . $resultdisplay1[$partition][2] . "] ";
            if (strcmp($resultdisplay1[$partition][3], "yes") == 1) {
                echo "Bootable";
            }
            echo " Space in use [" . round($tailleimagedisk[$index] / (1024 * 1024), 2) . " MB]";
            // Tranfer [";
            //echo '<span id='. $partition  .'span>'.' 0</span> bytes]';
            echo '<progress id="' . $partition . '" max="' . $tailleimagedisk[$index] . '" value="0" form="form-id">0%</progress>';
            echo "</p>";
            $index = $index + 1;
        }
        echo '
            </div>
        </div>';
    } else {
        $objprocess['process'] = $scriptmulticast;
        if (xmlrpc_check_process_multicast($objprocess)) {
            // if /tmp/multicast.sh is running then stoping
            $objprocess['process'] = $scriptmulticast;
            xmlrpc_stop_process_multicast($objprocess);
            $objprocess['process'] = $path . $scriptmulticast;
            xmlrpc_clear_script_multicast($objprocess);
        }
    }
?>
    <div class="spacer"></div>

    <h2 class="activity"><?php echo _T('Recent activity', 'imaging') ?></h2>

<?php
    $ajax = new AjaxFilter("modules/imaging/manage/ajaxLogs.php", "container_logs", array(), "Logs");
    $ajax->display();
    echo "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
} else {
    $e = new ErrorMessage(_T("Can't connect to the imaging server linked to the selected entity.", "imaging"));
    print $e->display();
}

require("../includes/ajaxcommon_bottom.inc.php");
?>
