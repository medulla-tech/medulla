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


require('modules/base/computers/localSidebar.php');
require("graph/navbar.inc.php");
 
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');

$params = getParams();

if (isset($_POST["bvalid"])) {
    $type = $_POST["type"];
    $target_uuid = $_POST['target_uuid'];

    /*$ret = xmlrpc_addImageToTarget($item_uuid, $target_uuid, $params);

    // goto images list 
    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Image <strong>%s</strong> added to boot menu", "imaging"), $label);
        new NotifyWidgetSuccess($str);
        header("Location: ".urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
    } elseif ($ret[0]) {
        header("Location: ".urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
    } else {
        new NotifyWidgetFailure($ret[1]);
    }*/
}

$type = $_GET["type"];
$target_uuid = $_GET['target_uuid'];
$target_name = $_GET['target_name'];

if ($type == '') {
    $p = new PageGenerator(sprintf(_T("Register your computer '%s'.", "imaging"), $target_name));
    list($whose, $menu) = xmlrpc_getMyMenuMachine($target_uuid);
} else {
    $p = new PageGenerator(sprintf(_T("Register your profile '%s'.", "imaging"), $target_name));
    list($whose, $menu) = xmlrpc_getMyMenuProfile($target_uuid);
}
$p->setSideMenu($sidemenu);
$p->display();

if (!$whose) {
    print sprintf(_T("<h4>The default values displayed here come from this %s's entity default menu.</h4>", "imaging"), ($type==''?'computer':'profile'));
} elseif ($whose == '') {
    print _T("", "imaging");
}

$f = new ValidatingForm();

$f->push(new Table());

// form preseeding
$f->add(new HiddenTpl("target_uuid"),                    array("value" => $target_uuid,            "hide" => True));
$f->add(new HiddenTpl("target_name"),                    array("value" => $target_name,            "hide" => True));
$f->add(new HiddenTpl("type"),                           array("value" => $type,                   "hide" => True));


$f->add(new TitleElement(sprintf(_T("%s menu parameters", "imaging"), ($type=='' ? _T('Computer', 'imaging') : _T('Profile', 'imaging') ))));
$f->push(new Table());

$f->add(
    new TrFormElement(_T('Default menu label', 'imaging'),
    new InputTpl("default_m_label")), array("value" => $menu['default_name'])
);
$f->pop();

$f->add(new TitleElement(_T("Restoration options", "imaging")));
$f->push(new Table());
$possible_protocols = web_def_possible_protocols();
$default_protocol = web_def_default_protocol(); 
$protocols_choices = array();
$protocols_values = array();

/* translate possibles protocols */
_T('nfs', 'imaging');
_T('tftp', 'imaging');
_T('mtftp', 'imaging');
foreach ($possible_protocols as $p) {
    if ($p['label']) {
        if ($p['label'] == $menu['protocol']) {
            $rest_selected = $p['imaging_uuid'];
        }
        if ($p['label'] == $default_protocol) {
            $p['label'] = _T($p['label'], 'imaging').' '._T('(default)', 'imaging');
        }
        $protocols_choices[$p['imaging_uuid']] = $p['label'];
        $protocols_values[$p['imaging_uuid']] = $p['imaging_uuid'];
    }
}

$rest_type = new RadioTpl("rest_type");

$rest_type->setChoices($protocols_choices);
$rest_type->setValues($protocols_values);
$rest_type->setSelected($rest_selected);
$f->add(
    new TrFormElement(_T("Restoration type", "imaging"), $rest_type)
);
$f->add(
    new TrFormElement(_T("Restoration: MTFTP maximum waiting (in sec)", "imaging"),
    new InputTpl("rest_wait")), array("value" => $menu['timeout'])
);
$f->pop();

$f->add(new TitleElement(_T("Boot options", "imaging")));
$f->push(new Table());
$f->add(
    new TrFormElement(_T("Full path to the XPM displayed at boot", "imaging"),
    new InputTpl("boot_xpm")), array("value" => $menu['background_uri'])
);
$f->add(
    new TrFormElement(_T("Message displayed during backup/restoration", "imaging"),
    new TextareaTpl("boot_msg")), array("value" => $menu['message']) //"Warning ! Your PC is being backed up or restored. Do not reboot !")
);
$f->add(
    new TrFormElement(_T("Keyboard mapping (empty/fr)", "imaging"),
    new InputTpl("boot_keyboard")), array("value" => "")
);
$f->pop();

$f->add(new TitleElement(_T("Administration options", "imaging")));
$f->push(new Table());
$f->add(
    new TrFormElement(_T("Password for adding a new client", "imaging"),
    new InputTpl("misc_passwd")), array("value" => "")
);
$f->pop();

$_GET["action"] = "save_configuration";
$f->addButton("bvalid", _T("Validate"));
$f->pop();
$f->display();




?>
