<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://www.siveo.net
 *
 * This file is part of Management Console (MMC).
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
<link rel="stylesheet" href="modules/dashboard/graph/css/index.css" type="text/css" />
<script type="text/javascript" src="jsframework/lib/raphael/raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.pie-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.line-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.bar-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/utilities.js"></script>
<script type="text/javascript" src="jsframework/portlet.js"></script>
<script src="jsframework/d3/d3.js"></script>

<script src="modules/dashboard/graph/js/donut.js"></script>
<script src="modules/dashboard/graph/js/line.js"></script>
<script src="modules/dashboard/graph/js/pie.js"></script>
<script src="modules/dashboard/graph/js/bar.js"></script>
<script src="modules/dashboard/graph/js/dashboard.js"></script>

<?php
print '<div id="dashboard-grid">';

$modules = $_SESSION["modulesList"];

// Widget order - each widget sizes to its content
$customPanelOrder = array(
    'general',
    'space',
    'os_repartition',
    'computersOnline',
    'product_updates',
    'inventory',
    'antivirus',
    'agents',
    'deploymentsLaunched',
    'successRate',
);

// Find panel files
$availablePanels = array();
foreach($customPanelOrder as $panelName) {
    foreach($modules as $module) {
        if (hasCorrectModuleAcl($module, false) == true) {
            $file = "modules/$module/includes/panels/$panelName.inc.php";
            if (file_exists($file) && hasCorrectDashboardAcl($module, $panelName)) {
                $options = array();
                ob_start();
                include($file);
                ob_end_clean();
                if (!isset($options["enable"])) $options["enable"] = True;
                if (!isset($options["refresh"])) $options["refresh"] = 10;
                $availablePanels[$panelName] = array(
                    'file' => $file,
                    'options' => $options
                );
                break;
            }
        }
    }
}

// Display panels
$z = 1;
foreach($customPanelOrder as $panelName) {
    if (isset($availablePanels[$panelName])) {
        $panelData = $availablePanels[$panelName];
        $file = $panelData['file'];
        $options = $panelData['options'];
        if ($options["enable"]) {
            print '<div class="dashboard-column" id="col'.$z++.'">';
            $panel = new AjaxPage(urlStrRedirect('dashboard/main/ajaxPanels'), $options["id"], array("file" => urlencode($file)), $options["refresh"]);
            $panel->class = "portlet";
            $panel->display();
            print '</div>';
        }
    }
}

print '</div>'; // Close dashboard-grid

// Disabled widgets drawer
$disabledText = _T("Disabled widgets", "dashboard");
print <<<DRAWER
<button id="disabled-widgets-btn" class="hidden">
    <span class="btn-text">$disabledText</span>
    <span class="btn-count">0</span>
</button>

<div id="drawer-overlay"></div>

<div id="disabled-widgets-drawer">
    <div class="drawer-header">
        <h3>$disabledText</h3>
        <button class="drawer-close">&times;</button>
    </div>
    <div class="drawer-content">
        <div id="collapsed-widgets-section"></div>
    </div>
</div>
DRAWER;

?>
