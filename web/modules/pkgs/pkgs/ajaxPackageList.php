<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
 * (c) 2016-2021 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/msc/includes/package_api.php");
require_once("modules/msc/includes/utilities.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
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
    top:2em; left:2em; width:25em;
    border:1px solid #000;
    background-color:#E0FFFF;
    color:#000;
    text-align: justify;
    font-weight:none;
    padding:5px;
}
</style>

<?php
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = array('filter'=> $_GET["filter"], 'bundle' => 0);
$filter1 = $_GET["filter"];
if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

$editAction = new ActionItem(_T("Edit a package", "pkgs"), "edit", "edit", "pkgs", "pkgs", "pkgs");
$editExpertAction = new EmptyActionItem(_T("Please switch to Expert mode to edit this package", "pkgs"));
$editNoRightsAction = new EmptyActionItem(_T("You must have write rights to edit this package", "pkgs"));
$emptyAction = new EmptyActionItem();
$delAction = new ActionPopupItem(_T("Delete a package", "pkgs"), "delete", "delete", "pkgs", "pkgs", "pkgs");
$delNoRightsAction = new EmptyActionItem(_T("You must have write rights to delete this package", "pkgs"));

$sharings = xmlrpc_pkgs_search_share(["login"=>$_SESSION["login"]]);

