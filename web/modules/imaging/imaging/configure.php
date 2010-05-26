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

/*
 * This page allows:
 *  - to register a computer or a profile the imaging module
 *  - to change the boot menu parameters of a computer or a profile
 */


require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');
require_once('modules/imaging/includes/part-type.inc.php');

if (!isset($is_registering)) {
    $is_registering = False;
}
$params = getParams();

if (isset($_POST["bvalid"])) {
    $type = $_POST["type"];
    $target_uuid = $_POST['target_uuid'];
    $target_name = $_POST['target_name'];

    $from = $_POST['from'];
    $loc_name = $_POST['loc_name'];
    $item_uuid = $_POST['itemid'];

    $label = urldecode($_POST['itemlabel']);

    $params['default_name'] = $_POST['default_m_label'];
    $params['timeout'] = $_POST['rest_wait'];
    $params['background_uri'] = $_POST['boot_xpm'];
    $params['message'] = $_POST['boot_msg'];
    $params['protocol'] = $_POST['rest_type'];
    $params['target_name'] = $target_name;
    $params['target_uuid'] = $target_uuid;
    $params['target_opt_kernel'] = $_POST['target_opt_kernel'];
    $params['target_opt_image'] = $_POST['target_opt_image'];

    $params['target_opt_parts'] = array();
    if (isset($_POST['check_disk'])) {
        foreach($_POST['check_disk'] as $disk => $parts) {
            foreach($parts as $part => $value) {
                $params['target_opt_parts'][] = array($disk, $part);
            }
        }
    }
    if ($type == '') {
        $ret = xmlrpc_setMyMenuComputer($target_uuid, $params);
        $params['uuid'] = $target_uuid;
    } else {
        $ret = xmlrpc_setMyMenuProfile($target_uuid, $params);
        $params['gid'] = $target_uuid;
    }

    # remove some useless
    unset($params['message']);
    unset($params['default_name']);
    unset($params['background_uri']);
    $params['hostname'] = $params['target_name'];
    // goto images list
    if ($ret[0] and !isXMLRPCError()) {
        if ($is_registering) {
            $str = sprintf(_T("Boot menu is created for <strong>%s</strong>.", "imaging"), $target_name);
        } else {
            $str = sprintf(_T("Boot menu modified for <strong>%s</strong>.", "imaging"), $target_name);
        }
        new NotifyWidgetSuccess($str);
        if ($is_registering) {
            header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabbootmenu", $params));
        } else {
            /* Reload the configure tab to get the synchro button */
            header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabconfigure", $params));
        }
    } elseif ($ret[0]) {
        if ($is_registering) {
            header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabbootmenu", $params));
        }
    } else {
        new NotifyWidgetFailure(sprintf(_T("Failed to synchronize those computers : %s", "imaging"), implode($ret[1], ", ")));
    }
}

$type = $_GET["type"];
$target_uuid = $_GET['target_uuid'];
$target_name = $_GET['target_name'];

$f = new ValidatingForm();

if ($type == '') {
    if (!xmlrpc_isComputerRegistered($target_uuid)) {
        $f->add(new TitleElement(sprintf(_T("Register computer '%s'", "imaging"), $target_name)));
    }
} else {
    if (!xmlrpc_isProfileRegistered($target_uuid)) {
        $f->add(new TitleElement(sprintf(_T("Register profile '%s'", "imaging"), $target_name)));
    }
}
if ($type == '') {
    list($whose, $menu) = xmlrpc_getMyMenuComputer($target_uuid);
} else {
    list($whose, $menu) = xmlrpc_getMyMenuProfile($target_uuid);
}

