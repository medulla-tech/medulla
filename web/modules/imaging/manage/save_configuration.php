<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2017-2024 Siveo, http://http://www.siveo.net
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/* Get MMC includes */
require_once("includes/config.inc.php");
require_once("includes/i18n.inc.php");
require_once("includes/acl.inc.php");
require_once("includes/session.inc.php");
require_once("includes/PageGenerator.php");
require("modules/imaging/includes/includes.php");
require_once("modules/imaging/includes/xmlrpc.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$location = getCurrentLocation();
$params = getParams();

if (xmlrpc_doesLocationHasImagingServer($location)) {
    $config = xmlrpc_getImagingServerConfig($location);
    $imaging_server = $config[0];
    $default_menu = $config[1];
    if (isset($_POST["bvalid"])) {
        $loc_name = (!empty($_POST['loc_name'])) ? $_POST['loc_name'] : "";
        $item_uuid = (!empty($_POST['itemid'])) ? $_POST['itemid'] : "";

        $label = (!empty($_POST['itemlabel'])) ? urldecode($_POST['itemlabel']) : "";
        $name = !empty($imaging_server["name"]) ? htmlentities($imaging_server["name"]) : $location;

        $params = getParams();
        $params['default_name'] = $_POST['default_m_label'];
        $params['timeout'] = $_POST['default_m_timeout'];
        $params['hidden_menu'] = (!empty($_POST['default_m_hidden_menu'])) ? $_POST['default_m_hidden_menu'] : false;
        $params['background_uri'] = $_POST['boot_xpm'];
        $params['message'] = $_POST['boot_msg'];
        $params['language'] = $_POST['language'];
        $params['pxe_login'] = $_POST['pxe_login'];
        if ($_POST['pxe_password'] != $_POST['old_pxe_password']) {
            $params['pxe_password'] = $_POST['pxe_password'];
        }
        $params['clonezilla_saver_params'] = $_POST['clonezilla_saver_params'];
        $params['clonezilla_restorer_params'] = $_POST['clonezilla_restorer_params'];
        $params["diskless_dir"] = htmlentities($_POST["diskless_dir"]);
        $params["diskless_kernel"] = htmlentities($_POST["diskless_kernel"]);
        $params["inventories_dir"] = htmlentities($_POST["inventories_dir"]);
        $params["pxe_time_reboot"] = htmlentities($_POST["pxe_time_reboot"]);
        $params["diskless_initrd"] = htmlentities($_POST["diskless_initrd"]);
        $params["tools_dir"] = htmlentities($_POST["tools_dir"]);
        $params['davos_opts'] = htmlentities($_POST['davos_opts']);
        $params['template_name'] = htmlentities($_POST['template_name']);

        $ret = xmlrpc_setImagingServerConfig($location, $params);

        // goto images list
        if ($ret[0] and !isXMLRPCError()) {
            $str = sprintf(_T("Imaging server <strong>%s</strong> configuration saved.", "imaging"), $name);
            xmlrpc_setfromxmppmasterlogxmpp(
                $str,
                "IMG",
                '',
                0,
                $label,
                'Manuel',
                '',
                '',
                '',
                "session user ".$_SESSION["login"],
                'Imaging | Postinstall | Menu | Configuration | Manual'
            );
            new NotifyWidgetSuccess($str);
            // Synchronize boot menu
            $ret = xmlrpc_synchroLocation($location);
            if (isXMLRPCError()) {
                $str = sprintf(_T("Boot menu generation failed for package server: %s<br /><br />Check /var/log/mmc/pulse2-package-server.log", "imaging"), implode(', ', $ret[1]));
                new NotifyWidgetFailure($str);
            }
        } else {
            new NotifyWidgetFailure($ret[1]);
        }
    }
}
header("Location: " . urlStrRedirect("imaging/manage/configuration", $params));
exit;
