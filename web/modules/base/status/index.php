<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
/* définition des fonctions pour cette page */

function print_mem_bar($title, $max, $used, $cache = 0, $width = 320) {
    $wused = ($used / $max) * $width;
    if ($title != "") {
        echo $title." :";
    }
    echo "<div class=\"membarfree\" style=\"width: ".$width."px\">";
    if ($cache > 0) {
        printf("<div class=\"membarcache\" style=\"width: %.0fpx\">", $wused);
        $wused = (($used - $cache) / $max) * $width;
    }
    printf("<div class=\"membarused\" style=\"width: %.0fpx\"></div>", $wused);
    if ($cache > 0) {
            echo "</div>";
    }
    echo "</div>\n";
}

function print_disk_info() {
    /* -l option to only get local filesystem occupation */
    $df = xmlCall("base.getDisksInfos");
    unset($df[0]);

    echo "<table>";
    
    $incomplete_lines = "";

    foreach ($df as $disk) {
        //if previous is truncated we add it to the current line
        if ($incomplete_lines) {
            $disk = $incomplete_lines ." ". $disk;
            unset($incomplete_lines);
        }

        if (preg_match("/^\/dev\/mapper\/data-snap/", $disk)
            || preg_match("/^[ ]+/", $disk)) {
            continue;
        }

        //if device name use whole line... we skip this line
        //concatenate it with the next
        if (!preg_match(("/[ ]/"),$disk)) {
            $incomplete_lines = $disk;
            continue;
        }

        $disk = preg_split("/[ ]+/", $disk);

        if ((array_search($disk[0], array("tmpfs", "none", "udev"))!==FALSE) || ($disk[1] == "0"))
            continue;
      
        echo "<tr><td class=\"statusPad\">$disk[5]</td><td class=\"statusPad\">($disk[0])</td><td class=\"statusPad\">[$disk[4]]</td></tr>\n";
        echo "<tr><td colspan=\"3\" class=\"statusPad\" style=\"padding-bottom: 2px;\">";
        print_mem_bar("", $disk[1], $disk[2]);
        echo "</td></tr>\n";
    }
    echo "</table>";
}

function print_health() {
    $up = xmlCall("base.getUptime");
    $up = trim($up);
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

    if ($days > 0) {
            echo $days." "._("day").$d." ";
    }

    if (($days > 0) || ($hrs > 0)) {
        echo $hrs." "._("hour").$h." ";
    }

    echo $mins." "._("minute").$m."<br/><br/>\n";

    $mem = xmlCall("base.getMemoryInfos");

    $m = preg_split("/[ ]+/", $mem[1]);
    print_mem_bar(_("Memory"), $m[1], $m[2],$m[5]+$m[6]);
    $m = preg_split("/[ ]+/", $mem[3]);
    if ($m[1] > 0) {
        print_mem_bar(_("Swap"), $m[1], $m[2]);
    }
}

function print_ldap_conf() {
    $conf = xmlCall("base.getLdapRootDN",null);
    foreach($conf as $name => $value) {
        echo '<p>'.$name.' : '.$value.'</p>';
    }
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

div.right {
        float: right;
        width: 49%;
        margin: 0;
}

div.left {
        width: 49%;
        margin: 0;
}

h2.statusPad {
        text-align: center;
}

div.statusPad {
        padding: 0px;
        text-align: center;
        font-size: 11px;
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        -moz-border-radius: 1em;
        -webkit-border-radius: 1em;
        padding: 10px;
        margin-bottom: 10px;
}

-->
</style>

<?php
require("graph/navbar.inc.php");
require("includes/statusSidebar.inc.php");
$p = new PageGenerator(_("Global view"));
$p->displayTitle();

?>

<div class="right">
  <div class="statusPad">
    <h2 class="statusPad"><?php echo  _("Server status") ?></h2>
    <?php print_health(); ?>
  </div>

 <div class="statusPad">
    <h2 class="statusPad"><?php echo  _("LDAP Configuration") ?></h2>
    <?php print_ldap_conf(); ?>
  </div>
</div>

<div class="left">
  <div class="statusPad">
    <h2 class="statusPad"><?php echo  _("Hard drive partitions") ?></h2>
    <?php print_disk_info(); ?>
  </div>
  
  <div class="statusPad">
    <h2 class="statusPad"><?php echo   _("Background jobs") ?></h2>
    <div id="bgps"> </div>
    <script type="text/javascript">
        function update_bgps(){
            jQuery('#bgps').load('includes/bgps_view.php',function(){
                setTimeout('update_bgps();',2000);
            });
        }
        update_bgps();
    </script>
  </div>
</div>
