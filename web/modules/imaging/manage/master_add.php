<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2017 Siveo, http://http://www.siveo.net
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

include('modules/imaging/includes/includes.php');
include('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');
require_once("modules/xmppmaster/includes/xmlrpc.php");

$params = getParams();
$location = getCurrentLocation();

if (isset($_POST["bconfirm"])) {
    $item_uuid = $_POST['itemid'];
    $label = urldecode($_POST['itemlabel']);

    //    $params['name'] = $_POST['default_mi_label'];
    $params['hidden'] = ($_POST['do_display'] != 'on');
    $params['hidden_WOL'] = ($_POST['do_display_WOL'] != 'on');
    $params['default'] = ($_POST['do_default'] == 'on');
    $params['default_WOL'] = ($_POST['do_default_WOL'] == 'on');

    $ret = xmlrpc_addImageToLocation($item_uuid, $location, $params);

    // goto images list
    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Image <strong>%s</strong> added to default boot menu", "imaging"), $label);
        xmlrpc_setfromxmppmasterlogxmpp(
            $str,
            "IMG",
            '',
            0,
            $label,
            'Manuel',
            '',
            '',
            '',
            "session user ".$_SESSION["login"],
            'Imaging | Master | Menu | Add | Manual'
        );
        new NotifyWidgetSuccess($str);

        // Synchronize boot menu

        $ret = xmlrpc_synchroLocation($location);
        // goto images list
        if ((is_array($ret) and $ret[0] or !is_array($ret) and $ret) and !isXMLRPCError()) {
            $str = sprintf(_T("Boot menu generation Success for package server: %s<br /><br />Check /var/log/mmc/medulla-package-server.log", "imaging"));
            /* insert notification code here if needed */
        } elseif (!$ret[0] and !isXMLRPCError()) {
            $str = sprintf(_T("Boot menu generation failed for package server: %s<br /><br />Check /var/log/mmc/medulla-package-server.log", "imaging"), implode(', ', $ret[1]));
            new NotifyWidgetFailure($str);
        } elseif (isXMLRPCError()) {
            $str = sprintf(_T("Boot menu generation failed for package server: %s<br /><br />Check /var/log/mmc/medulla-package-server.log", "imaging"), implode(', ', $ret[1]));
            new NotifyWidgetFailure($str);
        }
        header("Location: " . urlStrRedirect("imaging/manage/master", $params));
        exit;
    } elseif ($ret[0]) {
        $str = sprintf(_T("Error : Image <strong>%s</strong> added to default boot menu", "imaging"), $label);
        xmlrpc_setfromxmppmasterlogxmpp(
            $str,
            "IMG",
            '',
            0,
            $label,
            'Manuel',
            '',
            '',
            '',
            "session user ".$_SESSION["login"],
            'Imaging | Master | Menu | Add | Manual'
        );
        header("Location: " . urlStrRedirect("imaging/manage/master", $params));
        exit;
    } else {
        xmlrpc_setfromxmppmasterlogxmpp(
            $ret[1],
            "IMG",
            '',
            0,
            $label,
            'Manuel',
            '',
            '',
            '',
            "session user ".$_SESSION["login"],
            'Imaging | Master | Menu | Add | Manual'
        );
        new NotifyWidgetFailure($ret[1]);
    }
}

if(isset($_GET['mod'])) {
    $mod = $_GET['mod'];
} else {
    $mod = "none";
}

switch($mod) {
    case 'add':
        image_add($type, $target_uuid);
        break;
    case 'edit':
        image_edit($type, $target_uuid);
        break;
    default:
        image_add($type, $target_uuid);
        break;
}

function image_add($type, $target_uuid)
{
    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    $f = new PopupForm(sprintf(_T("Add the image <b>%s</b> to <b>%s</b>", "imaging"), $label, $params['hostname'])); # Need to get the name of the target

    $f->push(new Table());

    // form preseeding
    $f->add(new HiddenTpl("itemid"), array("value" => $item_uuid,                     "hide" => true));
    $f->add(new HiddenTpl("itemlabel"), array("value" => $label,                         "hide" => true));
    $f->add(new HiddenTpl("gid"), array("value" => $_GET['gid'],                   "hide" => true));
    $f->add(new HiddenTpl("uuid"), array("value" => $_GET['uuid'],                  "hide" => true));

    /*$input = new TrFormElement(_T('Default menu item label', 'imaging'),        new InputTpl("default_mi_label"));
    $f->add($input,                                         array("value" => ''));
     */

    $check = new TrFormElement(_T('Selected by default', 'imaging'), new CheckboxTpl("do_default"));
    $f->add($check, array("value" => web_def_image_default() ? "checked" : ""));
    $check = new TrFormElement(_T('Displayed', 'imaging'), new CheckboxTpl("do_display"));
    $f->add($check, array("value" => web_def_image_hidden() ? "checked" : ""));
    $check = new TrFormElement(_T('Selected by default on WOL', 'imaging'), new CheckboxTpl("do_default_WOL"));
    $f->add($check, array("value" => web_def_image_default_WOL() ? "checked" : ""));
    $check = new TrFormElement(_T('Displayed on WOL', 'imaging'), new CheckboxTpl("do_display_WOL"));
    $f->add($check, array("value" => web_def_image_hidden_WOL() ? "checked" : ""));

    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();

}
