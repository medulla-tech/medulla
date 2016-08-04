/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2015-2016 Siveo http://www.siveo.net
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


<?php if ($_SESSION['__notify'])  { ?>
<script type="text/javascript">
    window.location= 'main.php'
</script>
<?php

exit(6);

}
?>
<div style="width:99%">
<?php


$connectionNumber = array();
$action = array();
$extra = array();
$date = array();
$oparr = array();

foreach (xmlCall("base.getLdapLog",array($_SESSION['ajax']['filter'])) as $line) {
    if (is_array($line)) {
    $connectionNumber[] = '<a href="#" onClick="jQuery(\'#param\').val(\''.'conn='.$line["conn"].'\'); pushSearch(); return false">'.$line["conn"].'</a>';
    $action[] = '<a href="#" onClick="jQuery(\'#param\').val(\''.$line["op"].'\'); pushSearch(); return false">'.$line["op"].'</a>';
    $extra[] = $line["extra"];
    $dateparsed = strftime('%b %d %H:%M:%S',$line["time"]);
    $date[] = str_replace(" ", "&nbsp;", $dateparsed);
    if ($line["opfd"] == "op") {
            $oparr[] = $line["opfdnum"];
        } else {
            $oparr[] = "";
        }
    } else {
    $connectionNumber[] = "";
    $action[] = "";
    $date[] = "";
    $oparr[] = "";
    $extra[] = $line;
    }
}

$n = new UserInfos($date,_("Date"),"1px");
$n->addExtraInfo($connectionNumber,_("Connection"),"1px");
$n->addExtraInfo($oparr,_("Operation"),"1px");
$n->addExtraInfo($action,_("Actions"),"1px");
$n->addExtraInfo($extra,_("Extra information"));
$n->end= 200;
$n->first_elt_padding = 1;
$n->display(0,0);

?>
</div>
