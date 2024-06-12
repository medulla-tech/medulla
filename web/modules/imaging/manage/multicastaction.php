<?php
/*
 * (c) 2015-2024 Siveo, http://http://www.siveo.net
 *
 * $Id$
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("modules/imaging/manage/localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');
require_once("modules/xmppmaster/includes/xmlrpc.php");

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

$objprocess = array();
if (isset($multicast) &&
        isset($location) &&
        isset($process) &&
        isset($path) &&
        $location != "" &&
        $process != "") {

    $objprocess['location'] = $location;

    $informationsparameters = xmlrpc_GetMulticastMultiSessionParameters($location);

    switch ($multicast) {
        case "start":
            $objprocess['group'] = $informationsparameters['gid'];
            $objprocess['description'] = $informationsparameters['itemlabel'];
            $objprocess['master'] = $informationsparameters['uuidmaster'];
            $objprocess['path'] = "/var/lib/pulse2/imaging/masters/".$informationsparameters['uuidmaster'];
            $objprocess['process'] = $path.$process;
            xmlrpc_start_process_multicast($objprocess);
            xmlrpc_setfromxmppmasterlogxmpp(
                _T("Start Multicast of ( Master :", 'Imaging').' '.$informationsparameters['uuidmaster'].") ".
                                                    _T("on (group :", 'Imaging')." ".$informationsparameters['gid'].") ".
                                                    _T("to (location : ", 'Imaging').$location ."):( ".$informationsparameters['itemlabel'].")",
                "IMG",
                '',
                0,
                $informationsparameters['gid'],
                'Manuel',
                '',
                '',
                '',
                "session user ".$_SESSION["login"],
                'Imaging | Multicast | Start  | Manual'
            );
            break;
        case "stop":
            xmlrpc_delete_multicast_from_db($informationsparameters);
            $objprocess['process'] = $process;
            xmlrpc_stop_process_multicast($objprocess);
            $objprocess['process'] = $path.$process;
            $gr = xmlrpc_clear_script_multicast($objprocess);
            xmlrpc_ClearMulticastMultiSessionParameters($location);
            xmlrpc_setfromxmppmasterlogxmpp(
                _T("Stop Multicast of ( Master :", 'Imaging').' '.$informationsparameters['uuidmaster'].") ".
                                                    _T("on (group :", 'Imaging')." ".$informationsparameters['gid'].") ".
                                                    _T("to (location : ", 'Imaging').$location ."):( ".$informationsparameters['itemlabel'].")",
                "IMG",
                '',
                0,
                $informationsparameters['gid'],
                'Manuel',
                '',
                '',
                '',
                "session user ".$_SESSION["login"],
                'Imaging | Multicast | Start  | Manual'
            );
            if ($gr != -1) {
                xmlrpc_setfromxmppmasterlogxmpp(
                    _T("Synchro Profile Menu group : ", 'Imaging').' '.$informationsparameters['gid'].") ",
                    "IMG",
                    '',
                    0,
                    $informationsparameters['gid'],
                    'Manuel',
                    '',
                    '',
                    '',
                    "session user ".$_SESSION["login"],
                    'Imaging | Menu | Start | Manual'
                );
                xmlrpc_synchroProfile($gr);
            }
            break;
        case "clear":
            xmlrpc_delete_multicast_from_db($informationsparameters);
            $objprocess['process'] = $path.$process;
            $gr = xmlrpc_clear_script_multicast($objprocess);
            if ($gr != -1) {
                xmlrpc_synchroProfile($gr);
                xmlrpc_setfromxmppmasterlogxmpp(
                    _T("Synchro Profile Menu group : ", 'Imaging').' '.$informationsparameters['gid'].") ("._T("location : ", 'Imaging').$location.")",
                    "IMG",
                    '',
                    0,
                    $informationsparameters['gid'],
                    'Manuel',
                    '',
                    '',
                    '',
                    "session user ".$_SESSION["login"],
                    'Imaging | Menu | Start | Manual'
                );
            }
            //unset($_SESSION['PARAMMULTICAST']);
            xmlrpc_ClearMulticastMultiSessionParameters($location);
            xmlrpc_setfromxmppmasterlogxmpp(
                _T("Clear Multicast of ( Master :", 'Imaging').' '.$informationsparameters['uuidmaster'].") ".
                                                    _T("on (group :", 'Imaging')." ".$informationsparameters['gid'].") ".
                                                    _T("to (location : ", 'Imaging').$location ."):( ".$informationsparameters['itemlabel'].")",
                "IMG",
                '',
                0,
                $informationsparameters['gid'],
                'Manuel',
                '',
                '',
                '',
                "session user ".$_SESSION["login"],
                'Imaging | Multicast | Start  | Manual'
            );
            break;
    }
}
redirectTo(urlStrRedirect("imaging/manage/index/"));
