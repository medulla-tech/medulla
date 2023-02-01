<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2018-2021 Siveo, http://www.siveo.net/
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
require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/pkgs/includes/functions.php");
require_once("modules/pkgs/includes/html.inc.php");
require_once("modules/pkgs/includes/query.php");
require_once("modules/pkgs/includes/class.php");

if (in_array('dyngroup', $_SESSION['modulesList'])) {
    require_once("modules/dyngroup/includes/dyngroup.php");
}

$p = new PageGenerator(_T("Edit package", "pkgs"));
$p->setSideMenu($sidemenu);
$p->display();
function isExpertMode1(){return 1;}
// var formating
$_GET['p_api'] = isset($_GET['p_api']) ? $_GET['p_api'] : "";
$_GET['p_api'] = "UUID/package_api_get1";
$package = array();

/*
 * File Upload
 */
if (isset($_POST["bcreate"]) || isset($_POST["bassoc"])) {

    $p_api_id = $_POST['p_api'];
    $need_assign = False;
    if ($_GET["action"] == "add") {
        $need_assign = True;
    }

    foreach (array('id', 'label', 'version', 'description', 'Qvendor', 'Qsoftware', 'Qversion', 'mode',
            'boolcnd', 'licenses', 'targetos', 'metagenerator',
            'creator', 'creation_date', 'editor', 'edition_date', 'localisation_server', 'previous_localisation_server') as $post) {
        //$package[$post] = iconv("utf-8","ascii//TRANSLIT",$_POST[$post]);
        $package[$post] = $_POST[$post];
    }

    foreach (array('reboot', 'associateinventory') as $post) {
        $package[$post] = ($_POST[$post] == 'on' ? 1 : 0);
    }

        // Package command
        $package['command'] = array('name' => $_POST['commandname'], 'command' => $_POST['commandcmd']);
        // Simple package: not a bundle
        $package['sub_packages'] = array();

    // Send Package Infos via XMLRPC
    $ret = putPackageDetail($package, $need_assign);
    $plabel = $ret[3]['label'];
    $pversion = $ret[3]['version'];

    if (in_array('dyngroup', $_SESSION['modulesList'])) {
        // update convergence groups request if any
        update_convergence_groups_request($package);
        // stop current active convergence commands and set new commands
        restart_active_convergence_commands($p_api_id, $package);
    }

    $package_uuid = "";
    if(isset($_POST['saveList']))
    {
        $package_uuid = $ret[2];
        $saveList = $_POST['saveList'];
        $saveList1 = clean_json($saveList);
        //$saveList1 = iconv("utf-8","ascii//TRANSLIT",$saveList1);
        $result = save_xmpp_json($ret[2], $saveList1);
    }

    if (!isXMLRPCError() and $ret and $ret != -1) {
        if ($ret[0]) {
            if ($_GET["action"] == "add") {
                $str = sprintf(_T("Package successfully added in %s", "pkgs"), $ret[2]);
                new NotifyWidgetSuccess($str);
                if (!isset($_POST["bassoc"])) {
                    header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('location' => base64_encode($p_api_id)))); # TODO add params to go on the good p_api
                    exit;
                }
            } else {//ICI
                $str= _T("Package successfully edited", "pkgs");
                new NotifyWidgetSuccess($str);
                $package = $ret[3];
                if(!isset($_POST["bassoc"])) {
                  header("Location: " . urlStrRedirect("pkgs/pkgs/edit", array('pid' => $_GET['pid'], 'packageUuid' => $package['id'], 'permission' => $_GET['permission'], 'mod' => $_GET['mod'])));
                  exit;
                }
            }
            $pid = $package['id'];

            $cbx = array($_POST['random_dir']);
            // If there is uploaded files to associate
            if ($_POST['files_uploaded']) {
                // === BEGIN ASSOCIATING FILES ==========================
                $ret = associatePackages($pid, $cbx, 1);
                if (!isXMLRPCError() and is_array($ret)) {
                    if ($ret[0]) {
                        // ICI$_POST['files_uploaded']
                        $str = sprintf(_T("Files successfully added to the package <b>%s (%s)</b>", "pkgs"), $plabel, $pversion);
                        new NotifyWidgetSuccess($str);
                        header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('location' => base64_encode($p_api_id))));
                        exit;
                    } else {
                        $reason = '';
                        if (count($ret[1]) > 0) {
                            $reason = sprintf(" : <br/>%s", $ret[1]);
                        }
                        $str = sprintf(_T("Failed to associate files%s", "pkgs"), $reason);
                        new NotifyWidgetFailure($str);
                    }
                } else {
                    $str= _T("Failed to associate files", "pkgs");
                    new NotifyWidgetFailure($str);
                }
                // === END ASSOCIATING FILES ==========================
            }
        } else {
            new NotifyWidgetFailure($ret[1]);
        }
    } else {
        $str =_T("Package failed to save", "pkgs");
        new NotifyWidgetFailure($str);
    }
    if($package_uuid != ""){
      xmlrpc_update_package_size($pid);
      xmlrpc_chown($package_uuid);
    }
}

