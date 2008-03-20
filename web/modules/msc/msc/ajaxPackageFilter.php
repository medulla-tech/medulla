<?

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

#require("../../../graph/navbartools.inc.php");
require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");

require_once('../../../modules/msc/includes/qactions.inc.php');
require_once('../../../modules/msc/includes/mirror_api.php');
require_once('../../../modules/msc/includes/machines.inc.php');
require_once('../../../modules/msc/includes/widgets.inc.php');
require_once('../../../modules/msc/includes/utilities.php');
$machine = null;
$group = null;
if ($_GET['uuid']) {
    $machine = getMachine(array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname']), false); // should be changed in uuid
} elseif ($_GET['gid']) {
    require_once("../../../modules/dyngroup/includes/utilities.php");
    require_once("../../../modules/dyngroup/includes/querymanager_xmlrpc.php");
    require_once("../../../modules/dyngroup/includes/xmlrpc.php");
    require_once("../../../modules/dyngroup/includes/dyngroup.php");

    $group = new Group($_GET['gid'], true);
}

require_once("../../../modules/msc/includes/package_api.php");
if ($machine) {
    $label = new RenderedLabel(3, sprintf(_T('These packages can be installed on machine "%s"', 'msc'), $machine->hostname));
} else {
    $label = new RenderedLabel(3, sprintf(_T('These packages can be installed on group "%s"', 'msc'), $group->getName()));
}
$label->display();

$a_packages = array();
$a_pversions = array();
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
if ($machine) {
    $filter['machine'] = $machine->hostname;
    $filter['uuid'] = $machine->uuid;
} else {
    $filter['group'] = $group->id;
}

# TODO : decide what we want to do with groups : do we only get the first machine local packages
foreach (advGetAllPackages($filter, $start, $start + $maxperpage) as $c_package) {
    $package = to_package($c_package[0]);
    $type = $c_package[1];
    $p_api = new ServerAPI($c_package[2]);

    $a_packages[] = $package->label;
    $a_pversions[] = $package->version;
    $a_sizes[] = prettyOctetDisplay($package->size);
    if ($machine) {
        $params[] = array('pid'=>$package->id, 'uuid'=>$machine->uuid, 'hostname'=>$machine->hostname, 'from'=>'base|computers|msctabs|tablogs', 'papi'=>$p_api->toURI());
    } else {
        $params[] = array('pid'=>$package->id, 'gid'=>$group->id, 'from'=>'base|computers|msctabs|tablogs', 'papi'=>$p_api->toURI());
    }
    if ($type==0) {
        $a_css[] = 'primary_list';
    } else {
        $a_css[] = 'secondary_list';
    }
}

$count = advCountAllPackages($filter);

$n = new OptimizedListInfos($a_packages, _T("Package", "msc"));
$n->addExtraInfo($a_pversions, _T("Version", "msc"));
$n->addExtraInfo($a_sizes, _T("Package size", "msc"));
$n->setCssClasses($a_css);
$n->setParamInfo($params);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter['filter']));
$n->setTableHeaderPadding(1);
$n->start = 0;
$n->end = $count;

$n->addActionItem(new ActionPopupItem(_T("Launch", "msc"), "start_tele_diff", "start", "msc", "base", "computers"));
$n->addActionItem(new ActionPopupItem(_T("Details", "msc"), "package_detail", "detail", "msc", "base", "computers"));

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


