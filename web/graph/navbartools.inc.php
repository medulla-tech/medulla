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

/* FIXME: the parameters $search and $extra may be no more needed */
function print_nav($curstart, $curend, $items, $search = 0, $extra = "")
{
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
      echo "<li class=\"previousList\"><a href=\"".$_SERVER["SCRIPT_NAME"];
      printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s$extra", $_GET["module"],$_GET["submod"],$_GET["action"],$start, $end, $_GET["filter"]);
      echo "\">"._("Previous")."</a></li>\n";
    }

  if (($curend + 1) >= count($items))
    {
      echo "<li class=\"nextListInactive\">"._("Next")."</li>\n";
    }
  else
    {
      $start = $curend + 1;
      $end = $curend + $max;
      echo "<li class=\"nextList\"><a href=\"".$_SERVER["SCRIPT_NAME"];
      printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s$extra", $_GET["module"],$_GET["submod"],$_GET["action"],$start, $end, $_GET["filter"]);
      echo "\">"._("Next")."</a></li>\n";
    }

  echo "</ul>\n";
}

?>