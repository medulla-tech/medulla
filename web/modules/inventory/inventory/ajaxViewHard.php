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
$uniq = array('Bios', 'Hardware');

$filter = $_GET["filter"];
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

$n = null;
$result = array();
$headers = array('Machine');
$types = array();
foreach ($uniq as $display) {
    $machines = getLastMachineInventoryPart($display, array('gid'=>$_GET["gid"], 'uuid'=>$_GET['uuid'], 'filter'=>$filter, 'min'=>$start, 'max'=>($start + $maxperpage)));
    $count = countLastMachineInventoryPart($display, array('gid'=>$_GET["gid"], 'uuid'=>$_GET['uuid'], 'filter'=>$filter));

    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($display));
    $graph = getInventoryGraph($display);
    foreach ($machines as $machine) {
        $name = $machine[0];
        $uuid = $machine[2];
        if (count($machine[1]) == 0) {
            $result[$name]['Machine'] = $name;
            $result[$name]['uuid'] = $uuid;
        }   
        foreach ($machine[1] as $element) {
            $result[$name]['Machine'] = $name;
            $result[$name]['uuid'] = $uuid;
            foreach ($element as $head => $val) {
                if (!in_array($head, $disabled_columns) && $head != 'id' && $head != 'timestamp') {
                    if (!in_array($head, $headers)) {
                        $headers[]= $head;
                        $types[$head] = $display;
                    }
                    $result[$name][$head] = $val;
                }   
            }   
        }   
    }   
}
$sorted_result = array();
$params = array();
foreach ($result as $name => $val) {
    foreach ($headers as $head) {
        if (!is_array($sorted_result[$head])) {
            $sorted_result[$head] = array();
        }
        if ($val[$head]) {
            $sorted_result[$head][]= $val[$head];
        } else {
            $sorted_result[$head][]= "";
        }
    }
    $params[] = array('hostname'=>$val['Machine'], 'uuid'=>$val['uuid']);
}
foreach ($sorted_result as $head => $vals) {
    if (in_array($head, $graph)) {
        $type = ucfirst($types[$head]);
        $nhead = "$head <a href='main.php?module=inventory&submod=inventory&action=graphs&type=$type&field=$head";
        foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab') as $get) {
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
        
$n->addActionItem(new ActionItem(_T("View", "inventory"),"invtabs","voir","inventory", "base", "computers"));
#$n->addActionItem(new ActionPopupItem(_T("Informations"),"infos","infos","inventaire"));
$n->setParamInfo($params);
if ($n != null) {
    $n->setTableHeaderPadding(1);
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->start = 0;
    $n->end = $maxperpage;
    $n->display();
}

?><a href='<?= urlStr("inventory/inventory/csv", array('table'=>implode('|', $uniq), 'gid'=>$_GET["gid"])) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a>


</table>

