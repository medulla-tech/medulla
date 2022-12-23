<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
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
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");

global $conf;
$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$kb = (isset($_GET['kb'])) ? $_GET['kb'] : "";
$maxperpage = $conf["global"]["maxperpage"];
$gid = (isset($_GET['gid'])) ? $_GET['gid'] : "";
$contains = (isset($_GET['contains'])) ? $_GET['contains'] : "";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$filterCTX = "Microsoft";
$field = "platform";

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filterCTX;
$ctx['field'] = $field;
$ctx['contains'] = $contains;

$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

$uuid = htmlspecialchars($_GET['uuid']);
$ctx['uuid'] = $uuid;

//$uuidCut = substr($uuid, -1);

$entityMachineList = xmlrpc_xmppmaster_get_machines_list($start, $end, $ctx);
$filterGid = array('gid' => $gid);
$groupMachineList = getRestrictedComputersList(0, -1, $filterGid, False);

print_r($groupMachineList);

$count_with_upd = $withUpdArray['nb_element_total'];
$count_without_upd = $withoutUpdArray['nb_element_total'];

if ($uuid == '')
{
    $typeOfDetail = "group";
}
else
{
    $typeOfDetail = "entitie";
}

$withUpd = [];
$withoutUpd = [];

$titles_with = [];
$plateform_with = [];

$titles_without = [];
$plateform_without = [];

$with_Upd = xmlrpc_get_machine_with_update($kb);
$without_Upd = xmlrpc_get_count_machine_as_not_upd($kb);

$unique_with_Upd = array_unique($with_Upd);
$unique_without_Upd = array_unique($without_Upd);

if ($typeOfDetail == "entitie")
{
    $count = $entityMachineList['count'];
    for($i=0; $i < $count; $i++)
    {
        if (in_array($entityMachineList['data']['hostname'][$i], $unique_with_Upd))
        {
            $titles_with[] = $entityMachineList['data']['hostname'][$i];
            $plateform_with[] = $entityMachineList['data']['plateform'][$i];
        }
    }

    for($i=0; $i < $count; $i++)
    {
        if (in_array($entityMachineList['data']['hostname'][$i], $unique_without_Upd))
        {
            $titles_without[] = $entityMachineList['data']['hostname'][$i];
            $plateform_without[] = $entityMachineList['data']['plateform'][$i];
        }
    }
}
    

if ($typeOfDetail == "group")
{
    foreach ($listGroup as $k => $v)
    {
        if (in_array($v[1]['cn'][0], $unique_with_Upd))
        {
            $titles_with[] = $v[1]['cn'][0];
            $plateform_with[] = $v[1]['os'][0];
        }
    }

    foreach ($listGroup as $k => $v)
    {
        if (in_array($v[1]['cn'][0], $unique_without_Upd))
        {
            $titles_without[] = $v[1]['cn'][0];
            $plateform_without[] = $v[1]['os'][0];
        }
    }
}


echo "<h2>Machine without update</h2>";
$n = new OptimizedListInfos($titles_without, _T("Update name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($plateform_without, _T("Plateform", "updates"));

$n->setItemCount($count_count_with);
$n->setNavBar(new AjaxNavBar($count_count_with, $filter));

$n->display();

echo "<h2>Machine with update</h2>";
$w = new OptimizedListInfos($titles_with, _T("Update name", "updates"));
$w->disableFirstColumnActionLink();

$w->addExtraInfo($plateform_with, _T("Plateform", "updates"));

$w->setItemCount($count_without);
$w->setNavBar(new AjaxNavBar($count_without, $filter));

$w->display();
?>
