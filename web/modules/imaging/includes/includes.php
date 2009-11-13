<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id: launch.php 3946 2009-03-24 09:02:53Z cdelfosse $
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
 
function getCurrentLocation() {

    $location = false;

    if(isset($_GET["location"]))
        $_SESSION["location"] = $_GET["location"];

    if(isset($_SESSION["location"]))
        $location = $_SESSION["location"];
        
    return $location;
}

class TitleElement extends HtmlElement {    
    function TitleElement($title){
        $this->title=$title;
    }    
    function display(){
        print '<br/><h2>'.$this->title.'</h2>';
    }
}

class LedElement extends HtmlElement {    
    function LedElement($color){
        $this->color=$color;
        $this->value='<img style="vertical-align: middle" src="modules/imaging/graph/images/led_circle_'.$this->color.'.png">';
    }    
    function display(){
        print $this->value;
    }
    function __toString() {
        return $this->value;
    }
}

function getParams() {
    $params = array();
    // GET params
    if(isset($_GET['cn']) && isset($_GET['objectUUID'])) {
        $params = array('hostname' => $_GET['cn'], 'uuid' => $_GET['objectUUID']);
    } else if(isset($_GET['hostname']) && isset($_GET['uuid'])) {
        $params = array('hostname' => $_GET['hostname'], 'uuid' => $_GET['uuid']);
    } else if(isset($_GET['gid'])) {
        $params = array('gid' => $_GET['gid']);
    }
    return $params;
}

// value in 'o'
function humanSize($value) {
    if (strlen($value) > 9)
        return round($value/1024/1024/1024, 1).'Go';
    else if (strlen($value) > 6)
        return round($value/1024/1024, 1).'Mo';
    else if(strlen($value) > 3)
        return round($value/1024, 1).'Ko';
}

function print_disk_info() {
    /* -l option to only get local filesystem occupation */
    $df = xmlCall("base.getDisksInfos");
    unset($df[0]);
    
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
      
        print_mem_bar("<strong>$disk[5]</strong> <em>($disk[0])</em> : ".humanSize($disk[2]*1024)."/".humanSize($disk[3]*1024), $disk[1], $disk[2]);
    }
}

function print_mem_bar($title, $max, $used, $cache = 0, $width = 320) {
    $wused = ($used / $max) * $width;
    if ($title != "") {
        echo "<p>".$title."</p>";
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

function print_health() {
    $up = xmlCall("base.getUptime");
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

    echo "<em>"._("Uptime: ")."</em>";
    if ($days > 0) {
            echo $days." "._("day").$d." ";
    }
    if (($days > 0) || ($hrs > 0)) {
        echo $hrs." "._("hour").$h." ";
    }
    echo $mins." "._("minute").$m;

    $mem = xmlCall("base.getMemoryInfos");

    $m = preg_split("/[ ]+/", $mem[1]);
    print_mem_bar("<em>"._("Memory")."</em> : ".humanSize($m[2]*1024*1024)."/".humanSize(($m[5]+$m[6])*1024*1024)."/".humanSize($m[1]*1024*1024), $m[1], $m[2],$m[5]+$m[6]);
    $m = preg_split("/[ ]+/", $mem[3]);
    if ($m[1] > 0) {
        print_mem_bar("<em>"._("Swap")."</em> : ".humanSize($m[2]*1024*1024)."/".humanSize($m[1]*1024*1024), $m[1], $m[2]);
    }
}

?>
