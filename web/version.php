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


require("includes/config.inc.php");

require("includes/acl.inc.php");
require("includes/session.inc.php");

includeInfoPackage(fetchModulesList($conf["global"]["rootfsmodules"]));

session_start();

echo "<h2>LMC components version</h2>";
echo '<h3>LMC agent: version ' . $_SESSION["modListVersion"]['ver'] . ' / revision '.$_SESSION["modListVersion"]['rev'].'</h3>';
foreach ($_SESSION["supportModList"] as $modName) {
    echo "<b>$modName plugin</b><br/>";
    $apirev = xmlCall($modName.".getApiVersion",null);
    $apiver = xmlCall($modName.".getVersion",null);
    echo "agent: version $apiver / API ".$apirev. " / revision ".xmlCall($modName.".getRevision",null)."<br/>";
    echo "web: version ".$__version[$modName] .  " / API  ".$__apiversion[$modName]." / revision ".$__revision[$modName]."<br/>";  
    if ($__apiversion[$modName] != $apirev) {
        echo '<div style="color : #D00;">Warning: API numbers mismatch</div>';
    }
    echo "<br/>";
}

?>
