<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<style type="text/css">
<!--

<?php
require("modules/base/graph/users/index.css");
require("modules/base/includes/users.inc.php");

?>

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Users"),
                    "link" => "main.php?module=base&submod=users&action=index"),
              array("name" => _("List")));

require("localSidebar.php");

require("graph/navbar.inc.php");

if (isset($_POST["filter"])) $_GET["filter"] = $_POST["filter"];

if (!isset($_GET["items"]))
{
  $users = get_users_detailed($error, $_GET["filter"]);
  $start = 0;

  if (count($users) > 0)
    {
      $end = $conf["global"]["maxperpage"] - 1;
    }
  else
    {
      $end = 0;
    }
}
else
{
  $users = unserialize(base64_decode(urldecode($_GET["items"])));
}

if (isset($_GET["start"]))
{
$start = $_GET["start"];
$end = $_GET["end"];
}

if (!$users) {
$start = 0;
$end = 0;
}

if (isset($_POST["filter"])) {
$start = 0;
$end = 9;
}

setVar('start',$start);
setVar('end',$end);
setVar('stop',$stop);
setVar('users',$users);

renderTPL("index");

?>


