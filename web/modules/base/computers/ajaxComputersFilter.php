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

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = array('hostname'=> $_GET["filter"]);
if ($_GET['location']) {
    $filter['location'] = $_GET['location'];
}
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

$names = array();
foreach (getRestrictedComputersList($start, $start + $maxperpage, $filter) as $dn => $entry) {
    $name = $entry[1]["cn"][0];
    $comment = $entry[1]["displayName"][0];
    $uuid = $entry[1]["objectUUID"][0];
    $names[$name] = array('comment'=>$comment, 'uuid'=>$uuid, 'hostname'=>$name);
}

$count = getComputerCount($filter);
list_computers($names, $filter, $count, true);

?>
