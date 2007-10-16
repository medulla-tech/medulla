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
    $filename = $_POST["filename"];
    $size = $_POST["media"] + 0;
    
    # FIXME: should do some check on $newname (not empty, no bad chars, ...)
    $ret = createIsoFromImage($name, $filename, $size);
    if (isXMLRPCError()) {
        new NotifyWidgetFailure(_T("The ISO image creation has failed"));
    } else {
        $str = '';
        $str .= _("<p>CD creation is launched in background</p>");
        $str .= _("<p> The ISO files will be stored as <b>$filename-??.iso</b> on share « iso » at the end of the process</p>");
        $str .= _("<p>Operation duration depend of the amount of data</p>");
        $n = new NotifyWidgetSuccess(_T("The ISO image creation is being done"));
        $n->add($str);
    }    
    header("Location: main.php?module=imaging&submod=publicimages&action=index");
} else {
    $name = urldecode($_GET["name"]);
}

$infos = getPublicImageInfos($name);

$f = new PopupForm(_("Autobootable deployment CD"));
$f->push(new Table());
$f->add(
    new TrFormElement(_T("File name"), new InputTpl("filename")),
    array("value" => $infos['title'], "required" => True)
);

$medialist = array(
    _T("CD 74 mins"),
    _T("CD 80 mins"),
    _T("DVD SL (4.2 Go)"),
    _T("DVD DL (8.4 Go)")
);
$mediavals = array(
    640*1024*1024,
    700*1024*1024,
    4.2*1024*1024*1024,
    8.4*1024*1024*1024
);

$listbox = new SelectItem("media");
$listbox->setElements($medialist);
$listbox->setElementsVal($mediavals);
$listbox->setSelected($medialist[0]);

$f->add(
    new TrFormElement(_T("Media size"), $listbox)
);
$f->pop();
$f->addText(_T("File name should not contain extension (ie 'foo', not 'foo.iso')"));
$f->add(new HiddenTpl("name"), array("value" => $name, "hide" => True));
$f->addValidateButton("bconfirm");
$f->addCancelButton("bback");
$f->pop();
$f->display();

?>