//start formulaire
$p_api_id = base64_decode($_GET['p_api']);

$p_api_id = "UUID/package_api_get1";
//$p_api_id = "UUID/package_api_get1";

$pid = base64_decode($_GET['pid']);
//Result for root, pkgs.removeFilesFromPackage: ([['Administratif.zip'], []],)

if (isset($_GET['delete_file'], $_GET['filename'],$_GET['packageUuid'] )) {
    //$ret = removeFilesFromPackage($p_api_id, $pid, array($_GET['filename']));
    // RPC method call from user root: pkgs.removeFilesFromPackage(['firefox-64.0.tar.bz2'], '')

    $ret = removeFilesFromPackage($_GET['packageUuid'], array($_GET['filename']));
    if (!isXMLRPCError() and is_array($ret)) {
        $errorexplain = "";
        $successexplain = "";
        if (count($ret[1]) > 0) {$errorexplain   = sprintf(" : <br/>%s", implode("<br/>", $ret[1]));}
        if (count($ret[0]) > 0) {$successexplain = sprintf(" : <br/>%s", implode("<br/>", $ret[0]));}
        if (count($ret[1]) > 0){
            $str = sprintf(_T("Failed to delete files%s", "pkgs"), $errorexplain);
            if (count($ret[0]) > 0){
                $str += sprintf(_T("<br/>File successfully deleted. %s", "pkgs"), $successexplain);
            }
            new NotifyWidgetFailure($str);
        }
        else{
            $str = sprintf(_T("<br/>File successfully deleted. %s", "pkgs"), $successexplain);
            new NotifyWidgetSuccess($str);
        }
    }
    else {
        $str = _T("Failed to delete files", "pkgs");
        new NotifyWidgetFailure($str);
    }
    header("Location: " . urlStrRedirect("pkgs/pkgs/edit", array('p_api' => $_GET['p_api'], 'pid' => $_GET['pid'], 'packageUuid' => $_GET['packageUuid'])));
    exit(0);
}
    $formElt = new HiddenTpl("id");//use in js for createUploader
    $selectpapi = new HiddenTpl('p_api');//use in js for createUploader
    if (count($package) == 0) {

        $title = _T("Edit a package", "pkgs");
        $activeItem = "index";
        # get existing package
        $pid = base64_decode($_GET['pid']);
        $package = xmpp_getPackageDetail($pid);
        if ($package['do_reboot']) {
            $package['reboot'] = $package['do_reboot'];
        }
        //$p_api_number = count(getUserPackageApi());
    }
/*
 * Page form
 */

$json = json_decode(get_xmpp_package($_GET['packageUuid']),true);

if(!isset($json['info']['creator']) || $json['info']['creator'] == ""){
  $json['info']['creator'] = 'root';
}

// display an edit package form (description, version, ...)
$f = new ValidatingForm(array("onchange"=>"getJSON()","onclick"=>"getJSON()"));
$f->push(new Table());


