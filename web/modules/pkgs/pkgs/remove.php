<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2016 Siveo, http://siveo.net/
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
require_once("modules/msc/includes/commands_xmlrpc.inc.php");


if (isset($_POST["bconfirm"])) {
    $p_api = $_GET["p_api"];
    $pid = $_GET["pid"];
    $from = $_GET["from"];
    $uuid =  isset($_GET["packageUuid"]) ? $_GET["packageUuid"] : base64_decode($pid);
    $ret = remove_xmpp_package($uuid);
    xmlrpc_pkgs_delete_synchro_package($uuid);
    $expire_result = expire_all_package_commands($uuid);
    if ($ret == "1") {
        $str = _T("The package has been deleted.", "pkgs");
        new NotifyWidgetSuccess($str);
        xmlrpc_setfrompkgslogxmpp( $str,
                                    "PKG",
                                    '',
                                    0,
                                    $_GET["from"],
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Packaging | Remove | Package | Manual');
    }else{
        new NotifyWidgetFailure(_T("The package failed to delete", "pkgs"));
    }
        $to = "index";
        if ($from) {
            $to = $from;
        }
        header("Location: " . urlStrRedirect("pkgs/pkgs/$to", array('p_api' => $p_api)));
    exit;
} else {
    $p_api = $_GET["p_api"];
    $pid = $_GET["pid"];
    $from = $_GET["from"];
    $uuid =  isset($_GET["packageUuid"]) ? $_GET["packageUuid"] : base64_decode($pid);
    $f = new PopupForm(_T("Delete this package"));
    $hidden = new HiddenTpl("packageUuid");
    $f->add($hidden, array("value" =>$uuid, "hide" => True));
    $hidden = new HiddenTpl("p_api");
    $f->add($hidden, array("value" => $p_api, "hide" => True));
    $hidden = new HiddenTpl("pid");
    $f->add($hidden, array("value" => $pid, "hide" => True));
    $f->add(new HiddenTpl("from"), array("value" => $from, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