if($sharings['config']['centralizedmultiplesharing'] == true){
  /*
   * These variables will contain the packages info
   */
   $quotas = [];
   $sharingNames = [];
   $sharingUsedQuotas = [];
   $sharingQuotas = [];

   $countSharingsWithWRight = 0;
   for($i = 0; $i < count($sharings['datas']); $i++){
     $countSharingsWithWRight += ($sharings['datas'][$i]['permission'] == "w" || $sharings['datas'][$i]['permission'] == "rw") ? 1 :0;
     $quotas[$sharings['datas'][$i]['id_sharing']] = [
       'usedquotas'=>$sharings['datas'][$i]['usedquotas'],
       'quotas' => $sharings['datas'][$i]['quotas'],
       'percent' => ($sharings['datas'][$i]['quotas'] == 0) ? 0 : number_format(($sharings['datas'][$i]['usedquotas'] / 1073741824*$sharings['datas'][$i]['quotas'])*100, 2)
     ];
   }

  if($countSharingsWithWRight == 0){
    ?>
    <script>jQuery("#add").hide();</script>
    <?php
  }
  $_params = array();
  $__arraypackagename = array();
  $_versions = array();
  $_licenses = array();
  $_size = array();
  $_err = array();
  $_desc = array();
  $_os = array();
  $_editActions = array();
  $_delActions = array();

  $_packages = xmlrpc_get_all_packages($_SESSION['login'], $sharings['config']['centralizedmultiplesharing'], $start, $maxperpage, $filter);
  $_count = $_packages["total"];
  $_packages = $_packages["datas"];

  $_arraypackagename = [];
  $_localisations = [];
  $_sharing_types = [];
  $_descriptions = [];
  $_versions = [];
  $_licenses = [];
  $_sizes = [];
  $_diskUsages = [];
  $_params = [];

    for($i=0; $i< count($_packages['uuid']); $i++){
      $packageSize = $_packages['size'][$i];
      $usedQuotas = $quotas[$_packages['share_id'][$i]]['usedquotas'];
      $totalQuotas = 1048576*$quotas[$_packages['share_id'][$i]]['quotas'];
      $percentQuotas = $quotas[$_packages['share_id'][$i]]['percent'];

      if(($quotas[$_packages['share_id'][$i]]['quotas'] > 0)){
        $occupation = number_format(($_packages['size'][$i] / $totalQuotas)*100, 2);


      $size = "<span style='border-bottom: 4px double blue' title='Size : ".number_format(($packageSize/1048576), 2)." Mb&#013;"._T('Sharing disk usage', 'pkgs')." : &#013;".number_format(($usedQuotas/1048576), 2)." Mb / ".number_format(($totalQuotas/1048576), 2)." Mb ($percentQuotas %)&#013;"._T('Package occupation','pkgs')." : $occupation%'>".number_format(($packageSize/1048576), 2)." Mb</span>";
    }
    else{
      $occupation = _T("Not limited", "pkgs");
      $size = "<span style='border-bottom: 4px double black' title='Size : ".number_format(($packageSize/1048576), 2)." Mb&#013;"._T('Sharing disk usage', 'pkgs')." : ".number_format(($usedQuotas/1048576), 2)." Mb / "._T('not limited', 'pkgs')."&#013;'>".number_format(($packageSize/1048576), 2)." Mb</span>";
    }
    $_sizes[] = $size;

      if($totalQuotas != 0){
        if($percentQuotas < 70){
          $_diskUsages[] = "<span style='color:green;'>$percentQuotas %</span>";
        }
        else if($percentQuotas >=70 && $percentQuotas < 90){
          $_diskUsages[] = "<span style='color:orange;'>$percentQuotas %</span>";
        }
        else{
          $_diskUsages[] = "<span style='color:red;'>$percentQuotas %</span>";
        }
      }
      else{
        $_diskUsages[] = _T("not limited", "pkgs");
      }

      $_tmpParam = [];
      $_localisations[] = $_packages['share_name'][$i];
      $_sharing_types[] = $_packages['share_type'][$i];
      $_descriptions[] = $_packages['conf_json'][$i]['description'];
      $_versions[] = $_packages['conf_json'][$i]['version'];
      $_licenses[] = $_packages['conf_json'][$i]['inventory']['licenses'];
      $_os[] = $_packages['conf_json'][$i]['targetos'];

      $_tmpParam['pid']=base64_encode($_packages['uuid'][$i]);
      $_tmpParam['packageUuid'] = $_packages['uuid'][$i];

      $countfiles = _T('Non precised');
      $listfiles = "";
      // Missing list of file for each package
      switch($_packages['conf_json'][$i]['metagenerator']){
          case "expert":
              $_arraypackagename[] = "<img style='position:relative; top : 5px;'
                                          src='modules/pkgs/graph/img/package_expert.png'/>" .
                                          "<span style='border-bottom: 4px double blue' title='Package Expert Mode\n".$countfiles ." files : \n". $listfiles."'>".
                                              $_packages['conf_json'][$i]['name'].
                                          "</span>" ;
          break;
          case "standard":
              $_arraypackagename[] = "<img style='position:relative; top : 5px;
                                          'src='modules/pkgs/graph/img/package.png'/>".
                                          "<span style='border-bottom: 4px double black' title='Package Standart Mode\n".$countfiles ." files : \n". $listfiles."'>".
                                              $_packages['conf_json'][$i]['name'].
                                          "</span>"  ;
          break;
          default: //"manual":
              $_arraypackagename[] = "<img style='position:relative; top : 5px;'
                                          src='modules/pkgs/graph/img/package.png'/>".
                                          "<span style='border-bottom: 4px double green' title='Package manual Mode\n".$countfiles ." files : \n". $listfiles."'>".
                                              $_packages['conf_json'][$i]['name'].
                                          "</span>" ;
          break;
      }

      $_tmp_licenses = '';
      if ($_packages['conf_json'][$i]['inventory']['associateinventory'] == 1 && isset($_packages['conf_json'][$i]['inventory']['licenses']) && !empty($_packages['conf_json'][$i]['inventory']['licenses'])) {
          $_licensescount = getLicensesCount($_packages['conf_json'][$i]['inventory']['queries']['Qvendor'], $_packages['conf_json'][$i]['inventory']['queries']['Qsoftware'], $_packages['conf_json'][$i]['inventory']['queries']['Qversion'])['count'];
          // Link to the group creation for machines with licence.
          $_tmpParam['vendor'] = $_packages['conf_json'][$i]['inventory']['queries']['Qvendor'];
          $_tmpParam['software'] = $_packages['conf_json'][$i]['inventory']['queries']['Qsoftware'];
          $_tmpParam['version'] = $_packages['conf_json'][$i]['inventory']['queries']['Qversion'];
          $_tmpParam['count'] = $_licensescount;
          $_tmpParam['licencemax'] = $_packages['conf_json'][$i]['inventory']['licenses'];
          $_urlRedirect = urlStrRedirect("pkgs/pkgs/createGroupLicence", $_params);

          $_tmp_licenses = '<span style="border-width:1px;border-style:dotted; border-color:black; ">' .
              '<a href="' .
              $_urlRedirect . '" title="Create group">' .
              $_licensescount .
              '/' .
              $_packages['conf_json'][$i]['inventory']['licenses'] .
              '</a></span>';
          if ($_licensescount > $_packages['conf_json'][$i]['inventory']['licenses']) { // highlights the exceeded license count
              $_tmp_licenses = '<font color="FF0000">' . $tmp_licenses . '</font>';
          }
      }
      $_licenses[] = $_tmp_licenses;
      $_tmpParam['permission'] = $_packages['permission'][$i];

      if(!isExpertMode()) {
          // mode standart
          // seul root peut supprimer package manuel
          if ($_packages['conf_json'][$i]['metagenerator'] == 'manual') {
              $_editActions[] = $emptyAction;
              if ($_SESSION['login'] == "root"){
                  $_delActions[] = $delAction;
              }
              else{
                  $_delActions[] = $emptyAction;
              }
          }
          else if ($_packages['conf_json'][$i]['metagenerator'] == 'expert') {
            if($_packages['permission'][$i] == 'w' || $_packages['permission'][$i] == 'rw'){
              $_editActions[] = $editExpertAction;
              $_delActions[] = $delAction;
            }
            else{
              // No permission for editing/deleting
              $_editActions[] = $emptyAction;
              $_delActions[] = $emptyAction;
            }
          }
          else {
            if($_packages['permission'][$i] == 'w' || $_packages['permission'][$i] == 'rw'){
              $_editActions[] = $editAction;
              $_delActions[] = $delAction;
            }
            else{
              // No permission for editing/deleting
              $_editActions[] = $emptyAction;
              $_delActions[] = $emptyAction;
            }
          }
      }
      else {
          //mode expert
          if ($_packages['conf_json'][$i]['metagenerator'] == 'manual') {
              $_editActions[] = $emptyAction;
              if($_packages['permission'][$i] == 'w' || $_packages['permission'][$i] == 'rw'){
                $_delActions[] = $delAction;
              }
              else{
                $_delActions[] = $emptyAction;
              }
          }
          else {
              if($_packages['permission'][$i] == 'w' || $_packages['permission'][$i] == 'rw'){
                $_editActions[] = $editAction;
                $_delActions[] = $delAction;
            }
            else{
              $_editActions[] = $emptyAction;
              $_delActions[] = $emptyAction;
            }
          }
      }
      $_params[] = $_tmpParam;
    }

    // Display the list
    $n = new OptimizedListInfos($_arraypackagename, _T("Package name", "pkgs"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($_packages['share_name'], _T("Localization", "pkgs"));
    $n->addExtraInfo($_packages['permission'], _T("Permissions", "pkgs"));
    //$n->addExtraInfo($_sharing_types, _T("Localization type", "pkgs"));
    $n->addExtraInfo($_descriptions, _T("Description", "pkgs"));
    $n->addExtraInfo($_versions, _T("Version", "pkgs"));
    $n->addExtraInfo($_licenses, _T("Licenses", "pkgs"));
    $n->addExtraInfo($_os, _T("Os", "pkgs"));
    $n->addExtraInfo($_sizes, _T("Package size", "pkgs"));
    $n->addExtraInfo($_diskUsages, _T("Share usage", "pkgs"));
    $n->setItemCount($_count);
    $n->setNavBar(new AjaxNavBar($_count, $filter1));
    $n->setParamInfo($_params);
    $n->addActionItemArray($_editActions);
    $n->addActionItemArray($_delActions);
    $n->start = 0;
    $n->end = $_count;
}
else{
  $params = array();
  $arraypackagename = array();
  $versions = array();
  $licenses = array();
  $size = array();
  $err = array();
  $desc = array();
  $os = array();
  $editActions = array();
  $delActions = array();


  $packages = xmlrpc_xmppGetAllPackages($filter, $start, $start + $maxperpage);
  $count = $packages[0];
  $packages = $packages[1];

  foreach ($packages as $p) {
      $p = $p[0];
      $countfiles = 0;
      $countfiles = count($p['files']);
      $listfiles = "";
      foreach($p['files']  as $k){
          // Compose list des fichiers dans le packages
           $listfiles .="\t".$k['name']." : ".prettyOctetDisplay($k['size'])."\n";
      }
      switch($p['metagenerator']){
          case "expert":
              $arraypackagename[] = "<img style='position:relative; top : 5px;'
                                          src='modules/pkgs/graph/img/package_expert.png'/>" .
                                          "<span style='border-bottom: 4px double blue' title='Package Expert Mode\n".$countfiles ." files : \n". $listfiles."'>".
                                              $p['label'].
                                          "</span>" ;
          break;
          case "standard":
              $arraypackagename[] = "<img style='position:relative; top : 5px;
                                          'src='modules/pkgs/graph/img/package.png'/>".
                                          "<span style='border-bottom: 4px double black' title='Package Standart Mode\n".$countfiles ." files : \n". $listfiles."'>".
                                              $p['label'].
                                          "</span>"  ;
          break;
          default: //"manual":
              $arraypackagename[] = "<img style='position:relative; top : 5px;'
                                          src='modules/pkgs/graph/img/package.png'/>".
                                          "<span style='border-bottom: 4px double green' title='Package manual Mode\n".$countfiles ." files : \n". $listfiles."'>".
                                              $p['label'].
                                          "</span>" ;
          break;
      }

      $uuid = $p['id'];
      $versions[] = $p['version'];
      $desc[] = $p['description'];
      $os[] = $p['targetos'];
      // #### begin licenses ####
      $tmp_licenses = '';
      if ($p['associateinventory'] == 1 && isset($p['licenses']) && !empty($p['licenses'])) {
          $licensescount = getLicensesCount($p['Qvendor'], $p['Qsoftware'], $p['Qversion'])['count'];
          // Link to the group creation for machines with licence.
          $param = array();
          $param['vendor'] = $p['Qvendor'];
          $param['software'] = $p['Qsoftware'];
          $param['version'] = $p['Qversion'];
          $param['count'] = $licensescount;
          $param['licencemax'] = $p['licenses'];
          $urlRedirect = urlStrRedirect("pkgs/pkgs/createGroupLicence", $param);

          $tmp_licenses = '<span style="border-width:1px;border-style:dotted; border-color:black; ">' .
              '<a href="' .
              $urlRedirect . '" title="Create group">' .
              $licensescount .
              '/' .
              $p['licenses'] .
              '</a></span>';
          if ($licensescount > $p['licenses']) { // highlights the exceeded license count
              $tmp_licenses = '<font color="FF0000">' . $tmp_licenses . '</font>';
          }
      }
      $licenses[] = $tmp_licenses;
      // #### end licenses ####
      $size[] = prettyOctetDisplay($p['size']);
      $params[] = array( 'pid' => base64_encode($p['id']), 'packageUuid' => $p['id']);
      if(!isExpertMode()) {
          // mode standart
          // seul root peut supprimer package manuel
          if ($p['metagenerator'] == 'manual') {
              $editActions[] = $emptyAction;
              if ($_SESSION['login'] == "root"){
                  $delActions[] = $delAction;
              }
              else{
                  $delActions[] = $emptyAction;
              }
          }
          elseif ($p['metagenerator'] == 'expert') {
              $editActions[] = $editExpertAction;
              $delActions[] = $delAction;
          }
          else {
              $editActions[] = $editAction;
              $delActions[] = $delAction;
          }
      }
      else {
          //mode expert
          if ($p['metagenerator'] == 'manual') {
              $editActions[] = $emptyAction;
              $delActions[] = $delAction;
          }
          else {
              $editActions[] = $editAction;
              $delActions[] = $delAction;
          }
      }
    $localisations[] = $p['localisation_server'];
    $sharing_types[] = $p['sharing_type'];
  }

  // Display the list
  $n = new OptimizedListInfos($arraypackagename, _T("Package name", "pkgs"));
  $n->disableFirstColumnActionLink();
  $n->addExtraInfo($descriptions, _T("Description", "pkgs"));
  $n->addExtraInfo($versions, _T("Version", "pkgs"));
  $n->addExtraInfo($licenses, _T("Licenses", "pkgs"));
  $n->addExtraInfo($os, _T("Os", "pkgs"));
  $n->addExtraInfo($sizes, _T("Package size", "pkgs"));
  $n->setItemCount($count);
  $n->setNavBar(new AjaxNavBar($count, $filter1));
  $n->setParamInfo($params);
  $n->addActionItemArray($editActions);
  $n->addActionItemArray($delActions);
  $n->start = 0;
  $n->end = $count;

}

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();
?>
