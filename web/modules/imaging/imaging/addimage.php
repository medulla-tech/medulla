<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
require_once('modules/imaging/includes/web_def.inc.php');

if (isset($_POST["bconfirm"])) {
    $params = getParams();
    if(isset($_POST['gid']) && $_POST['gid'] != '') {
        $type = 'group';
        $target_uuid = $_POST['gid'];
    } else {
        $type = '';
        $target_uuid = $_POST['uuid'];
    }

    $item_uuid = $_POST['itemid'];
    $label = stripslashes(urldecode($_POST['itemlabel']));

    $params['name'] = $_POST['default_mi_label'];
    $params['hidden'] = ($_POST['do_display'] != 'on');
    $params['hidden_WOL'] = ($_POST['do_display_WOL'] != 'on');
    $params['default'] = ($_POST['do_default'] == 'on');
    $params['default_WOL'] = ($_POST['do_default_WOL'] == 'on');

    $ret = xmlrpc_addImageToTarget($item_uuid, $target_uuid, $params, $type);

    // goto images list
    if ($ret[0] and !isXMLRPCError()) {
        /* insert notification code here if needed */
        header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabimages", $params));
    } elseif ($ret[0]) {
        header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabimages", $params));
    } else {
        new NotifyWidgetFailure($ret[1]);
        header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabimages", $params));
    }
}

if(isset($_GET['gid'])) {
    $type = 'group';
    $target_uuid = $_GET['gid'];
} else {
    $type = '';
    $target_uuid = $_GET['uuid'];
}

if(isset($_GET['mod']))
    $mod = $_GET['mod'];
else
    $mod = "none";

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

function image_add($type, $target_uuid) {
    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    $f = new PopupForm(sprintf(_T("Add the image <b>%s</b> to <b>%s</b>", "imaging"), $label, $params['hostname'])); # Need to get the name of the target

    $f->push(new Table());

    // form preseeding
    $f->add(new HiddenTpl("itemid"),                        array("value" => $item_uuid,                     "hide" => True));
    $f->add(new HiddenTpl("itemlabel"),                     array("value" => $label,                         "hide" => True));
    $f->add(new HiddenTpl("gid"),                           array("value" => $_GET['gid'],                   "hide" => True));
    $f->add(new HiddenTpl("uuid"),                          array("value" => $_GET['uuid'],                  "hide" => True));

    $f->add(new HiddenTpl("default_mi_label"),              array("value" => $label,                         "hide" => True));

    $check = new TrFormElement(_T('Selected by default', 'imaging'), new CheckboxTpl("do_default"));
    $f->add($check,                                         array("value" => web_def_image_default() ? "checked" : ""));
    $check = new TrFormElement(_T('Displayed', 'imaging'), new CheckboxTpl("do_display"));
    $f->add($check,                                         array("value" => web_def_image_hidden() ? "checked" : ""));
    $check = new TrFormElement(_T('Selected by default on WOL', 'imaging'), new CheckboxTpl("do_default_WOL"));
    $f->add($check,                                         array("value" => web_def_image_default_WOL() ? "checked" : ""));
    $check = new TrFormElement(_T('Displayed on WOL', 'imaging'), new CheckboxTpl("do_display_WOL"));
    $f->add($check,                                         array("value" => web_def_image_hidden_WOL() ? "checked" : ""));

    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();

}

?>
