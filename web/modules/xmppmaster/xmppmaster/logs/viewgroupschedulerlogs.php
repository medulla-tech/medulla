<?php
/*
 * (c) 2017-2021 siveo, http://www.siveo.net/
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
 *
 *  file : logs/viewgroupschedulerlogs.php
 */
<?

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require_once("modules/dyngroup/includes/utilities.php");
include_once('modules/pulse2/includes/menu_actionaudit.php');
include_once('modules/glpi/includes/xmlrpc.php');
include_once('modules/pkgs/includes/xmlrpc.php');
include_once("modules/dyngroup/includes/xmlrpc.php");
    // Retrieve information deploy. For cmn_id
// affichefile(__FILE__);
$tab = xmlrpc_get_conrainte_slot_deployment_commands([$cmd_id]);
$contrainte  = $tab[$cmd_id] ?? "";

$pkgcreator = get_pkg_creator_from_uuid($pathpackage);

$p = new PageGenerator(_T("Deployment Group" ,"xmppmaster")." [ ".$title."]" );



$p->setSideMenu($sidemenu);
$p->display();

$hideText = _T("Hide", "xmppmaster");
$showText = _T("Show", "xmppmaster");

// detail group
$group_info = info_group($groupid);
$infospackage = pkgs_get_infos_details($pathpackage);


 $infos_base="Group id is ".$groupid."\nCommand id is ".$cmd_id;
        echo "<br>";
        echo '<h2 class="replytab" id="infofdeploy">'.$hideText.' '._T("Deployment Info", "xmppmaster").'</h2>';

        echo "<div id='deployinfo'>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                echo "<thead>";
                    echo "<tr>";
                        echo '<td class="col-w-210">';
                            echo '<span class="pkg-detail-header">'._T("Title","xmppmaster").'</span>';
                        echo '</td>';

                        echo '<td class="col-w-210">';
                            echo '<span class="pkg-detail-header">'._T("Group","xmppmaster").'</span>';
                        echo '</td>';

                        echo '<td class="col-w-210">';
                            echo '<span class="pkg-detail-header">'._T("Package","xmppmaster").'</span>';
                        echo '</td>';

                        echo '<td class="col-w-210">';
                            echo '<span class="pkg-detail-header">'._T("Start","xmppmaster").'</span>';
                        echo '</td>';
                        echo '<td class="col-w-210">';
                            echo '<span class="pkg-detail-header">'._T("End","xmppmaster").'</span>';
                        echo '</td>';

                        if ($deployment_intervals !=""){
                            echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("Deployment Intervals","xmppmaster").'</span>';
                            echo '</td>';
                        }
                    echo "</tr>";
                echo "</thead>";
                echo "<tbody>";
                    echo "<tr>";
                        echo "<td>";
                            echo  "<span title='".$infos_base."'>".$titledeploy."</span>";
                        echo "</td>";
                        echo "<td>";
                            echo $group_info['info'][0]['name_group'];
                        echo "</td>";
                        echo "<td>";
                            echo $pathpackage;
                        echo "</td>";
                        echo "<td>";
                            echo $start_date;
                        echo "</td>";
                        echo "<td>";
                            echo $end_date;
                        echo "</td>";
                        if ($deployment_intervals != ""){
                            echo "<td>";
                                echo $deployment_intervals;
                            echo "</td>";
                        }
                    echo "</tr>";
                echo "</tbody>";
            echo "</table>";
        echo "</div>";



