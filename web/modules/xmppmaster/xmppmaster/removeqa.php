<?php
/**
 * (c) 2015-2017 Siveo, http://www.siveo.net
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
 *
 * File removeqa.php
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");

extract($_GET);

if (isset($_POST["bconfirm"])) {
    xmlrpc_delQa_custom_command($user, $os, $namecmd );
    header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/customQA", array()));
}
else{
print_r($_GET);
    $f = new PopupForm(sprintf(_T("Delete this Quick Action :%s"),$namecmd));
    $hidden = new HiddenTpl("namecmd");
    $f->add($hidden, array("value" => $namecmd, "hide" => True));
    $hidden = new HiddenTpl("os");
    $f->add($hidden, array("value" => $os, "hide" => True));
    $hidden = new HiddenTpl("user");
    $f->add($hidden, array("value" => $user, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

?>
