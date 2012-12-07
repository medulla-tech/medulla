<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

if (isset($_POST["bconfirm"])) {
    // id of the script
    $script_id = $_POST['itemid'];
    $location = getCurrentLocation();
    $ret = xmlrpc_createBootServiceFromPostInstall($script_id, $location);

    $ret = (is_array($ret)) ? $ret[0] : $ret;
    if ($ret) {
        $str = sprintf(_T("Boot service successfully created", "imaging"));
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/service"));
        exit;
    }
    else {
        $str = sprintf(_T("Error while creating Boot Service", "imaging"));
        new NotifyWidgetFailure($str);
        header("Location: " . urlStrRedirect("imaging/manage/postinstall"));
        exit;
    }
}

$params = getParams();
$item_uuid = $_GET['itemid'];
$label = urldecode($_GET['itemlabel']);

$f = new PopupForm(sprintf(_T("Add <b>%s</b> to available Boot Services ?", "imaging"), $label));

$f->push(new Table());

// form preseeding
$f->add(new HiddenTpl("location"),                      array("value" => $location,                      "hide" => True));
$f->add(new HiddenTpl("itemlabel"),                     array("value" => $label,                         "hide" => True));
$f->add(new HiddenTpl("itemid"),                        array("value" => $item_uuid,                     "hide" => True));
$f->add(new HiddenTpl("default_mi_label"),              array("value" => $label,                         "hide" => True));

$f->addValidateButton("bconfirm");
$f->addCancelButton("bback");
$f->display();

?>
