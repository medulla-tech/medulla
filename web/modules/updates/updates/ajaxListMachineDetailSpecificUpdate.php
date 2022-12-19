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
$maxperpage = $conf["global"]["maxperpage"];
$gid = (isset($_GET['gid'])) ? $_GET['gid'] : "";
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filter;
$ctx['field'] = $field;
$ctx['contains'] = $contains;

$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

$uuid = htmlspecialchars($_GET['uuid']);
$ctx['uuid'] = $uuid;

$uuidCut = substr($uuid, -1);

//$withUpdArray = xmlrpc_get_grey_list($start, $maxperpage, $filter);
//$withoutUpdArray = xmlrpc_get_white_list($start, $maxperpage, $filter);

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

$titles = [];
$complRates = [];
$machineWithUpd = [];
$machineWithoutUpd = [];
$actionDetails = [];

$hostnames = [];
$ids = [];

if ($typeOfDetail == "entitie")
{
    
}
    

if ($typeOfDetail == "group")
{
     
}


// ########## Boucle greyList ########## //
for($i=0; $i < $count_with_upd; $i++)
{

}

for($i=0; $i < $count_without_upd; $i++)
{

}

$n = new OptimizedListInfos($titles, _T("Update name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Plateform", "updates"));

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

$n->addActionItemArray($actionDetails);

$n->display();
?>
