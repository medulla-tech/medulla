<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2018 Siveo, http://www.siveo.net/
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

// var formating
$_GET['p_api'] = isset($_GET['p_api']) ? $_GET['p_api'] : "";

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

    foreach (array('id', 'label', 'version', 'description', 'Qvendor', 'Qsoftware', 'Qversion',
            'boolcnd', 'licenses', 'targetos', 'metagenerator') as $post) {
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
    $ret = putPackageDetail($p_api_id, $package, $need_assign);
    $plabel = $ret[3]['label'];
    $pversion = $ret[3]['version'];

    if (in_array('dyngroup', $_SESSION['modulesList'])) {
        // update convergence groups request if any
        update_convergence_groups_request($p_api_id, $package);
        // stop current active convergence commands and set new commands
        restart_active_convergence_commands($p_api_id, $package);
    }


    if(isset($_POST['saveList']))
    {
        $saveList = $_POST['saveList'];
        $saveList1 = clean_json($saveList);
        //$saveList1 = iconv("utf-8","ascii//TRANSLIT",$saveList1);
        $result = save_xmpp_json($ret[2],$saveList1);
    }

    if (!isXMLRPCError() and $ret and $ret != -1) {
        if ($ret[0]) {
            if ($_GET["action"] == "add") {
                $str = sprintf(_T("Package successfully added in %s", "pkgs"), $ret[2]);
                new NotifyWidgetSuccess($str);
                xmlrpc_setfrompkgslogxmpp( $str,
                                            "PKG",
                                            '',
                                            0,
                                            $ret[2],
                                            'Manuel',
                                            '',
                                            '',
                                            '',
                                            "session user ".$_SESSION["login"],
                                            'Packaging | List | Create | Manual');
                if (!isset($_POST["bassoc"])) {
                    header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('location' => base64_encode($p_api_id)))); # TODO add params to go on the good p_api
                    exit;
                }
            } else {//ICI
                $str= _T("Package successfully edited", "pkgs");
                new NotifyWidgetSuccess($str);
                xmlrpc_setfrompkgslogxmpp( $str,
                                            "PKG",
                                            '',
                                            0,
                                            "",
                                            'Manuel',
                                            '',
                                            '',
                                            '',
                                            "session user ".$_SESSION["login"],
                                            'Packaging | List | | Create |Manual');
                $package = $ret[3];
            }
            $pid = $package['id'];

            $cbx = array($_POST['random_dir']);
            // If there is uploaded files to associate
            if ($_POST['files_uploaded']) {
                // === BEGIN ASSOCIATING FILES ==========================
                $ret = associatePackages($p_api_id, $pid, $cbx, 1);
                if (!isXMLRPCError() and is_array($ret)) {
                    if ($ret[0]) {
                        $explain = '';
                        if (count($ret) > 1) {
                            $explain = sprintf(" : <br/>%s", implode("<br/>", $ret[1]));
                        }
                        // ICI$_POST['files_uploaded']
                        $str = sprintf(_T("Files successfully added to the package <b>%s (%s)</b>", "pkgs"), $plabel, $pversion);
                        new NotifyWidgetSuccess($str);
                        xmlrpc_setfrompkgslogxmpp( $str,
                                                    "PKG",
                                                    '',
                                                    0,
                                                    $_POST['files_uploaded'],
                                                    'Manuel',
                                                    '',
                                                    '',
                                                    '',
                                                    "session user ".$_SESSION["login"],
                                                    'Packaging | List | Manual');

                        header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('location' => base64_encode($p_api_id))));
                        exit;
                    } else {
                        $reason = '';
                        if (count($ret) > 1) {
                            $reason = sprintf(" : <br/>%s", $ret[1]);
                        }
                        //ICI
                        $str = sprintf(_T("Failed to associate files%s", "pkgs"), $reason);
                        new NotifyWidgetFailure($str);
                        xmlrpc_setfrompkgslogxmpp( $str,
                                                    "PKG",
                                                    '',
                                                    0,
                                                    $_POST['files_uploaded'],
                                                    'Manuel',
                                                    '',
                                                    '',
                                                    '',
                                                    "session user ".$_SESSION["login"],
                                                    'Packaging | Files | Manual');
                    }
                } else {
                    $str= _T("Failed to associate files", "pkgs");
                    new NotifyWidgetFailure($str);
                    xmlrpc_setfrompkgslogxmpp( $str,
                                                "PKG",
                                                '',
                                                0,
                                                $_POST['files_uploaded'],
                                                'Manuel',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'Packaging | Files | Manual');
                }
                // === END ASSOCIATING FILES ==========================
            }
        } else {
            new NotifyWidgetFailure($ret[1]);
            xmlrpc_setfrompkgslogxmpp( $ret[1],
                                        "PKG",
                                        '',
                                        0,
                                        "",
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'Packaging | Files | Manual');
        }
    } else {
        $str =_T("Package failed to save", "pkgs");
        new NotifyWidgetFailure($str);
        xmlrpc_setfrompkgslogxmpp( $str,
                                        "PKG",
                                        '',
                                        0,
                                        "",
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'Packaging | Files | Manual');
    }
}

