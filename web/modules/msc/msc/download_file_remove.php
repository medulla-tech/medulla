<?
/**
 * (c) 2008 Mandriva, http://www.mandriva.com/
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

require('modules/msc/includes/scheduler_xmlrpc.php');

if (isset($_POST["bconfirm"])) {
    msc_remove_downloaded_files(array($_GET['id']));
    if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The file has been deleted.", "msc"));
    header("Location: " . urlStrRedirect("base/computers/download_file", array("objectUUID" => $_GET["objectUUID"])));
    exit;
} else {
    $f = new PopupWindowForm(_T("Please confirm file deletion", "msc"));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
