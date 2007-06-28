<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
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

function print_ajax_nav($curstart, $curend, $items, $filter)
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
      echo "<li class=\"previousList\"><a href=\"#\" onClick=\"updateSearchGroupParam('$filter','$start','$end'); return false\";>"._("Previous")."</a></li>\n";
    }

  if (($curend + 1) >= count($items))
    {
      echo "<li class=\"nextListInactive\">"._("Next")."</li>\n";
    }
  else
    {
      $start = $curend + 1;
      $end = $curend + $max;


      echo "<li class=\"nextList\"><a href=\"#\" onClick=\"updateSearchGroupParam('$filter','$start','$end'); return false\";>"._("Next")."</a></li>\n";
    }

  echo "</ul>\n";
}

require("modules/base/includes/groups.inc.php");

$filter=$_GET["filter"];

$groups = search_groups($filter);
$start = 0;

if (count($groups) > 0)
{
  $end = $conf["global"]["maxperpage"] - 1;
}
else
{
  $end = 0;
}

if (isset($_GET["start"]))
{
    $start = $_GET["start"];
    $end = $_GET["end"];
}


?>


<?php
print_ajax_nav($start, $end, $groups,$filter);

$arrGroup = array();
$arrComment = array();

for ($idx = 0; $idx < count($groups); $idx++) {
    $arrGroup[] = $groups[$idx][0];
    $arrComment[] = $groups[$idx][1];
    $arrNb[] = '<span style="font-weight: normal;">('.$groups[$idx][2].')</span>';
}


$n = new ListInfos($arrGroup,_("Groups"));
$n->setCssClass("groupName");
$n->addExtraInfo($arrComment,_("Comments"));
$n->setAdditionalInfo($arrNb);
$n->addActionItem(new ActionItem(_("Edit members"),"members","afficher","group") );
$n->addActionItem(new ActionItem(_("Edit group"),"edit", "edit","group") );
$n->addActionItem(new ActionPopupItem(_("Delete"),"delete","supprimer","group") );
$n->setName(_("Groups management"));
$n->display(0);

print_ajax_nav($start, $end, $groups,$filter);
?>