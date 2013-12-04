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

$group = null;
if (!empty($_GET['gid'])) {
    require_once("modules/dyngroup/includes/utilities.php");
    require_once("modules/dyngroup/includes/querymanager_xmlrpc.php");
    require_once("modules/dyngroup/includes/xmlrpc.php");
    require_once("modules/dyngroup/includes/dyngroup.php");

    $group = new Group($_GET['gid'], true);
}

require_once("modules/msc/includes/package_api.php");
if ($_GET['uuid']) {
    $label = new RenderedLabel(3, sprintf(_T('These packages can be installed on computer "%s"', 'msc'), $_GET['hostname']));
} else {
    $label = new RenderedLabel(3, sprintf(_T('These packages can be installed on group "%s"', 'msc'), $group->getName()));
}
$label->display();

function getConvergenceStatus($mountpoint, $pid, $group_convergence_status) {
    $return = 0;
    if (array_key_exists($mountpoint, $group_convergence_status)) {
        if (array_key_exists($pid, $group_convergence_status[$mountpoint])) {
            if ($group_convergence_status[$mountpoint][$pid]) {
                $return = 1;
            }
            else {
                $return = 2;
            }
        }
    }
    return $return;
}

function prettyConvergenceStatusDisplay($status) {
    switch ($status) {
        case 0:
            return _T('Available', 'msc');
        case 1:
            return _T('Active', 'msc');
        case 2:
            return _T('Inactive', 'msc');
        default:
            return _T('Not available', 'msc');
    }
}

$group_convergence_status = xmlrpc_getConvergenceStatus($group->id);

$a_packages = array();
$a_description = array();
$a_pversions = array();
$a_sizes = array();
$a_convergence_status = array();
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
list($count, $packages) = advGetAllPackages($filter, $start, $start + $maxperpage);
$err = array();
foreach ($packages as $c_package) {
    $package = to_package($c_package[0]);
    $type = $c_package[1];
    $p_api = new ServerAPI($c_package[2]);

    if ($c_package[0]['ERR'] && $c_package[0]['ERR'] == 'PULSE2ERROR_GETALLPACKAGE') {
        $err[] = sprintf(_T("MMC failed to contact package server %s.", "msc"), $c_package[0]['mirror']);
    } else {
        $a_packages[] = $package->label;
        $a_description[] = $package->description;
        $a_pversions[] = $package->version;
        $a_sizes[] = prettyOctetDisplay($package->size);
        $current_convergence_status = getConvergenceStatus($p_api->mountpoint, $package->id, $group_convergence_status);
        // set param_convergence_edit to True if convergence status is active or inactive
        $param_convergence_edit = (in_array($current_convergence_status, array(1, 2))) ? True : False;
        $a_convergence_status[] = prettyConvergenceStatusDisplay($current_convergence_status);
        if (!empty($_GET['uuid'])) {
            $params[] = array('name' => $package->label, 'version' => $package->version, 'pid' => $package->id, 'uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'from' => 'base|computers|msctabs|tablogs', 'papi' => $p_api->toURI());
        } else {
            $params[] = array('name' => $package->label, 'version' => $package->version, 'pid' => $package->id, 'gid' => $group->id, 'from' => 'base|computers|msctabs|tablogs', 'papi' => $p_api->toURI(), 'editConvergence' => $param_convergence_edit);
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

$n = new OptimizedListInfos($a_packages, _T("Package", "msc"));
$n->addExtraInfo($a_description, _T("Description", "msc"));
$n->addExtraInfo($a_pversions, _T("Version", "msc"));
$n->addExtraInfo($a_sizes, _T("Package size", "msc"));
$n->addExtraInfo($a_convergence_status, _T("Convergence", "msc"));
$n->setCssClasses($a_css);
$n->setParamInfo($params);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter['filter']));
$n->setTableHeaderPadding(1);
$n->disableFirstColumnActionLink();
$n->start = 0;
$n->end = $count;

$n->addActionItem(new ActionItem(_T("Advanced launch", "msc"), "start_adv_command", "advanced", "msc", "base", "computers"));
$n->addActionItem(new ActionItem(_T("Direct launch", "msc"), "start_command", "start", "msc", "base", "computers"));
$n->addActionItem(new ActionItem(_T("Convergence", "msc"), "convergence", "convergence", "msc", "base", "computers"));
//$n->addActionItem(new ActionPopupItem(_T("Details", "msc"), "package_detail", "detail", "msc", "base", "computers"));

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
    li.advanced a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/run.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
    }

li.convergence a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/convergence.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

</style>


