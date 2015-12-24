<?php
/*
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

require("modules/imaging/manage/localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');


 
 // fichier /tmp/multicast.sh existe
 // multicast lancer "affichage seulement bouton arrêt" voir aprés pour bar de progression
 // multicast non lancer "affichage seulement bouton stop"
 
 // cas extreme 
 // cas si  fichier /tmp/multicast.sh n'existe plus et /tmp/multicast.sh lancer normalement possible
 // stoper /tmp/multicast.sh
 
 // action bouton arret
 // 1)  stoper /tmp/multicast.sh
 // 2)  supprimer le fichier /tmp/multicast.sh
 // 3) regénéré les menus  unicast
 
 // action bouton marche
 // 1) start /tmp/multicast.sh

extract($_POST);

$objprocess=array();
if (    isset($multicast) && 
        isset($location) && 
        isset($process)&& 
        isset($path) &&
        $location !="" &&
        $process !=""){

    $objprocess['location']=$location;
 
    switch ($multicast) {
        case "start":
            $objprocess['process'] = $path.$process;
            xmlrpc_start_process_multicast($objprocess);
            break;
        case "stop":
            $objprocess['process'] = $process;
            xmlrpc_stop_process_multicast($objprocess);
            $objprocess['process'] = $path.$process;
            $gr = xmlrpc_clear_script_multicast($objprocess);
            if ($gr != -1) xmlrpc_synchroProfile($gr);
            break;
        case "clear":
            $objprocess['process'] = $path.$process;
            $gr = xmlrpc_clear_script_multicast($objprocess);
            if ($gr != -1) xmlrpc_synchroProfile($gr);
            break;
    }
}

redirectTo(urlStrRedirect("imaging/manage/index/")); 
?>
