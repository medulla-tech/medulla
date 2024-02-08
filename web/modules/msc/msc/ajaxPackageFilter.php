<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/mirror_api.php');
require_once('modules/msc/includes/machines.inc.php');
require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/utilities.php');
require_once("includes/xmlrpc.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");

$group = null;
if (!empty($_GET['gid'])) {
    require_once("modules/dyngroup/includes/utilities.php");
    require_once("modules/dyngroup/includes/querymanager_xmlrpc.php");
    require_once("modules/dyngroup/includes/xmlrpc.php");
    require_once("modules/dyngroup/includes/dyngroup.php");

    $group = new Group($_GET['gid'], true);
}

require_once("modules/msc/includes/package_api.php");
if (! in_array("xmppmaster", $_SESSION["supportModList"])) {
    if ($_GET['uuid']) {
        $label = new RenderedLabel(3, sprintf(_T('These packages can be installed on computer "%s"', 'msc'), $_GET['hostname']));
    } else {
        $label = new RenderedLabel(3, sprintf(_T('These packages can be installed on group "%s"', 'msc'), $group->getName()));
    }
    $label->display();
}

function getConvergenceStatus($mountpoint, $pid, $group_convergence_status, $associateinventory) {
    $ret = 0;
    if ($associateinventory) {
        if (array_key_exists($pid, $group_convergence_status)) {
            if ($group_convergence_status[$pid] == 0)
                $ret = 2;
            else
                $ret = 1;
        }
    }
    else {
        $ret = 3;
    }
    return $ret;
}

function prettyConvergenceStatusDisplay($status) {
    switch ($status) {
        case 0:
            return _T('Available', 'msc');
        case 1:
            return _T('Active', 'msc');
        case 2:
            return _T('Inactive', 'msc');
        case 3:
        default:
            return _T('Not available', 'msc');
    }
}
$a_convergence_status = array();
if ($group != null) {
    $group_convergence_status = xmlrpc_getConvergenceStatus($group->id);
    $group_convergence_status1 = $group_convergence_status['/package_api_get1'] ?? [];
}
$emptyAction = new EmptyActionItem();
$convergenceAction = new ActionItem(_T("Convergence", "msc"), "convergence", "convergence", "msc", "base", "computers");
$a_convergence_action = array();
$a_packages = array();
$a_description = array();
$a_pversions = array();
$a_sizes = array();
$a_css = array();
$params = array();

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

$filter['filter'] = $_GET["filter"];
if (!empty($_GET['uuid'])) {
    $filter['machine'] = $_GET['hostname'];
    $filter['uuid'] = $_GET['uuid'];
} else {
    $filter['group'] = $group->id;
}

# TODO : decide what we want to do with groups : do we only get the first machine local packages
//list($count, $packages) = advGetAllPackages($filter, $start, $start + $maxperpage);
if (isset($_GET['uuid'])){
    $platform = xmlrpc_getMachinefromuuid($_GET['uuid'])['platform'];
    if ( stripos($platform, "win") !== false) {
        $filter['filter1'] = "win";
    }elseif( stripos($platform, "linux") !== false){
        $filter['filter1'] = "linux";
    }elseif( stripos($platform, "darwin") !== false){
        $filter['filter1'] = "darwin";
    }
};
list($count, $packages) =  get_all_packages_deploy($_SESSION['login'], $start,  $start + $maxperpage, $filter);