if (!$whose && !$menu) {
    if ($type == '') {
        $msg = _T("To register, you must first set a default menu to the imaging server that manages the entity of this computer.", "imaging");
    } else {
        $msg = _T("To register, you must first set a default menu to the imaging server that manages the entities of the computers that belongs to this profile.", "imaging");
    }
    $f->add(new TitleElement($msg, 3));
    $f->display();
} else if (($type == '')
           && ($is_registering)
           && (xmlrpc_checkComputerForImaging($target_uuid) != 0)) {
    $msg = _T("The computer either doesn't have a MAC address, either has more than one MAC address. It can't be registered into the imaging module.", "imaging");
    $f->add(new TitleElement($msg, 3));
    $f->display();
} else if (($type == 'group')
           && ($is_registering)
           && (xmlrpc_checkProfileForImaging($target_uuid) != 0)) {
    $msg = _T("The profile can't be registered into the imaging module.", "imaging");
    $f->add(new TitleElement($msg, 3));
    $f->display();
} else {
    $target = null;
    if (!$whose) {
        if ($type == '') {
            $msg = _T("The default values for the imaging parameters will be inherited from the imaging server that manages the entity that owns this computer.", "imaging");
        } else {
            $msg = _T("The default values for the imaging parameters will be inherited from the imaging server that manages the entities of the computers that belongs to this profile.", "imaging");
        }

        $f->add(new TitleElement($msg, 3));
    } else {
        $target = $whose[2];
        if ($whose[1] == 2 && $type == '') { #PROFILE
            $f->add(new TitleElement(sprintf(_T("The default values displayed here come from this %s's profile menu.", "imaging"), ($type==''?'computer':'profile')), 4));
        }
    }

    // form preseeding
    $f->add(new HiddenTpl("target_uuid"),                    array("value" => $target_uuid,            "hide" => True));
    $f->add(new HiddenTpl("target_name"),                    array("value" => $target_name,            "hide" => True));
    $f->add(new HiddenTpl("type"),                           array("value" => $type,                   "hide" => True));

    if (($type == '') && (!$is_registering)) {
        /* Add disks and partitions selector widget for registered computers
           only, not profiles */
        $inventory = xmlCall("imaging.getPartitionsToBackupRestore", $target_uuid);
        if (!empty($inventory)) {
            $f->add(new TitleElement(_T("Backup/restore hard disks and partitions selection", "imaging")));
        }
        ksort($inventory);
        foreach($inventory as $disk => $parts) {
            $disk = $disk + 1;
            $msg = sprintf(_T("Hard disk number: %d", "imaging"), $disk);
            $inputvar = "check_disk[$disk][0]";
            if (isset($parts["exclude"])) {
                $value = "";
                unset($parts["exclude"]);
            } else {
                $value = "CHECKED";
            }
            $divid = "disk_div$disk";
            $f->push(new DivForModule($msg, "#FFF"));
            $f->push(new Table());
            $f->add(new TrFormElement(_T("Select this hard disk", "imaging"), new CheckboxTpl($inputvar)),
                    array("value" => $value,
                          "extraArg"=>'onclick="toggleVisibility(\''. $divid .'\');"'));
            $f->pop();
            $diskdiv = new Div(array("id" => $divid));
            $diskdiv->setVisibility($value == "CHECKED");
            $f->push($diskdiv);
            $f->push(new Table());
            ksort($parts);
            foreach($parts as $part) {
                $partnum = $part['num'] + 1;
                $type = $parttype[$part['type']];
                $length = humanSize($part['length'] * 512);
                $msg = sprintf(_T("Partition number: %d", "imaging"),
                               $partnum);
                $inputvar = "check_disk[$disk][$partnum]";
                $text = "$type $length";
                if (isset($part["exclude"])) {
                    $value = "";
                    unset($part["exclude"]);
                } else {
                    $value = "CHECKED";
                }
                $f->add(new TrFormElement($msg,
                                          new CheckboxTpl($inputvar, $text)),
                        array("value" => $value));
            }
            $f->pop();
            $f->pop();
            $f->pop();
        }
    }

    $f->add(new TitleElement(_T("Please switch to expert mode now if you want to change more parameters.", "imaging"), 3));

    $f->push(new DivExpertMode());

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
/*    $f->add(
        new TrFormElement(_T("Keyboard mapping (empty/fr)", "imaging"),
        new InputTpl("boot_keyboard")), array("value" => "")
    ); */
    $f->pop();

    /* $f->add(new TitleElement(_T("Administration options", "imaging")));
    $f->push(new Table());
    $f->add(
        new TrFormElement(_T("Password for adding a new client", "imaging"),
        new InputTpl("misc_passwd")), array("value" => "")
    );
    $f->pop();*/

    $f->add(new TitleElement(_T("Target options", "imaging")));
    $f->push(new Table());
    $f->add(
        new TrFormElement(_T("Kernel parameters", "imaging"),
        new InputTpl("target_opt_kernel")), array("value" => ($target != null?$target['kernel_parameters']:web_def_kernel_parameters()))
    );
    $f->add(
        new TrFormElement(_T("Image parameters", "imaging"),
        new InputTpl("target_opt_image")), array("value" => ($target != null?$target['image_parameters']:web_def_image_parameters()))
    );

    $f->pop();

    $f->addValidateButton("bvalid");

    $f->pop(); // Div expert mode

    $f->display();
}

?>