// if ($p_api_number > 1) {
//     $f->add(
//             new TrFormElement(_T("PIP", "pkgs"), $selectpapi), array("value" => $pid, "hide" => $hide)
//     );
//     $f->add(
//             new TrFormElement(_T("Package API", "pkgs"), $formElt), array("value" => $p_api_id, "hide" => $hide)
//     );
// } else {
    $f->add(
            $selectpapi, array("value" => $p_api_id, "hide" => True)
    );
    $f->add(
            $formElt, array("value" => $pid, "hide" => True)
    );
// }


$f->add(new HiddenTpl("id"), array("value" => $package['id'], "hide" => True));
// Uploaded field,
$f->add(new HiddenTpl("files_uploaded"), array("value" => 0, "hide" => True));
if ($_GET["action"] == "add") {
    $f->add(new HiddenTpl("mode"), array("value" => "creation", "hide" => True));
}
else{
    $f->add(new HiddenTpl("mode"), array("value" => "edition", "hide" => True));
}


$fields = array(
    array("label", _T("Package label", "pkgs"), array("required" => True)),
    array("version", _T("Package version", "pkgs"), array("required" => True)),
    array('description', _T("Description", "pkgs"), array()),
);
$cmds = array();
$options = array();
if(!isExpertMode1())
{

    $cmds = array(
        array('command', _T('Command\'s name : ', 'pkgs'), _T('Command : ', 'pkgs')),
    );

    $options = array(
        array('reboot', _T('Need a reboot ?', 'pkgs'))
    );

}

$os = array(
    array('win', 'linux', 'mac'),
    array(_T('Windows'), _T('Linux'), _T('Mac OS'))
);

$f->add(new HiddenTpl("editor"), array("value" => $_SESSION['login'], "hide" => True));
$f->add(new HiddenTpl("edition_date"), array("value" => date("Y-m-d H:i:s"), "hide" => True));
$f->add(new HiddenTpl("creator"), array("value" => $json['info']['creator'], "hide" => True));
$f->add(new HiddenTpl("creation_date"), array("value" => $json['info']["creation_date"], "hide" => True));

if(isset($_SESSION['sharings'])){
  $getShares = $_SESSION['sharings'];
}
else{
  $getShares = $_SESSION['sharings'] = xmlrpc_pkgs_search_share(["login"=>$_SESSION["login"]]);
}
$shares =[];
foreach($getShares['datas'] as $share){
  if(preg_match("#w#i", $share['permission'])){
    $shares[] = $share;
  }
}

if(isset($getShares["config"]["centralizedmultiplesharing"]) && $getShares["config"]["centralizedmultiplesharing"] == true){
  $previous_localisation = (isset($package['previous_localisation_server']) && $package['previous_localisation_server'] != "") ? $package['previous_localisation_server'] : $json['info']['localisation_server'];

  $f->add(new HiddenTpl("previous_localisation_server"), array("value" => $previous_localisation, "hide" => True));
  if(isset($getShares["config"]["movepackage"]) && $getShares["config"]["movepackage"] == True){
    if(isset($json["info"]["Dependency"]) && count($json["info"]["Dependency"]) == 0){
      if(count($shares) == 1){ // Just 1 sharing (no choice)
        $f->add(new HiddenTpl("localisation_server"), array("value" => $package['localisation_server'], "hide" => True));
      }
      else{ // sharing server > 1
        $sharesNames = [];
        $sharesPaths = [];
        foreach($shares as $key=>$value){
          $sharesNames[] = (isset($value['comments']) && $value['comments'] != "") ? $value['comments'] : $value['name'];
          $sharesPaths[] = $value['name'];
        }
        $location_servers = new SelectItem('localisation_server');
        $location_servers->setElements($sharesNames);
        $location_servers->setElementsVal($sharesPaths);
        $location_servers->setSelected($json['info']["localisation_server"]);

        $f->add(
                new TrFormElement(_T('Share', 'pkgs'), $location_servers), array()
        );
      }
    }
    else{ // Dependencies > 0
      $f->add(new HiddenTpl("localisation_server"), array("value" => $package["localisation_server"], "hide" => True));
    }
  }
  else{ // movepackage == false
    $f->add(new HiddenTpl("localisation_server"), array("value" => $json['info']["localisation_server"], "hide" => True));
  }
}
foreach ($fields as $p) {
    $f->add(
            new TrFormElement($p[1], new AsciiInputTpl($p[0])), array_merge(array("value" => $package[$p[0]]), $p[2])
    );
}

