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

$filter = array('filter'=> $_GET["filter"], 'gid'=> $_GET['gid']);
if ($_GET['location']) {
    $filter['location'] = $_GET['location'];
}

$names = array_map("join_value", array_values(getRestrictedComputersList($_GET["start"], $_GET["end"], $filter)));
$count = getComputerCount($filter);

$canbedeleted = true;
$group = getGroupById($_GET['gid']);
if ($group->isDyn() && $group->isRequest()) {
    $canbedeleted = false;
}

list_computers($names, $filter, $count, false, $canbedeleted);

function join_value($n) {
    $ret = array();
    foreach ($n[1] as $k=>$v) {
        if (is_array($v)) {
            $ret[$k] = join(", ", $v);
        } else {
            $ret[$k] = $v;
        }
    }
    return $ret;
}

?>
