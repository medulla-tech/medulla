<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
require_once("modules/base/includes/computers.inc.php");
require_once("modules/base/includes/computers_list.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$canbedeletedfromgroup = null;
$canbedeleted = true;
$is_group = false;

$filter = array('hostname' => $_GET["filter"]);
if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}
if (isset($_GET['location'])) {
    $filter['location'] = $_GET['location'];
    if (!empty($_GET['gid'])) {
        $_SESSION['computers.selected_location.' . $_GET['gid']] = $_GET['location'];
    } else {
        $_SESSION['computers.selected_location'] = $_GET['location'];
    }
}
if (isset($_SESSION['request'])) {
    $filter['request'] = $_SESSION['request'];
}
if (isset($_GET['equ_bool'])) {
    $filter['equ_bool'] = $_GET['equ_bool'];
}
if (isset($_GET['imaging_server'])) {
    $filter['imaging_server'] = $_GET['imaging_server'];
}

if (in_array("dyngroup", $_SESSION["modulesList"])) {
    require_once("modules/pulse2/includes/groups_xmlrpc.inc.php");
    require_once("modules/dyngroup/includes/dyngroup.php");
    if (isset($_GET['gid'])) {
        $filter['gid'] = $_GET['gid'];
        $canbedeletedfromgroup = true;
        $canbedeleted = false;
        $is_group = true;
        if (isrequest_group($_GET['gid'])) {
            $canbedeletedfromgroup = false;
        }
    }
}
$cl = getRestrictedComputersList($start, $start + $maxperpage, $filter, False);
$cl1 = array();
foreach ($cl as $k => $v) {
    $cl1[$v[1]['cn'][0] . $k] = $k;
}
$names = array();

function my_cmp($a, $b) {
    return strcmp(strtolower($a), strtolower($b));
}

uksort($cl1, "my_cmp");
foreach ($cl1 as $k1 => $k) {
    $names[] = join_value($cl[$k]);
}
$count = getComputerCount($filter);

/* Check:
 *   - if MSC is configured with file download capability
 *   - if MSC is configured with VNC client capability
 * */
$msc_can_download_file = False;
$msc_vnc_show_icon = False;
if (in_array("msc", $_SESSION["supportModList"])) {
    require_once("modules/msc/includes/scheduler_xmlrpc.php");
    require_once("modules/msc/includes/mscoptions_xmlrpc.php");
    $msc_can_download_file = msc_can_download_file();
    $msc_vnc_show_icon = web_vnc_show_icon();
}
list_computers($names, $filter, $count, $canbedeleted, $canbedeletedfromgroup, $is_group, $msc_can_download_file, $msc_vnc_show_icon);

function join_value($n) {
    $ret = array();
    foreach ($n[1] as $k => $v) {
        if (is_array($v)) {
            $ret[$k] = join(", ", $v);
        } else {
            $ret[$k] = $v;
        }
    }
    return $ret;
}

if (in_array("dyngroup", $_SESSION["modulesList"]) and isset($_GET['gid'])) {
    ?><a href='<?php echo urlStr("base/computers/csv", array('gid' => $_GET['gid'], 'location' => $_GET['location'], 'groupname' => $_GET['groupname'])) ?>'><img src='modules/pulse2/graph/csv.png' alt='export csv'/></a><?php
}
?>

<style type="text/css">
    td:hover {
        cursor:pointer;
    }
</style>
<script type="text/javascript">
    jQuery('tbody tr td:not(.action)').click(function() {
        jQuery('#param').val(jQuery(this).text().replace(/&nbsp;/g, ' '));
        pushSearch();
    });

// Detecting Java Runtime version for VNC Applet

    function JavaVersion()
    {

        if (deployJava.versionCheck("1.6.0+"))
            return deployJava.versionCheck("1.6.0+");
        return null;
    }

// Setting a cookie for Java Version
    document.cookie = "javaenabled=" + JavaVersion();

</script>
