<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

require("graph/navbar.inc.php");
require("modules/dashboard/includes/dashboard-xmlrpc.inc.php");

?>
<script type="text/javascript" src="jsframework/lib/raphael/raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.pie-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.line-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.bar-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/utilities.js"></script>
<script type="text/javascript" src="jsframework/portlet.js"></script>
<?php

$d = new Div(array("id" => "dashboard"));
$d->display();

$modules = $_SESSION["modulesList"];
$i = 1;
$z = 1;
// Search for panels in plugins subdirs...
foreach(getPanels() as $panelName) {
    foreach($modules as $module) {
        if (hasCorrectModuleAcl($module, false) == true) {
            $basedir = "modules/$module/includes/panels/";
            if (is_dir($basedir)) {
                $h = opendir($basedir);
                while (false !== ($f = readdir($h))) {
                    if (substr($f, 0, 1) != ".") {
                        if ($f == $panelName . ".inc.php") {
                            $file = $basedir . $f;
                            include_once($file);
                            if (!isset($options["enable"]))
                                $options["enable"] = True;
                            if (!isset($options["refresh"]))
                                $options["refresh"] = 10;
                            if ($options["enable"]) {
                                if ($i % 2 == 1)
                                    print '<div class="column" id="col'.$z++.'" style="width: 230px;">';
                                $panel = new AjaxPage(urlStrRedirect('dashboard/main/ajaxPanels'), $options["id"], array("file" => urlencode($file)), $options["refresh"]);
                                $panel->class = "portlet";
                                $panel->display();
                                if ($i % 2 == 0)
                                    print '</div>';
                                $i++;
                            }
                        }
                    }
                }
            }
        }
    }
}


// print final closing div
if ($i>1 && ($i % 2 == 0))
    print '</div>';

// Adding more columns (user custom) [8 for full HD resolution]
for ($i = $z; $i<=8; $i++)
    print '<div class="column" id="col'.$i.'"></div>';

?>
