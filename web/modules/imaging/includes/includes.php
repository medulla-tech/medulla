<?

/*
 * (c) 2009-2010 Mandriva, http://www.mandriva.com
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

require('web_def.inc.php');

global $SYNCHROSTATE_UNKNOWN;
global $SYNCHROSTATE_TODO;
global $SYNCHROSTATE_SYNCHRO;
global $SYNCHROSTATE_RUNNING;
global $SYNCHROSTATE_INIT_ERROR;
list($SYNCHROSTATE_UNKNOWN, $SYNCHROSTATE_TODO, $SYNCHROSTATE_SYNCHRO, $SYNCHROSTATE_RUNNING, $SYNCHROSTATE_INIT_ERROR) = array(0, 1, 2, 3, 4);

$errors = array(
    1000 => _T("There was an error (this is a default message).", "imaging"), // $ERR_DEFAULT
    1001 => _T("The nomenclature is missing.", "imaging"), // $ERR_MISSING_NOMENCLATURE
    1003 => _T("This imaging server don't exists.", "imaging"), // $ERR_IMAGING_SERVER_DONT_EXISTS
    1004 => _T("This entity already exists.", "imaging"), // $ERR_ENTITY_ALREADY_EXISTS
    1005 => _T("You asked for an unexisting menu item.", "imaging"), // $ERR_UNEXISTING_MENUITEM
    1006 => _T("This target has no menu.", "imaging"), // $ERR_TARGET_HAS_NO_MENU
    1007 => _T("This entity has no default menu, you first need to set one.", "imaging"), // $ERR_ENTITY_HAS_NO_DEFAULT_MENU
    1008 => _T("This image already exists.", "imaging"), // $ERR_IMAGE_ALREADY_EXISTS
    1009 => _T("This computer already exists.", "imaging"), // $ERR_COMPUTER_ALREADY_EXISTS
    1010 => _T("You need to register this computer's imaging server to be able to use imaging.", "imaging"), // $ERR_NEED_IMAGING_SERVER_REGISTRATION
);

function getPulse2ErrorString($ERR_CODE, $DEFAULT_STRING) {
    if (in_array($ERR_CODE, $errors)) {
        return $errors[$ERR_CODE];
    }
    return $DEFAULT_STRING;
}

function getCurrentLocation() {

    $location = false;

    if(isset($_GET["location"]))
        $_SESSION["location"] = $_GET["location"];

    if(isset($_SESSION["location"]))
        $location = $_SESSION["location"];

    return $location;
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

    echo format_disk_info($df);
}

function print_mem_bar($title, $max, $used, $cache = 0, $width = 320) {
    echo format_mem_bar($title, $max, $used, $cache, $width);
}

function print_health() {
    $up = xmlCall("base.getUptime");
    $up = trim($up[0]);

    $mem = xmlCall("base.getMemoryInfos");
    echo format_health($up, $mem);
}

function format_disk_info($df) {
    $ret = '';

    foreach ($df as $disk) {
        //if previous is truncated we add it to the current line
        if (isset($incomplete_lines) and $incomplete_lines != "") {
            $disk = $incomplete_lines . " " . $disk;
            unset($incomplete_lines);
        }

        if (preg_match("/^\/dev\/mapper\/data-snap/", $disk) || preg_match("/^[ ]+/", $disk)) {
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

        $ret .= format_mem_bar("<strong>$disk[5]</strong> <em>($disk[0])</em> : ".humanSize($disk[2]*1024)."/".humanSize($disk[3]*1024), $disk[1], $disk[2]);
    }
    return $ret;
}

function format_mem_bar($title, $max, $used, $cache = 0, $width = 320) {
    $ret = '';
    if ($max != 0) {
        $wused = ($used / $max) * $width;
    } else {
        $wused = $width;
    }
    if ($title != "") {
        $ret .= "<p>".$title."</p>";
    }
    $ret .= "<div class=\"membarfree\" style=\"width: ".$width."px\">";
    if ($cache > 0) {
        $ret .= sprintf("<div class=\"membarcache\" style=\"width: %.0fpx\">", $wused);
        $wused = (($used - $cache) / $max) * $width;
    }
    $ret .= sprintf("<div class=\"membarused\" style=\"width: %.0fpx\"></div>", $wused);
    if ($cache > 0) {
            $ret .= "</div>";
    }
    $ret .= "</div>\n";
    return $ret;
}

function format_health($up, $mem) {
    list($up) = explode(" ", $up);
    $ret = '';

    $days = (int) ($up / (24*60*60));
    $up -= $days * 24*60*60;
    $hrs = (int)($up / (60*60));
    $up -= $hrs * 60*60;
    $mins = (int)($up / 60);

    ($days > 1) ? $d = "s" : $d = "";
    ($hrs > 1) ? $h = "s" : $h = "";
    ($mins > 1) ? $m = "s" : $m = "";

    $ret .= "<em>"._("Uptime: ")."</em>";
    if ($days > 0) {
            $ret .= $days." "._("day").$d." ";
    }
    if (($days > 0) || ($hrs > 0)) {
        $ret .= $hrs." "._("hour").$h." ";
    }
    $ret .= $mins." "._("minute").$m;


    $m = preg_split("/[ ]+/", $mem[1]);
    $ret .= format_mem_bar("<em>"._("Memory")."</em> : ".humanSize($m[2]*1024)."/".humanSize(($m[5]+$m[6])*1024)."/".humanSize($m[1]*1024), $m[1], $m[2],$m[5]+$m[6]);
    $m = preg_split("/[ ]+/", $mem[3]);
    if ($m[1] > 0) {
        $ret .= format_mem_bar("<em>"._("Swap")."</em> : ".humanSize($m[2]*1024)."/".humanSize($m[1]*1024), $m[1], $m[2]);
    }
    return $ret;
}

function _toDate($a, $noneIsAsap = False) {
    $never = array(2031, 12, 31, 23, 59, 59);
    $asap = array(1970, 1, 1, 0, 0, 0);

    if (is_array($a) && (count($a) == 6 || count($a) == 9)) {

        if (count(array_diff(array_slice($a, 0, 6), $never)) == 0)
            return _T('Never', 'msc');

        if (count(array_diff(array_slice($a, 0, 6), $asap)) == 0)
            return _T('As soon as possible', 'msc');

        $parsed_date = mktime($a[3], $a[4], $a[5], $a[1], $a[2], $a[0]);
        return strftime(web_def_date_fmt(), $parsed_date);

    } elseif ($noneIsAsap && !$a) {
        return _T('As soon as possible', 'msc');
    } else { // can't guess if we talk about a date or something else :/
        return _T('<i>undefined</i>', 'msc');
    }
}

function humanReadable($num, $unit='B', $base=1024) {
    foreach (array('', 'K', 'M', 'G', 'T') as $i) {
        if ($num < $base) {
            return sprintf("%3.1f %s%s", $num, $i, $unit);
        }
        $num /= $base;
    }
}

/*
 * Widget that display an image backup log
 */
