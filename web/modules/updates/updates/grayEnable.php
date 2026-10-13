<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
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

require_once("modules/updates/includes/xmlrpc.php");

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    exit;
}

verifyCSRFToken($_POST);

$updateid = htmlentities($_POST['updateid']);
$title = htmlentities($_POST['title']);
$identity = isset($_POST['entityid']) ? $_POST['entityid'] : -1;

$result = xmlrpc_grey_update($updateid, $identity, 1);
if($result){
    $str = sprintf(_T("The update %s (%s) has been enabled.", "updates"), $title, $updateid);
    new NotifyWidgetSuccess($str);
}
else{
    $str = sprintf(_T("The update %s (%s) hasn't been enabled.", "updates"), $title, $updateid);
    new NotifyWidgetFailure($str);
}
header('location: '.urlStrRedirect("updates/updates/updatesListWin", getFilteredGetParams($_POST)));
exit;
?>
