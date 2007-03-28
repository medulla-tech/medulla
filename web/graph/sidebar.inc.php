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
/* $Id$ */

?>

<div id="help">
    help here
</div>

<div id="sidebar">
<?php
echo "<ul class=\"".$sidebar["class"]."\">\n";

foreach ($sidebar["content"] as $item)
{
  //verify acl before echoing
  $arrUrl = parse_url($item["link"]);
  foreach (split('&amp;',$arrUrl["query"]) as $arg) {
    list($key,$value) = split('=',$arg);
    //storing arg in an array
    $arrArg[$key]=$value;
  }
  if (hasCorrectAcl($arrArg["module"],$arrArg["submod"],$arrArg["action"])) {
    echo "<li id=\"".$item["id"]."\">";
    echo "<a href=\"".$root.$item["link"]."\" target=\"_self\">".$item["text"]."</a></li>\n";
  }
}
?>

</ul>
</div>


