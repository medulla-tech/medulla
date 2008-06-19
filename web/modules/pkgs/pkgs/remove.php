<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id: edit.php 433 2008-05-16 12:29:42Z cdelfosse $
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
    $p_api = $_GET["p_api"];
    $pid = $_GET["pid"];
    dropPackage(base64_decode($p_api), base64_decode($pid));
    if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The package has been deleted."));
    header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('p_api'=>$p_api)));
} else {
    $p_api = $_GET["p_api"];
    $pid = $_GET["pid"];
    $f = new PopupForm(_T("Delete this package"));
    $hidden = new HiddenTpl("p_api");
    $f->add($hidden, array("value" => $p_api, "hide" => True));
    $hidden = new HiddenTpl("pid");
    $f->add($hidden, array("value" => $pid, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

?>
