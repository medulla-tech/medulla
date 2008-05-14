<?
/**
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

require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");

require_once("../../../modules/inventory/includes/xmlrpc.php");
require_once("../../../modules/base/includes/edit.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"];
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

if ($_GET['uuid'] != '') {
    $table = $_GET['part'];
    $inv = getLastMachineInventoryPart($table, array('uuid'=>$_GET["uuid"], 'filter'=>$filter, 'min'=>$start, 'max'=>($start + $maxperpage)));
    $count = countLastMachineInventoryPart($table, array('uuid'=>$_GET["uuid"], 'filter'=>$filter));
    
    /* display everything else in separated tables */
    $n = null;
    $h = array();
    $index = 0;
    foreach ($inv[0][1] as $def) {
        foreach ($def as $k => $v) {
            $h[$k][$index] = $v;
        }
        $index+=1;
    }
    $max = 0;
    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($table));
    foreach ($h as $k => $v) {
        
        if ($k != 'id' && $k != 'timestamp' && !in_array($k, $disabled_columns)) {
            if ($n == null) {
                $n = new OptimizedListInfos($h[$k], $k);
            } else {
                $n->addExtraInfo($h[$k], $k);
            }
            if (count($h[$k]) > $max) { $max = count($h[$k]); }
        }
    }
    if ($n != null) {
        $n->setTableHeaderPadding(1);
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $maxperpage;
        $n->display();
    }
    ?><a href='<?= urlStr("inventory/inventory/csv", array('table'=>$table, 'uuid'=>$_GET["uuid"])) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a><?php
} else {
    $display = $_GET['part'];
    $machines = getLastMachineInventoryPart($display, array('gid'=>$_GET["gid"], 'filter'=>$filter, 'min'=>$start, 'max'=>($start + $maxperpage)));
    $count = countLastMachineInventoryPart($display, array('gid'=>$_GET["gid"], 'filter'=>$filter));

    $result = array();
    $index = 0;
    foreach ($machines as $machine) {
        $name = $machine[0];
        if (count($machine[1]) == 0) {
            $result['Machine'][$index] = $name;
            $index += 1;
        }
        foreach ($machine[1] as $element) {
            $result['Machine'][$index] = $name;
            foreach ($element as $head => $val) {
                if ($head != 'id' && $head != 'timestamp') {
                    $result[$head][$index] = $val;
                }
            }
            $index += 1;
        }
    }
    $n = null;
    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($display));
    $graph = getInventoryGraph($display);
    foreach ($result as $head => $vals) {
        if (!in_array($head, $disabled_columns)) {
            if (in_array($head, $graph)) {
                $type = ucfirst($_GET['part']);
                $nhead = "$head <a href='main.php?module=inventory&submod=inventory&action=graphs&type=$type&field=$head";
                foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
                    $nhead .= "&$get=".$_GET[$get];
                }
                $nhead .= "' alt='graph'><img src='modules/inventory/img/graph.png'/></a>";
                $head = $nhead;
            }
            if ($n == null) {
                $n = new OptimizedListInfos($vals, $head);
            } else {
                $n->addExtraInfo($vals, $head);
            }
        }
    }

    if ($n != null) {
        $n->addActionItem(new ActionItem(_T("View"),"view","voir","inventaire", "inventory"));
        $n->addActionItem(new ActionPopupItem(_T("Informations"),"infos","infos","inventaire", "inventory"));
        $n->disableFirstColumnActionLink();
        $n->setTableHeaderPadding(1);
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $maxperpage;
        $n->display();
    }
    ?><a href='<?= urlStr("inventory/inventory/csv", array('table'=>$display, 'gid'=>$_GET["gid"])) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a><?php
}

?>

</table>

