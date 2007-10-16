<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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

require("modules/imaging/includes/imaging-xmlrpc.inc.php");

if (isset($_POST["bconfirm"])) {
    $name = $_POST["name"];
    $newname = $_POST["newname"];
    
    # FIXME: should do some check on $newname (not empty, no bad chars, ...)
    $ret = duplicatePublicImage($name, $newname);
    if (isXMLRPCError())
        new NotifyWidgetFailure(_T("The image has not been duplicated to $newname"));
    elseif ($ret === 0)
        new NotifyWidgetSuccess(_T("The image has been duplicated to $newname."));
    elseif ($ret === 1)
        new NotifyWidgetFailure(_T("The image has not been duplicated to $newname, as $newname already exists"));
    else
        new NotifyWidgetFailure(_T("The image has not been duplicated to $newname"));
    header("Location: main.php?module=imaging&submod=publicimages&action=index");
} else {
    $name = urldecode($_GET["name"]);
}

$f = new PopupForm(_("Duplicate Image"));
$f->push(new Table());
$f->add(
    new TrFormElement(_T("Copy image to"), new InputTpl("newname")),
    array("value" => $name, "required" => True)
);
$f->pop();
$f->add(new HiddenTpl("name"), array("value" => $name, "hide" => True));
$f->addValidateButton("bconfirm");
$f->addCancelButton("bback");
$f->pop();
$f->display();
?>

