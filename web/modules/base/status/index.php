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
<?
/* définition des fonctions pour cette page */

function print_mem_bar($title, $max, $used, $cache = 0, $width = 320) {
  $wused = ($used / $max) * $width;

  if ($title != "")
    {
      echo $title." :";
    }
  echo "<div class=\"membarfree\" style=\"width: ".$width."px\">";
  if ($cache > 0)
    {
      printf("<div class=\"membarcache\" style=\"width: %.0fpx\">", $wused);
      $wused = (($used - $cache) / $max) * $width;
    }
  printf("<div class=\"membarused\" style=\"width: %.0fpx\"></div>", $wused);

  if ($cache > 0)
    {
      echo "</div>";
    }
  echo "</div>\n";
}

function print_disk_info() {
  /* -l option to only get local filesystem occupation */
  remote_exec("df -m",$df);

  unset($df[0]);

  echo "<table style=\"width:95%\">";

  $incomplete_lines = "";

  foreach ($df as $disk)
    {
      //if previous is truncated we add it to the current line
      if ($incomplete_lines) {
  	$disk = $incomplete_lines ." ". $disk;
	unset($incomplete_lines);
      }

      if (preg_match("/^\/dev\/mapper\/data-snap/", $disk)
          || preg_match("/^[ ]+/", $disk))
        {
          continue;
        }

      //if device name use whole line... we skip this line
      //concatenate it with the next
      if (!preg_match(("/[ ]/"),$disk)) {
	$incomplete_lines = $disk;
	continue;
      }

      $disk = preg_split("/[ ]+/", $disk);

      if (array_search($disk[0], array("tmpfs","none"))!==FALSE)
	{
	  continue;
	}

	echo "<tr><td>$disk[5]</td><td>($disk[0])</td><td>[$disk[4]]</td></tr>\n";
	echo "<tr><td colspan=\"3\" style=\"padding-bottom: 2px;\">";
	print_mem_bar("", $disk[1], $disk[2]);
	echo "</td>\n";
    }
echo "</table>";
}

function print_health() {
  remote_exec("cat /proc/uptime", $up);
  $up = trim($up[0]);
  list($up) = explode(" ", $up);

  $days = (int) ($up / (24*60*60));
  $up -= $days * 24*60*60;
  $hrs = (int)($up / (60*60));
  $up -= $hrs * 60*60;
  $mins = (int)($up / 60);

  ($days > 1) ? $d = "s" : $d = "";
  ($hrs > 1) ? $h = "s" : $h = "";
  ($mins > 1) ? $m = "s" : $m = "";

  echo _("Uptime: ");

  if ($days > 0)
    {
      echo $days." "._("day").$d." ";
    }

  if (($days > 0) || ($hrs > 0))
    {
      echo $hrs." "._("hour").$h." ";
    }

  echo $mins." "._("minute").$m."<br>\n";

  remote_exec("free -m", $mem);

  $m = preg_split("/[ ]+/", $mem[1]);
  print_mem_bar(_("Memory"), $m[1], $m[2],$m[5]+$m[6]);
  $m = preg_split("/[ ]+/", $mem[3]);
  print_mem_bar(_("Swap"), $m[1], $m[2]);
}


?>

<style type="text/css">
<!--

div.membarfree {
        border-right: 1px solid #27537C;
        height: 12px;
        background: url("<?php echo $root; ?>img/main/bg_status_blue.gif") repeat-x left top transparent;
        padding: 0;
        margin: 0;
}

div.membarused {
        border: none;
        background: red;
        height: 12px;
        background: url("<?php echo $root; ?>img/main/bg_status_orange.gif") repeat-x right top transparent;
        overflow: hidden;
        float: left;
        padding: 0;
        display: inline;
}

div.membarcache {
        height: 12px;
        background: url("<?php echo $root; ?>img/main/bg_status_green.gif") repeat-x right top transparent;
        float: left;
        padding: 0;
        margin: 0;
}

*html div.membarused { margin: 0 -4px 0 0; } /* pour IE/PC */
*html div.membarcache { margin: 0 -4px 0 0; } /* pour IE/PC */

div.left {
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        -moz-border-radius: 1em;
        float: right;
        width: 45%;
        padding: 10px;
        margin-bottom: 1em;
        display: block;
        margin: 0;
	position: relative;
}

div.right {
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        -moz-border-radius: 1em;
        width: 45%;
        margin-bottom: 1em;
        padding: 10px;
        display: block;
	position: relative;
}

#accueilPad {
        overflow: auto;
}

#accueilPad h2,
#statusPad h2,
#accueilPad td {
        text-align: center;
}

#accueilPad h2,
#statusPad h2 {
	font-size: 14px;
}

#accueilPad table {
	color: #666;
	border: none;
	border-width: 0px;
	width: auto;
}

#accueilPad td {
	border: none;
	border-width: none;
	padding: 0px;
}

-->
</style>

<?php
require("graph/navbar.inc.php");
require("includes/statusSidebar.inc.php");
?>



<h2><?= _("Global view")?></h2>


<div class="fixheight"></div>

<div class="left">
  <div id="statusPad">
    <h2><?= _("Server status") ?></h2>
<?php print_health(); ?>
  </div>
</div>

<div class="right">
  <div id="accueilPad">
    <h2><?= _("Hard drive partitions") ?></h2>
  <?php print_disk_info(); ?>
  </div>
</div>

<div class="right">
  <div id="statusPad">

    <h2><?=  _("Background jobs") ?></h2>
    <div id="bgps">
    </div>
    <script type="text/javascript">
        new Ajax.PeriodicalUpdater('bgps','includes/bgps_view.php', {asynchronous: true, frequency: 2});
    </script>
  </div>
</div>
