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
<?php

require("modules/base/includes/users.inc.php");

$root = $conf["global"]["root"];
$maxperpage = $conf["global"]["maxperpage"];


require("graph/navbartools.inc.php");
//require("includes/PageGenerator.php");


function
print_ajax_nav($curstart, $curend, $items, $filter)
{
  $_GET["action"] = "index";
  global $conf;

  $max = $conf["global"]["maxperpage"];
  $encitems = urlencode(base64_encode(serialize($items)));

  echo '<form method="post" action="' . $PHP_SELF . '">';
  echo "<ul class=\"navList\">\n";

  if ($curstart == 0)
    {
      echo "<li class=\"previousListInactive\">"._("Previous")."</li>\n";
    }
  else
    {
      $start = $curstart - $max;
      $end = $curstart - 1;
      echo "<li class=\"previousList\"><a href=\"#\" onClick=\"updateSearchUserParam('$filter','$start','$end'); return false\";>"._("Previous")."</a></li>\n";
    }

  if (($curend + 1) >= count($items))
    {
      echo "<li class=\"nextListInactive\">"._("Next")."</li>\n";
    }
  else
    {
      $start = $curend + 1;
      $end = $curend + $max;


      echo "<li class=\"nextList\"><a href=\"#\" onClick=\"updateSearchUserParam('$filter','$start','$end'); return false\";>"._("Next")."</a></li>\n";
    }

  echo "</ul>\n";
}



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


$filter = $_GET["filter"];



print_ajax_nav($start, $end, $users,$filter);

global $maxperpage;

$arrUser = array();
$arrSnUser = array();
$homeDirArr = array();


$css =array();

for ($idx = 0; $idx < count($users); $idx++)
 {
    if ($users[$idx]["enabled"]) {
        $css[$idx] = "userName";
    }  else $css[$idx] = "userNameDisabled";
    $arrUser[]=$users[$idx]['uid'];

    $arrSnUser[]=$users[$idx]['givenName'].' '.$users[$idx]['sn'];;
    $homeDirArr[]=$users[$idx]['homeDirectory'];
}


// $arrUser is the list of all Users
$n = new UserInfos($arrUser,_("Login"));

$n->setCssClass("userName");

$n->css = $css;

$n->addExtraInfo($arrSnUser,_("Name"));

//add a list with all homeDir
$n->addExtraInfo($homeDirArr,_("Home directory"));

$n->addActionItem(new ActionItem(_("Edit"),"edit","edit","user") );
//
$n->addActionItem(new ActionItem(_("LMC rights"),"editacl","editacl","user") );
$n->addActionItem(new ActionPopupItem(_("Delete"),"delete","supprimer","user") );
$n->addActionItem(new ActionPopupItem(_("Backup"),"backup","archiver","user") );

$n->setName(_("Users"));
$n->display(0);

?>
</table>
<?php
print_ajax_nav($start, $end, $users,$filter);
?>