$p_api_id = base64_decode($_GET['p_api']);
$pid = base64_decode($_GET['pid']);

if (isset($_GET['delete_file'], $_GET['filename'])) {
    $ret = removeFilesFromPackage($p_api_id, $pid, array($_GET['filename']));
    if (!isXMLRPCError() and is_array($ret)) {
        if ($ret[0]) {
            $explain = '';
            if (count($ret) > 1) {
                $explain = sprintf(" : <br/>%s", implode("<br/>", $ret[1]));
            }
            //ICI
            $str = sprintf(_T("File successfully deleted.", "pkgs"));
            new NotifyWidgetSuccess($str);
             xmlrpc_setfrompkgslogxmpp( $str,
                                        "PKG",
                                        '',
                                        0,
                                        $_GET['filename'],
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'Packaging | Files | Delete | Manual');
        } else {
            $reason = '';
            if (count($ret) > 1) {
                $reason = sprintf(" : <br/>%s", $ret[1]);
            }
            $str = sprintf(_T("Failed to delete files%s", "pkgs"), $reason);
            new NotifyWidgetFailure($str);
            xmlrpc_setfrompkgslogxmpp( $str,
                                        "PKG",
                                        '',
                                        0,
                                        $_GET['filename'],
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'Packaging | Files | Delete | Manual');
        }
    } else {
        $str = _T("Failed to delete files", "pkgs");
        new NotifyWidgetFailure($str);
        xmlrpc_setfrompkgslogxmpp( $str,
                                    "PKG",
                                    '',
                                    0,
                                    $_GET['filename'],
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Packaging | Files | Delete | Manual');
    }
    header("Location: " . urlStrRedirect("pkgs/pkgs/edit", array('p_api' => $_GET['p_api'], 'pid' => $_GET['pid'], 'packageUuid' => $_GET['packageUuid'])));
}
if (count($package) == 0) {
    $title = _T("Edit a package", "pkgs");
    $activeItem = "index";
    # get existing package
    $pid = base64_decode($_GET['pid']);
    $package = getPackageDetail($p_api_id, $pid);
    if ($package['do_reboot']) {
        $package['reboot'] = $package['do_reboot'];
    }

    $formElt = new HiddenTpl("id");

    $selectpapi = new HiddenTpl('p_api');
    $p_api_number = count(getUserPackageApi());
} else {
    $formElt = new HiddenTpl("id");
    $selectpapi = new HiddenTpl('p_api');
}

/*
 * Page form
 */

// display an edit package form (description, version, ...)
$f = new ValidatingForm(array("onchange"=>"getJSON()","onclick"=>"getJSON()"));
$f->push(new Table());

$p_api_id = ($_GET['p_api']) ? base64_decode($_GET['p_api']) : base64_decode($_POST['p_api']);
$selectpapi = new HiddenTpl('p_api');

if ($p_api_number > 1) {
    $f->add(
            new TrFormElement(_T("Package API", "pkgs"), $selectpapi), array("value" => $p_api_id, "hide" => $hide)
    );
} else {
    $f->add(
            $selectpapi, array("value" => $p_api_id, "hide" => True)
    );
}

$f->add(new HiddenTpl("id"), array("value" => $package['id'], "hide" => True));

// Uploaded field,
$f->add(new HiddenTpl("files_uploaded"), array("value" => 0, "hide" => True));

if ($_GET["action"] == "add") {
    $f->add(new HiddenTpl("mode"), array("value" => "creation", "hide" => True));
}

$fields = array(
    array("label", _T("Package label", "pkgs"), array("required" => True)),
    array("version", _T("Package version", "pkgs"), array("required" => True)),
    array('description', _T("Description", "pkgs"), array()),
);
if(!isExpertMode())
{

$cmds = array(
    array('command', _T('Command\'s name : ', 'pkgs'), _T('Command : ', 'pkgs')), /*
          array('installInit', _T('installInit', 'pkgs'), _T('Install Init', 'pkgs')),
          array('preCommand', _T('preCommand', 'pkgs'), _T('Pre Command', 'pkgs')),
          array('postCommandFailure', _T('postCommandFailure', 'pkgs'), _T('postCommandFailure', 'pkgs')),
          array('postCommandSuccess', _T('postCommandSuccess', 'pkgs'), _T('postCommandSuccess', 'pkgs')) // */
);

$options = array(
    array('reboot', _T('Need a reboot ?', 'pkgs'))
);

}
$os = array(
    array('win', 'linux', 'mac'),
    array(_T('Windows'), _T('Linux'), _T('Mac OS'))
);

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

if(isExpertMode())
{
  $f->add(new HiddenTpl("metagenerator"), array("value" => "expert", "hide" => True));
}
else {
  $f->add(new HiddenTpl("metagenerator"), array("value" => "standard", "hide" => True));
}

if(isExpertMode())
{
    $json = json_decode(get_xmpp_package($_GET['packageUuid']),true);
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
    $methodtransfer->setElements(['pullcurl','pushrsync']);
    $methodtransfer->setElementsVal(['pullcurl','pushrsync']);
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

    // Get the sorted list of dependencies
    if(isset($json['info']['Dependency']))
    {
        $dependencies = $json['info']['Dependency'];
    }
    else
        $dependencies = [];

    //Get all the dependencies as uuid => name
    $allDependenciesList = [];
    foreach(xmpp_packages_list() as $xmpp_package) {
        if($_GET['packageUuid'] != $xmpp_package['uuid'])
            $allDependenciesList[$xmpp_package['uuid']] = $xmpp_package['name'];
    }

    //Generate the list of not-added dependencies, the sort is not important
    $packagesInOptionNotAdded = '';

    foreach($allDependenciesList as $xmpp_package => $xmpp_name){
        if(!in_array($xmpp_package,$dependencies))
            $packagesInOptionNotAdded .= '<option value="'.$xmpp_package.'">'.$xmpp_name.'</option>';
    }

    //Generate the sorted list of added dependencies
    $packagesInOptionAdded = '';
    foreach($dependencies as $uuid_package){
        if(isset($allDependenciesList[$uuid_package]))
            $packagesInOptionAdded .= '<option value="'.$uuid_package.'">'.$allDependenciesList[$uuid_package].'</option>';
    }

    $f->add(new TrFormElement("Dependencies",new SpanElement('<div id="grouplist">
    <table style="border: none;" cellspacing="0">
        <tr>
            <td style="border: none;">
                <div>
                    <img src="img/common/icn_arrowup.png" alt="|^" id="moveDependencyToUp" onclick="moveToUp()"/><br/>
                    <img src="img/common/icn_arrowdown.png" alt="|v" id="moveDependencyToDown" onclick="moveToDown()"/></a><br/>
                </div>
            </td>
            <td style="border: none;">
                <h3>Added dependencies</h3>
                <div class="list">
                    <select multiple size="13" class="list" name="Dependency" id="addeddependencies">
                    '.$packagesInOptionAdded.'
                    </select>
                </div>
            </td>
            <td style="border: none;">
                <div>
                    <img src="img/common/icn_arrowright.gif" alt="-->" id="moveDependencyToRight" onclick="moveToRight()"/><br/>
                    <img src="img/common/icn_arrowleft.gif" alt="<--" id="moveDependencyToLeft" onclick="moveToLeft()"/></a><br/>
                </div>
            </td>
            <td style="border: none;">
                <div class="list" style="padding-left: 10px;">
                    <h3>Available dependencies</h3>
                    <select multiple size="13" class="list" name="members[]" id="pooldependencies">
                        '.$packagesInOptionNotAdded.'
                    </select>
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
$cssClasses = array();
$params = array();

// Get Papi details
$papi_details = getPApiDetail($p_api_id);
$pserver_base_url = '';
// Very dirty hack: TODO: read conf from package server
if ($papi_details['mountpoint'] == '/package_api_get1')
    $mirror = 'mirror1';
elseif ($papi_details['mountpoint'] == '/appstream')
    $mirror = 'appstream';

$pserver_base_url = $papi_details['protocol'] . '://' . $papi_details['server'] . ':' . $papi_details['port'] . '/' . $mirror . "_files/$pid/";

foreach ($package['files'] as $file) {
    if ($file['name'] == "MD5SUMS" || $file['name'] == "xmppdeploy.json")
        continue;
    $names[] = sprintf('<a href="%s">%s</a>', $pserver_base_url . $file['name'] , $file['name']);
    $params[] = array(
        'p_api' => $_GET['p_api'],
        'pid' => $_GET['pid'],
        'packageUuid' => $_GET['packageUuid'],
        'filename' => $file['name'],
        'delete_file' => 1
    );
    //$sizes[$i] = formatFileSize($sizes[$i]);
    $viewVersionsActions[] = $viewVersionsAction;
    $cssClasses[] = 'file';
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

$m = new MultiFileTpl2('filepackage');
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
if(isExpertMode())
{
    $f->add(new HiddenTpl('saveList'), array('id'=>'saveList','name'=>'saveList',"value" => '', "hide" => True));
    include('addXMPP.php');
}

$f->addValidateButton("bcreate");

$f->display();

?>