// info group

 echo "<br>";
        echo '<h2 class="replytab" id="phase">'.$hideText.' '._T("Group Info", "xmppmaster").'</h2>';
            echo "<div id='detail_grp'>";
                echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";
                        echo "<tr>";
                            echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("Group Name","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("Creator","xmppmaster").'</span>';
                            echo '</td>';
                            if (isset($nbmachine)){
                                echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("Number of Machines","xmppmaster").'</span>';
                                echo '</td>';
                            }
                                echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("Number of shares","xmppmaster").'</span>';
                                echo '</td>';

                        echo "</tr>";
                    echo "</thead>";

                    echo "<tbody>";
                        echo "<tr>";
                            echo "<td>";
                               echo  $group_info['info'][0]['name_group'];
                            echo "</td>";
                            echo "<td>";
                               echo  $group_info['info'][0]['creator'];
                            echo "</td>";
                            if (isset($nbmachine)){
                                echo '<td>';
                                echo $nbmachine;
                                echo '</td>';
                            }
                             echo "<td>";
                               echo  count($group_info['share_partage'])-1;
                            echo "</td>";
                        echo "</tr>";
                    echo "</tbody>";
                echo "</table>";





        if  (count($group_info['share_partage']) > 1){
            echo "<br>";
            echo '<h3 id="shareowner">'._T("share user", "xmppmaster").'</h3>';
                echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";
                        echo "<tr>";
                            echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("owner Name","xmppmaster").'</span>';
                            echo '</td>';
                        echo "</tr>";
                    echo "</thead>";
                    echo "<tbody>";
                       foreach ($group_info['share_partage'] as $val){
                            echo "<tr>";
                                echo "<td>";
                                if ($val['creator'] == $group_info['info'][0]['creator']){
                                    echo  '<span class="creator-highlight">'. $val['creator'].' (Creator) </span>';
                                }else{
                                    echo  $val['creator'];
                                }
                                echo "</td>";
                            echo "</tr>";
                       }
                    echo "</tbody>";
                echo "</table>";
        }

 echo "</div>";


// ----------------------Info package-------------------------------
 echo "<br>";
    echo '<h2 class="replytab" id="phase">'.$hideText.' '._T("Packages Info", "xmppmaster").'</h2>';
    echo "<div id='detail_package'>";
 echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";
                        echo "<tr>";
                            echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("pkg Name","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("description","xmppmaster").'</span>';
                            echo '</td>';

                                echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("version","xmppmaster").'</span>';
                                echo '</td>';
 echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("uuid","xmppmaster").'</span>';
                            echo '</td>';
                                echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("os","xmppmaster").'</span>';
                                echo '</td>';

                                 echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("share Name","xmppmaster").'</span>';
                                echo '</td>';

                                 echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'._T("share Comment","xmppmaster").'</span>';
                                echo '</td>';
                        echo "</tr>";
                    echo "</thead>";

                    echo "<tbody>";
                            echo "<tr>";
                                echo "<td>";
                                    echo $infospackage['label'];
                                echo "</td>";

                                echo "<td>";
                                    echo $infospackage['description'];
                                echo "</td>";
                                echo "<td>";
                                    echo $infospackage['version'];
                                echo "</td>";

                                echo "<td>";
                                    echo $pathpackage;
                                echo "</td>";

                                echo "<td>";
                                    echo $infospackage['os'];
                                echo "</td>";

                                echo "<td>";
                                    echo $infospackage['sharename'];
                                echo "</td>";

                                echo "<td>";
                                    echo $infospackage['sharecomments'];
                                echo "</td>";


                       echo "</tr>";
                    echo "</tbody>";
                echo "</table>";

                if($infospackage[0]['AssoINVvendor'] !="" &&
                    $infospackage[0]['AssoINVsoftware'] != "" &&
                    $infospackage[0]['AssoINVversion'] !="")
                {
//                     $infospackage[0]['AssoINVinventorylicence'] !="" &&
                    echo "<br>";
                    echo '<h3 id="shareowner">'._T("Inventory detail", "xmppmaster").'</h3>';

                        echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                            echo "<thead>";

                                echo "<tr>";
                                    echo '<td class="col-w-210">';
                                        echo '<span class="pkg-detail-header">'._T("Software Name","xmppmaster").'</span>';
                                    echo '</td>';

                                    echo "<tr>";
                                    echo '<td class="col-w-210">';
                                        echo '<span class="pkg-detail-header">'._T("Vendor software]","xmppmaster").'</span>';
                                    echo '</td>';

                                    echo "<tr>";
                                    echo '<td class="col-w-210">';
                                        echo '<span class="pkg-detail-header">'._T("Version software","xmppmaster").'</span>';
                                    echo '</td>';
                                    if ($AssoINVinventorylicence){
                                        echo '<td class="col-w-210">';
                                            echo '<span class="pkg-detail-header">'._T("number version","xmppmaster").'</span>';
                                        echo '</td>';
                                    }
                                echo "</tr>";
                            echo "</thead>";

                            echo "<tbody>";
                                    echo "<tr>";
                                        echo "<td>";
                                            echo  $infospackage[0]['AssoINVsoftware'];
                                        echo "</td>";
                                        echo "<td>";
                                            echo  $infospackage[0]['AssoINVvendor'];
                                        echo "</td>";
                                          echo "<td>";
                                            echo  $infospackage[0]['AssoINVversion'];
                                        echo "</td>";
                                        if ($AssoINVinventorylicence){
                                            echo '<td>';
                                            echo  $infospackage[0]['AssoINVinventorylicence'];
                                            echo '</td>';
                                        }

                                    echo "</tr>";

                            echo "</tbody>";
                        echo "</table>";
        }

if($infospackage['dependencies'] != "")
{
    $dependenciesarray= explode(",", $infospackage['dependencies']);
    echo "<br>";
    echo '<h3 id="shareowner">'._T("dependencies", "xmppmaster").'</h3>';

        echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
            echo "<thead>";

                echo "<tr>";
                    echo '<td class="col-w-210">';
                        echo '<span class="pkg-detail-header">'._T("dependencies","xmppmaster").'</span>';
                    echo '</td>';
                echo "</tr>";
            echo "</thead>";

            echo "<tbody>";
            foreach ($dependenciesarray as $val){
                    echo "<tr>";
                        echo "<td>";
                            echo  $val;
                        echo "</td>";
                    echo "</tr>";
            }
            echo "</tbody>";
        echo "</table>";
}


$myresult = array_keys($infospackage['verify']);
sort($myresult);
if (count($myresult) <= 3){
     echo '<h2 id="shareowner">'._T("No problems detected in the formatting of deployment descriptor files", "xmppmaster").'</h32>';
}

// ---------------------------------------------
// verify package existe est bien place
// --------------------------------------------
if ($infospackage['verify']['Package_info']){
    unset($infospackage['verify']['Package_info']);
        echo "<br>";
                    echo '<h3 id="shareowner">'._T("package location detail", "xmppmaster").'</h3>';
                        echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                            echo "<thead>";

                                echo "<tr>";
                                    echo '<td class="col-w-210">';
                                        echo '<span class="pkg-detail-header">'."<h2>Packge ".$pathpackage. "</h2>".'</span>';
                                    echo '</td>';
                                echo "</tr>";
                            echo "</thead>";

                            echo "<tbody>";
                          foreach($myresult as $value ){
                                $pos = strpos($value,"Package");
                                if ($pos === false) {
                                    continue;
                                }elseif($pos == 0){
                                     if ($infospackage['verify'][$value] != ""){
                                    echo "<tr>";
                                        echo "<td>";
                                            echo  $infospackage['verify'][$value];
                                        echo "</td>";
                                    echo "</tr>";
                                     }
                               }
                            }

                            echo "</tbody>";
                        echo "</table>";

}
echo "</div>";
  unset($myresult[array_search('Package_info', $myresult)]);
// ---------------------------------------------
// verify deploy file
// --------------------------------------------

if ($infospackage['verify']['deploy_xmppdeploy']){
     unset($infospackage['verify']['deploy_xmppdeploy']);
                    echo '<h3 id="shareowner">'._T("detail descripteur file xmppdeploy", "xmppmaster").'</h3>';
                    echo "<div id='name_inventory_convergence'>";
                        echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                            echo "<thead>";

                                echo "<tr>";
                                    echo '<td class="col-w-210">';
                                        echo '<span class="pkg-detail-header">'."<h2>". "Note xmppdeploy.json file"."</h2>".'</span>';
                                    echo '</td>';
                                echo "</tr>";
                            echo "</thead>";

                            echo "<tbody>";
                          foreach($myresult as $value ){
                                $pos = strpos($value,"deploy");
                                if ($pos === false) {
                                    continue;
                                }elseif($pos == 0){
                                    if ($infospackage['verify'][$value] != ""){
                                    echo "<tr>";
                                        echo "<td>";
                                             echo  $infospackage['verify'][$value];
                                        echo "</td>";
                                    echo "</tr>";
                                    }
                               }
                            }

                            echo "</tbody>";
                        echo "</table>";
        }
unset($myresult[array_search('deploy_xmppdeploy', $myresult)]);
// ---------------------------------------------
// verify conf file
// --------------------------------------------

if ($infospackage['verify']['conf_confjson']){
    unset($infospackage['verify']['conf_confjson']);
    echo "<br>";
            echo '<h3 id="shareowner">'._T("detail descripteur file conf.json", "xmppmaster").'</h3>';
            echo "<div id='name_inventory_convergence'>";
                echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";

                        echo "<tr>";
                            echo '<td class="col-w-210">';
                                echo '<span class="pkg-detail-header">'."<h2>"."Note conf.json file"."</h2>".'</span>';
                            echo '</td>';
                        echo "</tr>";
                    echo "</thead>";

                    echo "<tbody>";
                    foreach($myresult as $value ){
                        $pos = strpos($value,"conf");
                        if ($pos === false) {
                            continue;
                        }elseif($pos == 0){
                            if ($infospackage['verify'][$value] != ""){
                                echo "<tr>";
                                    echo "<td>";
                                        echo  $infospackage['verify'][$value];
                                    echo "</td>";
                                echo "</tr>";
                            }
                        }
                    }

                    echo "</tbody>";
                echo "</table>";
}
unset($myresult[array_search('conf_confjson', $myresult)]);
 echo "</div>";

?>

<script type="text/javascript">
    function hideid(id){
        jQuery("#"+ id).hide();
        a = jQuery("#"+"title"+id).text();
        if (a.search( '<?php echo $showText;?>' ) != -1){
            a = a.replace("<?php echo $showText;?> ", "<?php echo $hideText;?> ");
        }
        else{
            a = a.replace("<?php echo $hideText;?> ", "<?php echo $showText;?> ");
        }
        jQuery("#"+"title"+id).text(a);
    }
    //hidden table by default.decommente pour hide by default
    hideid("env");
        jQuery( ".replytab" ).click(function() {
            a = jQuery(this).text();
            if (a.search( "<?php echo $showText;?>" ) != -1){
                a = a.replace( "<?php echo $showText;?> ",  "<?php echo $hideText;?> ");
            }
            else{
                a = a.replace("<?php echo $hideText;?> ",  "<?php echo $showText;?> ");
            }
            jQuery(this).text(a);
            jQuery(this).next('div').toggle();
        });

        jQuery( ".replytab2" ).click(function() {
            a = jQuery(this).text();
            jQuery(this).text(a);
            completed = jQuery(this).next('p');
            successed = completed.next('p');
            action = jQuery(".actions");
            completed.toggle();
            successed.toggle();
            action.toggle();
        });
</script>