class ImageLogs extends HtmlElement {

    /* Logs to display */
    var $logs;

    var $errstr = "ERROR:";

    var $colors = array(
        'daemon.debug'=>'LOG_DEBUG',
        'daemon.notice'=>'LOG_NOTICE',
        'daemon.info'=>'LOG_INFO',
        'daemon.warn'=>'LOG_WARNING',
        'daemon.err'=>'LOG_ERR',
        'syslog.debug'=>'LOG_DEBUG',
        'syslog.notice'=>'LOG_NOTICE',
        'syslog.info'=>'LOG_INFO',
        'syslog.warn'=>'LOG_WARNING',
        'syslog.err'=>'LOG_ERR',
        'user.debug'=>'LOG_DEBUG',
        'user.notice'=>'LOG_NOTICE',
        'user.info'=>'LOG_INFO',
        'user.warn'=>'LOG_WARNING',
        'user.err'=>'LOG_ERR',
    );

    function ImageLogs($logs) {
        assert(is_array($logs));
        $this->logs = $logs;
    }

    function display() {
        $lines = array();
        $errlines = array();
        foreach($this->logs as $line => $msg) {
            if (strpos($msg, "===") === 0) {
                $msg = "<b>" . "$msg" . "</b>";
            }  else if(strpos($msg, $this->errstr) === 0) {
                $msg = "<span id=\"err$line\" class=\"LOG_ERR\">" . "$msg" . "</span>";
                $errlines[] = $line;
            }
            foreach ($this->colors as $pattern=>$color) {
                if (strpos($msg, $pattern) > 0) {
                    $msg = "<span id=\"err$line\" class=\"$color\">" . "$msg" . "</span>";
                    continue;
                }
            }
            $lines[] = sprintf("<span class=\"linenumber\">%04d:</span>", $line) . " " . $msg;
        }

        foreach($errlines as $line) {
            print "<p class =\"LOG_ERR\" onClick=\"javascript:new Element.scrollTo('err$line');\">Click here to scroll to error on line $line.</p>";
        }

        $l = new ListInfos($lines, _T("Backup log messages", "imaging"));
        $l->setCssClass("imagelogs");
        $l->setRowsPerPage(count($lines));
        $l->setNavBar(False);
        $l->display(0, 1);
    }
}

?>
