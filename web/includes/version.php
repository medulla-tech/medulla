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


require("config.inc.php");

require("acl.inc.php");
require("session.inc.php");

includeInfoPackage(fetchModulesList($conf["global"]["rootfsmodules"]));

session_start();

//echo "<h3>VERSION:</h3>";

echo '<h3> Agent revision'.$_SESSION["modListVersion"]['rev'].': </h3>';
foreach ($_SESSION["supportModList"] as $modName) {
          echo '<h4 style="padding-top: 1em; padding-bottom: 0em;">'.$modName."</h4>";
          echo '<b>agent</b> ';
          $apirev = xmlCall($modName.".getApiVersion",null);
          $apiver = xmlCall($modName.".getVersion",null);
          echo "version: $apiver<br/>api:".$apirev.
                "/ build: ".xmlCall($modName.".getRevision",null)."<br/>";
          echo '<b>web</b> ';
          echo "version: ".$__version[$modName]."<br/>";
          echo "api:  ".$__apiversion[$modName]."/ build: ".$__revision[$modName]."<br/>";

          if ($__apiversion[$modName]!=$apirev) {
              echo '<div style="color : #D00;">Modules non compatibles !!!</div>';
          }


      }



?>
