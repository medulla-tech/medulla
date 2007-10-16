<?

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

require("localSidebar.php");
require("graph/navbar.inc.php");

$name = urldecode($_GET["name"]);

if (isset($_POST["bedit"])) {
    $ret = setPublicImageData($name, $_POST["newname"], $_POST["newtitle"], $_POST["newdesc"]);
    if (!isXMLRPCError())
        new NotifyWidgetSuccess(_T("Data successfully changed for « $name »"));
    else     
        new NotifyWidgetFailure(_T("An error occured while changing data for « $name »"));
    header("Location: main.php?module=imaging&submod=publicimages&action=index");
} else {
    $p = new PageGenerator(sprintf(_T("Edit image %s"), $name));
    $p->setSideMenu($sidemenu);
    $p->display();

    $infos = getPublicImageInfos($name);

    $f = new ValidatingForm();
    $f->push(new Table());

    $formElt = new InputTpl("newname");
    $a = array("required" => True, "value" => $infos["name"]);
    $f->add(new TrFormElement(_T("Name"), $formElt), $a);

    $formElt = new InputTpl("newtitle");
    $a = array("required" => True, "value" => $infos["title"]);
    $f->add(new TrFormElement(_T("Title"), $formElt), $a);

    $formElt = new InputTpl("newdesc");
    $a = array("required" => True, "value" => $infos["desc"]);
    $f->add(new TrFormElement(_T("Description"), $formElt), $a);

    $f->addValidateButton("bedit");

    $f->pop();
    $f->display();
}

?>
