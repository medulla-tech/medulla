<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
?>
<?php

/* Display MMC architecture component versions */

require("includes/config.inc.php");

require("includes/acl.inc.php");
require("includes/session.inc.php");

includeInfoPackage(fetchModulesList($conf["global"]["rootfsmodules"]));

echo "<h2>" . _T("MMC components version", "base") . "</h2>";
echo "<h3>" . _T("MMC agent: version", "base") . $_SESSION["modListVersion"]['ver'] . " / " . T_("revision", "base") . " " . $_SESSION["modListVersion"]['rev'] . "</h3>";
foreach ($_SESSION["supportModList"] as $modName) {
    echo "<b>$modName " . _T("plugin", "base") . "</b><br/>";
    $apirev = xmlCall($modName.".getApiVersion",null);
    $apiver = xmlCall($modName.".getVersion",null);
    $rev = xmlCall($modName.".getRevision", null);
    echo _T("agent: version", "base") . " " . $apiver . " / " . _T("API", "base") . $apirev. " / " . _T("revision", "base") . " " . $rev . "<br/>";
    if (in_array($modName, $_SESSION["modulesList"])) {
        echo _T("web: version", "base") . " " . $__version[$modName] . " / " . _T("API", "base") . $__apiversion[$modName] . " / " . _T("revision", "base") . " " . $__revision[$modName] . "<br/>";  
        if ($__apiversion[$modName] != $apirev) {
            echo '<div style="color : #D00;">' . _T("Warning: API numbers mismatch", "base") . '</div>';
        }
    } else {
        echo '<div style="color : #D00;">' . _T("web: plugin is not installed", "base") . '</div>';
    }
    echo "<br/>";
}

?>
