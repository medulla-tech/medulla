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

#require("../../../graph/navbartools.inc.php");
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
require_once("../../../modules/dyngroup/includes/utilities.php");
require_once("../../../modules/dyngroup/includes/querymanager_xmlrpc.php");
require_once("../../../modules/dyngroup/includes/xmlrpc.php");
require_once("../../../modules/dyngroup/includes/request.php");
require("../../../modules/dyngroup/includes/dyngroup.php");



$onames = array();
if (!$_GET["start"]) { $_GET["start"] = 0; }
if (!$_GET["end"]) { $_GET["end"] = 10; }

$filter = $_GET["filter"];
if ($_GET['location']) {
    $filter['location'] = $_GET['location'];
}
$gid = $_GET['gid'];

$group = getGroupById($gid);

if ($group->isDyn()) {
    if (!$group->isRequest()) { # dynamic group with static results
        displayStatic($group, $_GET["start"], $_GET["end"], $filter, $gid);
    } else { # dynamic gropu with dynamic results
        $res = $group->reply($_GET["start"], $_GET["end"], $filter);
        $len = $group->countReply($filter);
        display($res, $len, $group, $_GET["start"], $_GET["end"], $filter, $gid);
    }
} else { # static group with static result
    displayStatic($group, $_GET["start"], $_GET["end"], $filter, $gid);
}


function displayStatic($group, $start, $end, $filter, $gid) {
    $res = $group->getResult($start, $end, $filter);
    $len = $group->countResult($filter);
    display($res, $len, $group, $start, $end, $filter, $gid, true);
}

function display($res, $len, $group, $start, $end, $filter, $gid, $canbedeleted = false) {
    foreach ($res as $host) {
        $hostname = $host['hostname'];
        $uuid = $host['uuid'];
        $p = $default_params;
        $p['delete'] = $hostname;
        $p['hostname'] = $hostname;
        $p['uuid'] = $uuid;
        $p['inventaire'] = $hostname;
        $comp = getComputer(array('uuid'=>$uuid));
        if ($comp) {
            $p['comment'] = $comp[1]['displayName'][0];
        }
        $parameters[$hostname] = $p;
    }
    
    list_computers($parameters, $filter, $len, false, $canbedeleted);
    print "<br/>";
}

?>
