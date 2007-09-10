<?php
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
?>
<?php

require("modules/base/includes/users.inc.php");

global $conf;
$root = $conf["global"]["root"];
$maxperpage = $conf["global"]["maxperpage"];

require("graph/navbartools.inc.php");

function print_ajax_nav($curstart, $curend, $totalcount, $items, $filter) {
  $_GET["action"] = "index";
  global $conf;

  $max = $conf["global"]["maxperpage"];

  echo '<form method="post" action="' . $PHP_SELF . '">';
  echo "<ul class=\"navList\">\n";

  if ($curstart == 0) {
      echo "<li class=\"previousListInactive\">"._("Previous")."</li>\n";
  } else {
      $start = $curstart - $max;
      $end = $curstart - 1;
      echo "<li class=\"previousList\"><a href=\"#\"
          onClick=\"updateSearchUserParam('$filter','$start','$end');
          return false\";>"._("Previous")."</a></li>\n";
  }

  if (($curend + 1) >= $totalcount) {
      echo "<li class=\"nextListInactive\">"._("Next")."</li>\n";
  } else {
      $start = $curend + 1;
      $end = $curend + $max;

      echo "<li class=\"nextList\"><a href=\"#\"
           onClick=\"updateSearchUserParam('$filter','$start','$end');
           return false\";>"._("Next")."</a></li>\n";
  }

  echo "</ul>\n";
}



if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;
if (isset($_GET["end"])) $end = $_GET["end"];
else $end = 0;

$filter = $_GET["filter"];

list($usercount, $users) = get_users_detailed($error, $filter, $start, $start + $maxperpage);

if (!$usercount) {
    $start = 0;
    $end = 0;
}

if (($usercount > 0) && ($end == 0)) {
    $end = $maxperpage - 1;
} 

print_ajax_nav($start, $end, $usercount, $users, $filter);

$arrUser = array();
$arrSnUser = array();
$homeDirArr = array();
$mails = array();
$phones = array();
$css = array();

for ($idx = 0; $idx < count($users); $idx++) {
    if ($users[$idx]["enabled"]) {
        $css[$idx] = "userName";
    } else $css[$idx] = "userNameDisabled";
    $arrUser[]=$users[$idx]['uid'];

    $arrSnUser[]=$users[$idx]['givenName'].' '.$users[$idx]['sn'];;

    if (strlen($users[$idx]["mail"]) > 0) {
        $mails[] = '<a href="mailto:' . $users[$idx]["mail"] . '">' . $users[$idx]["mail"] . "</a>";
    } else {
        $mails[] = $users[$idx]["mail"];
    }
    /* We display the smallest telephone number, hopefully it is the user phone extension */
    $num = null;
    foreach($users[$idx]["telephoneNumber"] as $number) {
        if ($num == null) $num = $number;
        else if (strlen($number) < strlen($num)) $num = $number;
    }
    $phones[] = $num;
}

// $arrUser is the list of all Users
$n = new UserInfos($arrUser, _("Login"));
$n->setItemCount($usercount);
$n->start = 0;
$n->end = count($users) - 1;

$n->setCssClass("userName");

$n->css = $css;

$n->addExtraInfo($arrSnUser,_("Name"));
$n->addExtraInfo($mails,_("Mail"));
$n->addExtraInfo($phones,_("Telephone"));

$n->addActionItem(new ActionItem(_("Edit"),"edit","edit","user"));
$n->addActionItem(new ActionItem(_("MMC rights"),"editacl","editacl","user") );
$n->addActionItem(new ActionPopupItem(_("Delete"),"delete","supprimer","user") );
$n->addActionItem(new ActionPopupItem(_("Backup"),"backup","archiver","user") );

$n->setName(_("Users"));
$n->display(0);

?>
</table>
<?php
print_ajax_nav($start, $end, $usercount, $users, $filter);
?>
