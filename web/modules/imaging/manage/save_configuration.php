<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

/* Get MMC includes */
require_once("includes/config.inc.php");
require_once("includes/i18n.inc.php");
require_once("includes/acl.inc.php");
require_once("includes/session.inc.php");
require_once("includes/PageGenerator.php");
require("modules/imaging/includes/includes.php");
require("modules/imaging/includes/xmlrpc.inc.php");

$location = getCurrentLocation();
$params = getParams();

if (xmlrpc_doesLocationHasImagingServer($location)) {
    $config = xmlrpc_getImagingServerConfig($location);
    $imaging_server = $config[0];
    $default_menu = $config[1];
    if (isset($_POST["bvalid"])) {
        $from = $_POST['from'];
        $loc_name = $_POST['loc_name'];
        $item_uuid = $_POST['itemid'];

        $label = urldecode($_POST['itemlabel']);

        $params = getParams();
        $params['default_name'] = $_POST['default_m_label'];
        $params['timeout'] = $_POST['default_m_timeout'];
        $params['background_uri'] = $_POST['boot_xpm'];
        $params['message'] = $_POST['boot_msg'];
        $params['protocol'] = $_POST['rest_type'];
        $params['language'] = $_POST['language'];
        $params['mtftp_restore_timeout'] = $_POST['rest_wait'];

        $ret = xmlrpc_setImagingServerConfig($location, $params);

        // goto images list
        if ($ret[0] and !isXMLRPCError()) {
            $str = sprintf(_T("Imaging server <strong>%s</strong> configuration saved.", "imaging"), $label, $loc_id);
            new NotifyWidgetSuccess($str);
            // Synchronize boot menu
            $ret = xmlrpc_synchroLocation($location);
            if (isXMLRPCError()) {
                new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for package server: %s<br /><br />Check /var/log/mmc/pulse2-package-server.log", "imaging"), implode(', ', $ret[1])));
            }
        } else {
            new NotifyWidgetFailure($ret[1]);
        }
    }
}
header("Location: " . urlStrRedirect("imaging/manage/configuration", $params));

?>