foreach ($options as $p) {
    $op = ($package[$p[0]] == 1 || $package[$p[0]] == '1' || $package[$p[0]] === 'enable');
    $f->add(
            new TrFormElement($p[1], new CheckboxTpl($p[0])), array("value" => ($op ? 'checked' : ''))
    );
}

$oslist = new SelectItem('targetos');
$oslist->setElements($os[1]);
$oslist->setElementsVal($os[0]);
$f->add(
        new TrFormElement(_T('Operating System', 'pkgs'), $oslist), array("value" => $package['targetos'])
);

if(isExpertMode1())
{
  $f->add(new HiddenTpl("metagenerator"), array("value" => "expert", "hide" => True));
}
else {
  $f->add(new HiddenTpl("metagenerator"), array("value" => "standard", "hide" => True));
}

if(isExpertMode1())
{
    //$f->add(new HiddenTpl("last_editor"), array("value" => $_SESSION['login'], "hide" => True));
    $f->add(new HiddenTpl('transferfile'), array("value" => true, "hide" => true));

    if(isset($json['info']['methodetransfert']))
    {
        $setmethodetransfert = $json['info']['methodetransfert'];
    }
    else
    {
        $setmethodetransfert = 'pushrsync';
    }
    $methodtransfer = new SelectItem('methodetransfert');
    // Allowed methods are pullcurl, pushrsync, pullrsync, pullscp
    $methodtransfer->setElements(['pushrsync', 'pullrsync', 'pulldirect']);
    $methodtransfer->setElementsVal(['pushrsync', 'pullrsync', 'pulldirect']);
    $methodtransfer->setSelected($setmethodetransfert);

    $f->add(new TrFormElement(_T('Transfer method','pkgs'),$methodtransfer, ['trid'=>'trTransfermethod']),['value'=>'']);

    if(isset($json['info']['limit_rate_ko']))
    {
        $setlimit_rate_ko = $json['info']['limit_rate_ko'];
    }
    else
    {
        $setlimit_rate_ko = '';
    }
    $bpuploaddownload = new IntegerTpl("limit_rate_ko");
    $bpuploaddownload->setAttributCustom('min = 0');
    $f->add(
        new TrFormElement(_T("bandwidth throttling (ko)",'pkgs'), $bpuploaddownload), array_merge(array("value" => $setlimit_rate_ko), array('placeholder' => _T('<in ko>', 'pkgs')))
    );

    if(isset($json['info']['spooling']))
    {
        $spooling = $json['info']['spooling'];
    }
    else
    {
        $spooling = 'ordinary';
    }
    $rb = new RadioTpl("spooling");
    $rb->setChoices(array(_T('high priority', 'pkgs'), _T('ordinary priority', 'pkgs')));
    $rb->setvalues(array('high', 'ordinary'));
    $rb->setSelected($spooling);
    $f->add(new TrFormElement(_T('Spooling', 'pkgs'), $rb));

    if(isset($json["info"]["launcher"]) && $json["info"]["launcher"] != "")
    {
        $launcher = (base64_decode($json["info"]["launcher"], true) != false)? $launcher = base64_decode($json["info"]["launcher"]) : $json["info"]["launcher"];
    }
    else{
    $launcher = "";
    }
    $f->add(
            new TrFormElement(_T("Launcher (kiosk)", "pkgs"), new InputTpl("launcher")), ["value"=>$launcher,"placeholder"=>"C:\Program Files\my_app\app.exe"]
    );

    // Get the sorted list of dependencies
    if(isset($json['info']['Dependency']))
    {
        $dependencies = $json['info']['Dependency'];
    }
    else
        $dependencies = [];

    //Get all the dependencies as uuid => name
    $allPackagesList = get_dependencies_list_from_permissions($_SESSION["login"]);
    $allDependenciesList = [];
    $packagesInOptionAdded = '';
    $packagesInOptionNotAdded = '';
    $dependenciesArray = [];
    foreach($dependencies as $dependency){
      $dependenciesArray[] = [
        "uuid"=>$dependency,
        "version"=>"",
        "name"=>""
      ];
    }
    foreach($allPackagesList as $xmpp_package) {
      if(is_array($xmpp_package)){
        if($_GET['packageUuid'] != $xmpp_package['uuid']){
          $uuid = $xmpp_package['uuid'];
          $name = $xmpp_package['name'];
          $version = $xmpp_package['version'];

          if(in_array($uuid, $dependencies))
          {
            $id = array_search($uuid, $dependencies);
            $dependenciesArray[$id]["name"] = $name;
            $dependenciesArray[$id]["version"] = $version;
          }
          else{
            $packagesInOptionNotAdded .= '<option title="'.$name.' v.'.$version.'" value="'.$uuid.'">'.$name.' v.'.$version.'</option>';
            $allDependenciesList[] = $xmpp_package;
          }
        }
      }
    }

    foreach($dependenciesArray as $dep){
      $packagesInOptionAdded .= '<option title="'.$dep["name"].' v.'.$dep["version"].'" value="'.$dep["uuid"].'">'.$dep["name"].' v.'.$dep["version"].'</option>';
    }
    $f->add(new TrFormElement(_T("Dependencies", "pkgs"),new SpanElement('<div id="grouplist">
    <table style="border: none;" cellspacing="0">
        <tr>
            <td style="border: none;">
                <div>
                    <img src="img/other/up.svg" width="25" height="25" alt="|^" id="moveDependencyToUp" onclick="moveToUp()"/><br/>
                    <img src="img/other/down.svg" width="25" height="25" alt="|v" id="moveDependencyToDown" onclick="moveToDown()"/></a><br/>
                </div>
            </td>
            <td style="border: none;">
                <h3>'._T('Added dependencies', 'pkgs').'</h3>
                <div class="list">
                    <select multiple size="13" class="list" name="Dependency" id="addeddependencies">
                    '.$packagesInOptionAdded.'
                    </select>
                    <div class="opt_name" style="position:absolute;"></div>
                </div>
            </td>
            <td style="border: none;">
                <div>
                    <img src="img/other/right.svg" width="25" height="25" alt="-->" id="moveDependencyToRight" onclick="moveToRight()"/><br/>
                    <img src="img/other/left.svg" width="25" height="25" alt="<--" id="moveDependencyToLeft" onclick="moveToLeft()"/></a><br/>
                </div>
            </td>
            <td style="border: none;">
                <div class="list" style="padding-left: 10px;">
                    <h3>'._T('Available dependencies', 'pkgs').'</h3>
                    <input type="text" id="dependenciesFilter" value="" placeholder="'._T("search by name ...", "pkgs").'"><br/>

                    <select multiple size="13" class="list" name="members[]" id="pooldependencies">
                        '.$packagesInOptionNotAdded.'
                    </select>
                    <div class="opt_name" style="position:absolute;"></div>
                </div>
                <div class="clearer"></div>
            </td>
        </tr>
    </table>
</div>',"pkgs")));
}

foreach ($cmds as $p) {
    $f->add(
            new HiddenTpl($p[0] . 'name'), array("value" => $package[$p[0]]['name'], "hide" => True)
    );
    $f->add(
      new TrFormElement($p[2], new TextareaTplArray(['name'=>$p[0] . 'cmd', "required"=>"required","value" => htmlspecialchars($package[$p[0]]['command'])]))
    );
}

/* =================   BEGIN FILE LIST  ===================== */

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$names = array();
// $cssClasses = array();
$params = array();

$pserver_base_url = '';

foreach ($package['files'] as $file) {
    if ($file['name'] == "MD5SUMS" || $file['name'] == "xmppdeploy.json")
        continue;
    $names[] = $file['name'];
    $params[] = array(
        'p_api' => $_GET['p_api'],
        'pid' => $_GET['pid'],
        'packageUuid' => $_GET['packageUuid'],
        'filename' => $file['name'],
        'delete_file' => 1
    );
//     $viewVersionsActions[] = $viewVersionsAction;
//     $cssClasses[] = 'file';
}

$count = count($names);
$n = new OptimizedListInfos($names, _T('File', 'pkgs'));
$n->disableFirstColumnActionLink();
//$n->addExtraInfo($sizes, _T("Size", "pkgs"));
$n->setCssClass('file');
$n->setItemCount($count);
$n->start = isset($_GET['start']) ? $_GET['start'] : 0;
$n->end = 1000;
$n->setParamInfo($params); // Setting url params

$n->addActionItem(new ActionConfirmItem(_T("Delete file", 'pkgs'), "edit", "delete", "filename", "pkgs", "pkgs", _T('Are you sure you want to delete this file?', 'pkgs')));

/* =================   END FILE LIST   ===================== */

addQuerySection($f, $package);

// =========================================================================
// UPLOAD FORM
// =========================================================================

if (isset($_SESSION['random_dir'])) {
    $upload_tmp_dir = sys_get_temp_dir();
    delete_directory($upload_tmp_dir . '/' . $_SESSION['random_dir']);
}

$m = new MultiFileTpl3('filepackage');
_T("Click here to select files", "pkgs");
_T("Upload Queued Files", "pkgs");

// =========================================================================

$f->add(
        new TrFormElement("Files", $n, array())
);

$f->add(
        new TrFormElement("", $m, array())
);

// =========================================================================

$f->pop();
if(isExpertMode1())
{
    $f->add(new HiddenTpl('saveList'), array('id'=>'saveList','name'=>'saveList',"value" => '', "hide" => True));
    include('addXMPP.php');
}

$f->addValidateButton("bcreate");

$f->display();

?>

<script>
jQuery(function(){
  jQuery(".opt_bubble").on("mouseover", function(e){
    let bubble = jQuery(this).parent().next(".opt_name");
    let element = this;
    let bodyRect = document.body.getBoundingClientRect();
    let elementRect = element.getBoundingClientRect();
    let offsetY = elementRect.top - bodyRect.top - 15;

    let pkgsName = jQuery(element).text();
    jQuery(bubble).text(pkgsName);
    jQuery(bubble).css("background-color", "yellow");
    jQuery(bubble).css("left", elementRect.x+"px");
    jQuery(bubble).css("top", offsetY+"px");
    jQuery(bubble).show();
  })

  jQuery(".opt_bubble").on("mouseleave", function(){
    let bubble = jQuery(this).parent().next(".opt_name");
    jQuery(bubble).text("");

  })

  dependenciesFilter = jQuery("#dependenciesFilter");
  pooldependencies = jQuery("#pooldependencies option");

  dependenciesFilter.on("change click hover keypress keydown", function(event){
    if(dependenciesFilter.val() != ""){
      regex = new RegExp(dependenciesFilter.val(), "i");
      jQuery.each(pooldependencies, function(id, dependency){
        optionSelector = jQuery(dependency)
        if(regex.test(dependency.title) === false){
          optionSelector.hide();
        }
        else{
          optionSelector.show();
        }
      })
    }
    else{
      jQuery.each(pooldependencies, function(id, dependency){
        optionSelector = jQuery(dependency)
        optionSelector.show();
      })
    }
  })


  jQuery("input[name='label']").attr("maxlength", 60);
  jQuery("#container_input_description").prepend("<div style='color:red;'><?php echo _T("Accentuated and special chars are not allowed", "pkgs");?></div>");
})
</script>
