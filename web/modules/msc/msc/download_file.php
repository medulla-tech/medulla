<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
 *
 * $Id: start_quick_action.php 259 2008-07-29 08:17:13Z cdelfosse $
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

require('modules/msc/includes/scheduler_xmlrpc.php');

$ret = scheduler_download_file('', $_GET['objectUUID']);

if (($ret === False) || ($ret[0] != 0)) {
    new NotifyWidgetFailure(_T("The download has failed."));
    header("Location: " . urlStrRedirect("base/computers/index"));
} else {
    $end = strpos($ret[1], "\n");
    $header = substr($ret[1], 0, $end);
    list($encoding, $mode, $filename) = explode(" ", $header);
    if ($encoding != "begin-base64")
        exit("Bad encoding");
    ob_end_clean();
    header("Content-type: application/octet-stream");
    header('Content-Disposition: attachment; filename="' . $filename . '"');
    print base64_decode(substr($ret[1], $end + 1));
}

exit;

?>