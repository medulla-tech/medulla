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

$location = getCurrentLocation();

if (isset($_POST["bconfirm"])) {
    $params = getParams();

    $item_uuid = $_POST['itemid'];
    $label = urldecode($_POST['itemlabel']);

    $params['default_name'] = $_POST['default_mi_label'];
    $params['hidden'] = ($_POST['do_display'] != 'on');
    $params['hidden_WOL'] = ($_POST['do_display_WOL'] != 'on');
    $params['default'] = ($_POST['do_default'] == 'on');
    $params['default_WOL'] = ($_POST['do_default_WOL'] == 'on');

    $ret = xmlrpc_addServiceToLocation($item_uuid, $location, $params);

    // goto images list 
    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Service <strong>%s</strong> added to default boot menu", "imaging"), $label);
        new NotifyWidgetSuccess($str);
         
        // Synchronize boot menu
        $ret = xmlrpc_synchroLocation($location);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for package server: %s", "imaging"), implode(', ', $ret[1])));
        }
        header("Location: " . urlStrRedirect("imaging/manage/service", $params));
    } elseif ($ret[0]) {
        header("Location: " . urlStrRedirect("imaging/manage/service", $params));
    } else {
        new NotifyWidgetFailure($ret[1]);
    }
}

if(isset($_GET['mod']))
    $mod = $_GET['mod'];
else 
    $mod = "none";

switch($mod) {
    case 'add':
        service_add($location);
        break;
    case 'edit':
        service_edit($location);
        break;
    default:
        service_add($location);
        break;
}

function service_add($location) {
    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    $f = new PopupForm(sprintf(_T("Add the boot service <b>%s</b> to the default boot menu", "imaging"), $label));

    $f->push(new Table());

    // form preseeding
    $f->add(new HiddenTpl("location"),                      array("value" => $location,                      "hide" => True));
    $f->add(new HiddenTpl("itemlabel"),                     array("value" => $label,                         "hide" => True));
    $f->add(new HiddenTpl("itemid"),                        array("value" => $item_uuid,                     "hide" => True));
    $f->add(new HiddenTpl("default_mi_label"),              array("value" => $label,                         "hide" => True));

    #    $input = new TrFormElement(_T('Default menu item label', 'imaging'),        new InputTpl("default_mi_label"));
    #$f->add($input,                                         array("value" => ''));
    

    $check = new TrFormElement(_T('Selected by default', 'imaging'), new CheckboxTpl("do_default"));
    $f->add($check,                                         array("value" => web_def_service_default() ? "checked" : ""));
    $check = new TrFormElement(_T('Displayed', 'imaging'), new CheckboxTpl("do_display"));
    $f->add($check,                                         array("value" => web_def_service_hidden() ? "checked" : ""));
    $check = new TrFormElement(_T('Selected by default on WOL', 'imaging'), new CheckboxTpl("do_default_WOL"));
    $f->add($check,                                         array("value" => web_def_service_default_WOL() ? "checked" : ""));
    $check = new TrFormElement(_T('Displayed on WOL', 'imaging'), new CheckboxTpl("do_display_WOL"));
    $f->add($check,                                         array("value" => web_def_service_hidden_WOL() ? "checked" : ""));
    
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
    
}

?>