// list($count, $packages) =  xmlrpc_xmppGetAllPackages($filter, $start, $start + $maxperpage);
$packages[0][1] = 0;
$packages[0][2] = array();
$packages[0][2]["mountpoint"] = "/package_api_get1";
$packages[0][2]["server"] = "localhost";
$packages[0][2]["protocol"] = "https";
$packages[0][2]["uuid"] = "UUID/package_api_get1";
$packages[0][2]["port"] = 9990;
$err = array();
foreach ($packages as $c_package) {
    $elt_convergence_status = "";
    $current_convergence_status = 0;
    $package = isset($c_package[0]) ? to_package($c_package[0]) : null;

    $type = isset($c_package[1]) ? $c_package[1] : 0;

    $p_api = (isset($c_package[2])) ? new ServerAPI($c_package[2]) : new ServerAPI();
    if (isset($c_package[0]['ERR']) && $c_package[0]['ERR'] == 'PULSE2ERROR_GETALLPACKAGE') {
        $err[] = sprintf(_T("MMC failed to contact package server %s.", "msc"), $c_package[0]['mirror']);
    } else {
      if($package != null)
      {
        $a_packages[] = $package->label;
        $a_description[] = $package->description ;
        $a_pversions[] = $package->version ;
        $a_pos[] = $package->targetos ;
        $a_sizes[] = prettyOctetDisplay($package->size);

        if ($group != null) {
            $current_convergence_status = ($package != null) ? getConvergenceStatus(0,
                                                               $package->id,
                                                               $group_convergence_status1,
                                                               $package->associateinventory) : null;
            // set param_convergence_edit to True if convergence status is active or inactive
            $param_convergence_edit = (in_array($current_convergence_status, array(1, 2))) ? True : False;
            $elt_convergence_status = prettyConvergenceStatusDisplay($current_convergence_status);
            $a_convergence_status[] = $elt_convergence_status;
            $a_convergence_action[] = (isset($package->associateinventory) && $package->associateinventory == 1) ? $convergenceAction : $emptyAction;
        }
      }

        if($package == null){

        }
        else if (!empty($_GET['uuid'])) {
            $params[] = array('name' => $package->label,
                              'version' => $package->version,
                              'pid' => $package->id,
                              'uuid' => $_GET['uuid'],
                              'hostname' => $_GET['hostname'],
                              'from' => 'base|computers|msctabs|tablogs',
                              'papi' => $p_api->toURI(),
                              'actionconvergence' => $elt_convergence_status,
                              'actionconvergenceint' => $current_convergence_status);
        } else {
            $params[] = array('name' => $package->label,
                              'version' => $package->version,
                              'pid' => $package->id,
                              'gid' => $group->id,
                              'from' => 'base|computers|groupmsctabs|tablogs',
                              'papi' => $p_api->toURI(),
                              'editConvergence' => $param_convergence_edit,
                              'actionconvergence' => $elt_convergence_status,
                              'actionconvergenceint' => $current_convergence_status);
        }
        if ($type == 0) {
            $a_css[] = 'primary_list';
        } else {
            $a_css[] = 'secondary_list';
        }
    }
}
if ($err) {
    new NotifyWidgetFailure(implode('<br/>', array_merge($err, array(_T("Please contact your administrator.", "msc")))));
}

// Avoiding the CSS selector (tr id) to start with a number
$ids_deploy = [];
foreach($params as $pid_pkgs){
    $ids_deploy[] = 'p_'.$pid_pkgs['pid'];
}

$n = new OptimizedListInfos($a_packages, _T("Package", "msc"));
$n->setcssIds($ids_deploy);
$n->addExtraInfo($a_description, _T("Description", "msc"));
$n->addExtraInfo($a_pversions, _T("Version", "msc"));
$n->addExtraInfo($a_sizes, _T("Package size", "msc"));
if ($group != null) {
    $n->addExtraInfo($a_convergence_status, _T("Convergence", "msc"));
}
$n->setCssClasses($a_css);
$n->setParamInfo($params);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter['filter']));
$n->setTableHeaderPadding(1);
$n->disableFirstColumnActionLink();
$n->start = 0;
$n->end = $count;

$presencemachinexmpp = (isset($_GET['uuid'])) ? xmlrpc_getPresenceuuid( $_GET['uuid']) : 0;

if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
    $n->addActionItem(new ActionItem(_T("Advanced launch", "msc"), "start_adv_command", "advanced", "msc", "base", "computers"));
    $n->addActionItem(new ActionItem(_T("Direct launch", "msc"), "start_command", "start", "msc", "base", "computers"));
}
else{
    $n->addActionItem(new ActionItem(_T("Advanced launch", "msc"), "start_adv_command", "advanced", "msc", "base", "computers"));
    if ( $presencemachinexmpp || isset($_GET['gid']))
        $n->addActionItem(new ActionItem(_T("Direct launch", "msc"), "start_command", "start", "msc", "base", "computers"));
}

if ($group != null) {
    $n->addActionItem($a_convergence_action);
}

$n->display();
?>
<style>
    .primary_list { }
    .secondary_list {
        background-color: #e1e5e6 !important;
    }
    li.detail a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/info.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
    }

</style>
