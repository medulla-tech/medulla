<?
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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

require("../../../graph/navbartools.inc.php");
require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
# TODO warn : if the module is not installed ...
require("../../../modules/inventory/includes/xmlrpc.php");
require("../../../modules/glpi/includes/xmlrpc.php");
#require("../../../modules/msc/includes/xmlrpc.php");
######
require("../../../modules/base/includes/computers.inc.php");
require("../../../modules/base/includes/computers_list.inc.php");
require_once("../../../modules/dyngroup/includes/data_access.php");
require_once("../../../modules/dyngroup/includes/utilities.php");
require_once("../../../modules/dyngroup/includes/xmlrpc.php");
require_once("../../../modules/dyngroup/includes/request.php");
require_once("../../../modules/dyngroup/includes/result.php");
require("../../../modules/dyngroup/includes/dyngroup.php");


$onames = array();
if (!$_GET["start"]) { $_GET["start"] = 0; }
if (!$_GET["end"]) { $_GET["end"] = 10; }

$filter = $_GET["filter"];
if ($_GET['location']) {
    $filter['location'] = $_GET['location'];
}
$gid = $_GET['gid'];

$group = getStagroupById($gid);
$res = new Result();
$res->parse($group->getResult());
$names = $res->toA($filter, $_GET["start"], $_GET["end"]);
$count = count($res->toA($filter));

foreach ($names as $name) {
    $computer = getComputer(array('hostname'=>$name));
    $computer = $computer[1];
    
    $comment = $computer['displayName'][0];
    $uuid = $computer['objectUUID'][0];
    $onames[$name] = array('comment'=>$comment, 'uuid'=>$uuid, 'name'=>$name, 'gid'=>$gid);
}

list_computers($onames, array('name' => $filter), $count, true, true);

?>
