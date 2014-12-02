<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require_once("modules/pkgs/includes/xmlrpc.php");

if (isset($_POST["bconfirm"])) {
    activateAppstreamFlow($_POST['id'], $_POST['package_name'], $_POST['package_label'], $_POST['duration']);
    if (!isXMLRPCError() and $ret != -1) new NotifyWidgetSuccess(_T("The stream has been added successfully. You will receive the latest updates of this stream directly in your package list.", "pkgs"));
    if ($ret == -1) new NotifyWidgetFailure(_T("Unable to add stream.", "pkgs"));

    header("Location: " . urlStrRedirect("pkgs/pkgs/appstreamSettings", array()));
    exit;
} else {
    $id = $_GET['id'];
    $package_name = $_GET['package_name'];
    $package_label = $_GET['package_label'];
    $duration = $_GET['duration'];

    $f = new PopupForm(_T("Activate this Appstream stream?"));
    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $id, "hide" => True));
    $hidden = new HiddenTpl("package_name");
    $f->add($hidden, array("value" => $package_name, "hide" => True));
    $hidden = new HiddenTpl("package_label");
    $f->add($hidden, array("value" => $package_label, "hide" => True));
    $hidden = new HiddenTpl("duration");
    $f->add($hidden, array("value" => $duration, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

?>
