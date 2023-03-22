<?php
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
require_once('modules/imaging/includes/post_install_script.php');
require_once("modules/xmppmaster/includes/xmlrpc.php");
function expertModeDisplay($f, $has_profile, $type, $menu, $opts, $target, $real_target) {
    if (!$has_profile) {
        $f->add(new TitleElement(sprintf(_T("%s menu parameters", "imaging"), ($type=='' ? _T('Computer', 'imaging') : _T('Profile', 'imaging') ))));
        $f->push(new Table());

        $f->add(
            new TrFormElement(_T('Default menu label', 'imaging'),
            new InputTpl("default_m_label")), array("value" => $menu['default_name'])
        );
        $f->add(
            new TrFormElement(_T('Menu timeout', 'imaging'),
            new InputTpl("default_m_timeout")), array("value" => $menu['timeout'])
        );

        foreach($opts as $key => $str) {
            if ($menu[$key]) {
                $value = 'CHECKED';
            } else {
                $value = '';
            }
            $f->add(new TrFormElement($str, new CheckBoxTpl($key)),
                array("value" => $value));
        }
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
                /* $f->add(
                    new TrFormElement(_T("Keyboard mapping (empty/fr)", "imaging"),
                    new InputTpl("boot_keyboard")), array("value" => "")
                ); */
        $f->pop();

    } else {
        $f->add(new HiddenTpl("default_m_label"),                    array("value" => $menu['default_name'],            "hide" => True));
        $f->add(new HiddenTpl("default_m_timeout"),                    array("value" => $menu['timeout'],            "hide" => True));

        $f->add(new HiddenTpl("rest_type"),           array("value" => $rest_selected,            "hide" => True));
        $f->add(new HiddenTpl("rest_wait"),           array("value" => $menu['timeout'],          "hide" => True));
        $f->add(new HiddenTpl("boot_xpm"),            array("value" => $menu['background_uri'],   "hide" => True));
        $f->add(new HiddenTpl("boot_msg"),            array("value" => $menu['message'],          "hide" => True));

        foreach($opts as $key => $str) {
            if ($menu[$key]) {
                $value = 'CHECKED';
            } else {
                $value = '';
            }
            $f->add(new HiddenTpl($str),              array("value" => $value,            "hide" => True));
        }
    }

    if ($type == '') {
        $f->add(new TitleElement(_T("Target options", "imaging")));
        $f->push(new Table());
        $local_kernel_parameters = web_def_kernel_parameters();
        $local_image_parameters = web_def_image_parameters();
        if (isset($real_target)) {
            if ($real_target != null) {
                $local_kernel_parameters = $real_target['kernel_parameters'];
                $local_image_parameters = $real_target['image_parameters'];
            }
            /* Make checkbox to force raw backup mode */
            if (($real_target != null) && (!empty($real_target['raw_mode']))) {
                $rawmode = "CHECKED";
            } else {
                $rawmode = "";
            }
        } else {
            if ($target != null) {
                $local_kernel_parameters = $target['kernel_parameters'];
                $local_image_parameters = $target['image_parameters'];
            }
            /* Make checkbox to force raw backup mode */
            if (($target != null) && (!empty($target['raw_mode']))) {
                $rawmode = "CHECKED";
            } else {
                $rawmode = "";
            }
        }

        $f->add(
            new TrFormElement(_T("Kernel parameters", "imaging"),
            new InputTpl("target_opt_kernel")), array("value" => $local_kernel_parameters)
        );
        $f->add(
            new TrFormElement(_T("Image parameters", "imaging"),
            new InputTpl("target_opt_image")), array("value" => $local_image_parameters)
        );

        $f->add(
            new TrFormElement(_T("Force raw backup mode", "imaging"),
            new CheckboxTpl("target_opt_raw_mode")),
            array("value" => $rawmode)
        );
    } else {
        $f->add(new HiddenTpl('target_opt_kernel'),       array("value" => ($target != null?$target['kernel_parameters']:web_def_kernel_parameters()),            "hide" => True));
        $f->add(new HiddenTpl('target_opt_image'),        array("value" => ($target != null?$target['image_parameters']:web_def_image_parameters()),              "hide" => True));
        $f->add(new HiddenTpl('target_opt_raw_mode'),     array("value" => ($target != null?$target['raw_mode']:''),                                              "hide" => True));
    }
}

$is_unregistering = False;
if (!isset($is_registering) || $is_registering == '') {
    $is_registering = False;
}

$params = getParams();

$opts = array(
    'hidden_menu' => _T("Hide menu (shortcut to show it : Shift - Alt - Shift)", 'imaging'),
    'bootcli' => _T('GRUB command line access', 'imaging'),
    'dont_check_disk_size' => _T('Do not check hard disk size', 'imaging'),
    'update_nt_boot' => _T('Update the NT boot loader if the hard disk has changed', 'imaging'),
    'disklesscli' => _T('Diskless Linux command line access', 'imaging')
);

/*
 * Enter here on page validation
 */
if (isset($_POST["bvalid"])) {
    /*
     * type: 'group' for a profile, '' for a single computer
     */
    $type = $_POST["type"];
    $target_uuid = $_POST['target_uuid'];
    $target_name = $_POST['target_name'];

    if ($type == 'group') { // profile
        xmlrpc_setfromxmppmasterlogxmpp(sprintf(_T("choose network profile for group %s", "imaging"), urldecode($label), $target_name),
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        /*
         * choose_network_profile reminder...
         * $_POST['choose_network_MachineUUID'] = NetworkUUID
         */
        $choose_network_profile = array();
        foreach ($_POST as $key => $value) {
            /*
             * Feed $choose_network_profile
             * $choose_network_profile = array($machineUUID => $networkUUID, etc..)
             */
            if (startswith($key, "choose_network"))
                $choose_network_profile[substr($key, 15)] = $value;
        }
    }
    else { // single machine
        xmlrpc_setfromxmppmasterlogxmpp(sprintf(_T("choose network profile for machine %s", "imaging"), urldecode($label), $target_name),
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        $choose_network = $_POST["choose_network"];
    }

    /*
     * default_m_ is for boot menu
     */
    $params['default_name'] = $_POST['default_m_label'];
    $params['timeout'] = $_POST['default_m_timeout'];
    foreach($opts as $key => $str) {
        $params[$key] = $_POST[$key];
    }
    /*
    rest_wait is MTFTP timeout
    $params['timeout'] = $_POST['rest_wait'];
     */
    $params['background_uri'] = $_POST['boot_xpm'];
    $params['message'] = $_POST['boot_msg'];
    $params['target_name'] = $target_name;
    $params['target_uuid'] = $target_uuid;
    $params['target_opt_kernel'] = $_POST['target_opt_kernel'];
    $params['target_opt_image'] = $_POST['target_opt_image'];

    if ($type == 'group') { // Profile
        if (count($choose_network_profile) > 0) {
            $params["choose_network_profile"] = $choose_network_profile;
        }
    }
    else { // Single machine
        if ($choose_network != Null && $choose_network != '') {
            $params["choose_network"] = $choose_network;
        }
    }

    $params['target_opt_parts'] = array();
    if (isset($_POST['check_disk'])) {
        foreach($_POST['check_disk'] as $disk => $parts) {
            foreach($parts as $part => $value) {
                $params['target_opt_parts'][] = array($disk, $part);
            }
        }
    }

    $params['target_opt_raw_mode'] = $_POST['target_opt_raw_mode'];

    if ($type == '') { // single computer
        $ret = xmlrpc_setMyMenuComputer($target_uuid, $params);
        $params['uuid'] = $target_uuid;
    } else { // Profile
        $ret = xmlrpc_setMyMenuProfile($target_uuid, $params);
        $params['gid'] = $target_uuid;
    }

    # remove some useless
    unset($params['message']);
    unset($params['default_name']);
    unset($params['background_uri']);
    $params['hostname'] = $params['target_name'];

    // Go to images list
    if ($ret[0] and !isXMLRPCError()) {
        if ($type == 'group') { // Imaging group
            // Synchronize location
            $location = xmlrpc_getProfileLocation($target_uuid);
            xmlrpc_synchroLocation($location);
        }
        if ($is_registering) {
            $str = sprintf(_T("Boot menu is created for <strong>%s</strong>.", "imaging"), $target_name);
        } else {
            $str = sprintf(_T("Boot menu modified for <strong>%s</strong>.", "imaging"), $target_name);
        }
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        new NotifyWidgetSuccess($str);
        if ($is_registering) {
            if ($type == 'group') { // Imaging group
                header("Location: ".urlStrRedirect("imaging/manage/".$type."imgtabs/".$type."tabbootmenu", $params));
            }
            else {
                header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabbootmenu", $params));
            }
            exit;
        } else {
            /* Reload the configure tab to get the synchro button */
            if ($type == 'group') { // Imaging group
                header("Location: ".urlStrRedirect("imaging/manage/".$type."imgtabs/".$type."tabconfigure", $params));
            }
            else {
                header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabconfigure", $params));
            }
            exit;
        }
    } elseif ($ret[0]) {
        if ($is_registering) {
            if ($type == 'group') { // Imaging group
                header("Location: ".urlStrRedirect("imaging/manage/".$type."imgtabs/".$type."tabbootmenu", $params));
            }
            else {
                header("Location: ".urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabbootmenu", $params));
            }
            exit;
        }
    } else {
        $str = sprintf(_T("Error generating the menu : %s", "imaging"), $ret[1]);
        new NotifyWidgetFailure($str);
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
    }
}

/*
 * Unregister computer section in 2 steps:
 *      1/ Display a warning page (are you sure you want to unregister ?) => bunregister
 *      2/ unregister computer => bunregister2
 */

// Step 1: Display warning message
if (isset($_POST["bunregister"])) {
    $type = $_POST["type"];
    $target_uuid = $_POST['target_uuid'];
    $target_name = $_POST['target_name'];
    $params['target_uuid'] = $target_uuid;
    $params['target_name'] = $target_name;
    $msg = _T("You are going to unregister this computer from the imaging module, are you sure you want to do that?", "imaging");

    $f = new ValidatingForm();
    $f->add(new TitleElement($msg, 3));
    $f->push(new Table());

    $f->add(new TrFormElement(_T("Do you want a backup to be done ?", "imaging"), new CheckBoxTpl("backup")), array("value" => ''));

    $f->add(new HiddenTpl("target_uuid"),                    array("value" => $target_uuid,            "hide" => True));
    $f->add(new HiddenTpl("target_name"),                    array("value" => $target_name,            "hide" => True));
    $f->add(new HiddenTpl("type"),                           array("value" => $type,                   "hide" => True));

    $f->pop();
    $f->addButton("bunregister2", _T("Unregister this computer", 'imaging'));
    $f->addButton("cancel", _T("Cancel", "imaging"), 'btnSecondary');
    $f->display();
}
// Step 2: unregister computer
else if (isset($_POST["bunregister2"])) {
    $type = $_POST["type"];
    $target_uuid = $_POST['target_uuid'];
    $target_name = $_POST['target_name'];
    $params['target_uuid'] = $target_uuid;
    $params['target_name'] = $target_name;
    $params['backup'] = $_POST['backup'];

    $ret = xmlrpc_delComputersImaging(array($target_uuid), ($params['backup'] ? true : false));
    if ($ret[0] and !isXMLRPCError()) {
        $str= sprintf(_T("The computer %s has correctly been unregistered from imaging", 'imaging'), $target_name);
        new NotifyWidgetSuccess($str);
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');

        unset($_SESSION["imaging.isComputerRegistered_".$target_uuid]);
        header("Location: " . urlStrRedirect("base/computers/register_target", $params));
        exit;
    }
    else {
        $str = sprintf(_T("Failed to unregister the computer %s", 'imaging'), $target_name);
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        new NotifyWidgetFailure($str);
    }
    $is_unregistering = True;
}
// Display register page form
else {
    /*
     * type: 'group' for a profile, '' for a single computer
     */
    $type = $_GET["type"];
    $target_uuid = $_GET['target_uuid'];
    $target_name = $_GET['target_name'];

    $f = new ValidatingForm();

    // Set title
    if ($type == '') { // Computer
        if (!xmlrpc_isComputerRegistered($target_uuid) && !xmlrpc_isComputerInProfileRegistered($target_uuid) ) {
            $f->add(new TitleElement(sprintf(_T("Register computer '%s'", "imaging"), $target_name)));
        }
    } else { // Profile
        if (!xmlrpc_isProfileRegistered($target_uuid)) {
            $f->add(new TitleElement(sprintf(_T("Imaging activation for group '%s'", "imaging"), $target_name)));
        }
    }

    // Get boot menu
    if ($type == '') { // Computer
        $ret = xmlrpc_getMyMenuComputer($target_uuid);
    } else { // Profile
        $ret = xmlrpc_getMyMenuProfile($target_uuid);
    }
    if (!$ret[0] && $ret[1] == 'ERROR') {
        $err_msg = getPulse2ErrorString($ret[2], $ret[3]);
    } else {
        list($whose, $menu) = $ret;
    }

    /*
     * whose is a list who come from python imaging database code: [uuid, type, target[0].toH]
     * menu is the target boot menu
     */
    if (!$whose && !$menu) {
        if ($type == '') {
            $msg = _T("To register, you must first set a default menu to the imaging server that manages the entity of this computer.", "imaging");
        } else {
            $msg = _T("To register, you must first set a default menu to the imaging server that manages the entities of the computers that belongs to this profile.", "imaging");
        }
        $f->add(new TitleElement($msg, 3));
        $f->display();
    } else if (($type == '') && ($is_registering) && (xmlrpc_checkComputerForImaging($target_uuid) != 0)) {
        $msg = _T("The computer either doesn't have a MAC address, either has more than one MAC address or the only NIC doesn't have any network mask. It can't be registered into the imaging module.", "imaging");
        $f->add(new TitleElement($msg, 3));
        $f->display();
    } else if (($type == 'group') && ($is_registering) && ($checkProfileForImagingStatus = xmlrpc_checkProfileForImaging($target_uuid) and $checkProfileForImagingStatus != 0)) {
        if ($checkProfileForImagingStatus != 2) {
            $msg = _T("The profile can't be registered into the imaging module.", "imaging");
            $f->add(new TitleElement($msg, 3));
        }
        else {
            // form preseeding
            $f->add(new HiddenTpl("target_uuid"),                    array("value" => $target_uuid,            "hide" => True));
            $f->add(new HiddenTpl("target_name"),                    array("value" => $target_name,            "hide" => True));
            $f->add(new HiddenTpl("type"),                           array("value" => $type,                   "hide" => True));

            $profileNetworks = xmlrpc_getProfileNetworks($target_uuid);
            foreach ($profileNetworks as $networks) {
                $networks = $networks[1];
                foreach (range(0, count($networks['ipHostNumber']) - 1) as $i) {
                    $ip=explode(":", $networks['ipHostNumber'][$i] );
                    if(filter_var($ip[0], FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) == ""){
                        unset($networks['ipHostNumber'][$i]);
                        unset($networks['macAddress'][$i]);
                        unset($networks['networkUuids'][$i]);
                        unset($networks['domain'][$i]);
                    }
                }

                // Remove dupplicate entries

                $tabip = array();
                $idkey = array();
                foreach ($networks['ipHostNumber'] as $key=>$val) {
                    if (!in_array($val, $tabip))
                    {
                        $tabip[] =  $val;
                    }
                    else{
                        $idkey[]=$key;
                    }
                }
                foreach ($idkey as $vv){
                    unset($networks['ipHostNumber'][$vv]);
                    unset($networks['macAddress'][$vv]);
                    unset($networks['networkUuids'][$vv]);
                    unset($networks['domain'][$vv]);
                    unset($networks['subnetMask'][$vv]);
                }
                // Reinitialize the array's index
                $networks['ipHostNumber'] = array_values($networks['ipHostNumber']);
                $networks['macAddress'] = array_values($networks['macAddress']);
                $networks['networkUuids'] = array_values($networks['networkUuids']);
                $networks['domain'] = array_values($networks['domain']);
                $networks['subnetMask'] = array_values($networks['subnetMask']);

                if (is_array($networks) && count($networks) > 1 and isset($networks['macAddress'])) {
                    if (count($networks['macAddress']) > 1) {
                        $f->push(new Table());
                        $macs_choice = new MySelectItem("choose_network_" . $networks['objectUUID'][0], 'exclusive_orders');
                        $elements = array();
                        $values = array();
                        foreach (range(0, count($networks['macAddress']) - 1) as $i) {
                            $elements[] = sprintf("%s / %s", $networks['ipHostNumber'][$i], $networks['macAddress'][$i]);
                            $values[] = $networks['networkUuids'][$i];
                        }
                        $macs_choice->setElements($elements);
                        $macs_choice->setElementsVal($values);
                        $f->add(new TrFormElement(_T("Computer:"), new SpanElement($networks['fullname'])));
                        $f->add(new TrFormElement(_T("Choose the MAC address you want to use", "imaging"), $macs_choice));
                        $f->pop();
                    } elseif (count($networks['macAddress']) == 1) {
                        $f->add(new HiddenTpl("choose_network_" . $networks['objectUUID'][0]),
                            array(
                                "value" => $networks['networkUuids'][0],
                                "hide" => True,
                            )
                        );
                    }
                }
            }
            if (!isExpertMode()) {
                $f->add(new TitleElement(_T("Please switch to expert mode now if you want to change more parameters.", "imaging"), 3));
            } else {
                $f->add(new TitleElement(_T("You can switch to standard mode now if you want less parameters.", "imaging"), 3));
            }

            $f->push(new DivExpertMode());

            expertModeDisplay($f, $has_profile, $type, $menu, $opts, $target, $real_target);

            $f->pop();

            $f->addValidateButton("bvalid");
        }
        $f->display();
    }
    else {
        $target = null;
        $real_target = null;
        $has_profile = False;
        if (!$whose) {
            if ($type == '') {
                $msg = _T("The default values for the imaging parameters will be inherited from the imaging server that manages the entity that owns this computer.", "imaging");
            }
            else {
                $msg = _T("The default values for the imaging parameters will be inherited from the imaging server that manages the entities of the computers that belongs to this profile.", "imaging");
            }

            $f->add(new TitleElement($msg, 3));
        }
        else {
            $target = $whose[2];
            if ($whose[1] == 2 && $type == '') { #PROFILE
                if (count($whose) > 3) {
                    $real_target = $whose[3];
                }
                $has_profile = True;
                $f->add(new TitleElement(sprintf(_T("The default values displayed here come from this %s's profile menu.", "imaging"), ($type==''?'computer':'profile')), 4));
            }
        }

        // form preseeding
        $f->add(new HiddenTpl("target_uuid"),                    array("value" => $target_uuid,            "hide" => True));
        $f->add(new HiddenTpl("target_name"),                    array("value" => $target_name,            "hide" => True));
        $f->add(new HiddenTpl("type"),                           array("value" => $type,                   "hide" => True));

        if (($type == '') && (!$is_registering) && (!$is_unregistering)) {
            /* Add disks and partitions selector widget for registered computers
            only, not profiles */
            $inventory = xmlrpc_getPartitionsToBackupRestore($target_uuid);
            if (!empty($inventory)) {
                $f->add(new TitleElement(_T("Hard disks and partitions selection to backup", "imaging")));
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
                    "extraArg"=>'onclick="jQuery(\''. $divid .'\').toggle();"'));
                $f->pop();
                $diskdiv = new Div(array("id" => $divid));
                $diskdiv->setVisibility($value == "CHECKED");
                $f->push($diskdiv);
                $f->push(new Table());
                ksort($parts);
                foreach($parts as $part) {
                    $partnum = $part['num'] + 1;
                    $ptype = $parttype[$part['type']];
                    $length = humanSize($part['length'] * 512);
                    $msg = sprintf(_T("Partition number: %d", "imaging"),
                        $partnum);
                    $inputvar = "check_disk[$disk][$partnum]";
                    $text = "$ptype $length";
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
        /*
         * Network card selection
         * If more than one network card, display a select form to select the one to use with imaging
         */
        if ($is_registering && $type == '') {
            $networks = xmlCall('base.getComputersNetwork', array(array('uuid'=>$_GET["target_uuid"])));
            $networks = $networks[0][1];
            foreach (range(0, count($networks['ipHostNumber']) - 1) as $i) {
                $ip = explode(":", $networks['ipHostNumber'][$i]);
                if(filter_var($ip[0], FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) == ""){
                    unset($networks['ipHostNumber'][$i]);
                    unset($networks['macAddress'][$i]);
                    unset($networks['networkUuids'][$i]);
                    unset($networks['domain'][$i]);
                }
            }

            // Remove dupplicate entries

            $tabip = array();
            $idkey = array();
            foreach ($networks['ipHostNumber'] as $key=>$val) {
                if (!in_array($val, $tabip))
                {
                    $tabip[] =  $val;
                }
                else{
                    $idkey[]=$key;
                }
            }

            foreach ($idkey as $vv){
                unset($networks['ipHostNumber'][$vv]);
                unset($networks['macAddress'][$vv]);
                unset($networks['networkUuids'][$vv]);
                unset($networks['domain'][$vv]);
                unset($networks['subnetMask'][$vv]);
            }

            // Reinitialize the array's index
            $networks['ipHostNumber'] = array_values($networks['ipHostNumber']);
            $networks['macAddress'] = array_values($networks['macAddress']);
            $networks['networkUuids'] = array_values($networks['networkUuids']);
            $networks['domain'] = array_values($networks['domain']);
            $networks['subnetMask'] = array_values($networks['subnetMask']);

            if (is_array($networks) && count($networks) > 1 and isset($networks['macAddress'])) {
                if (count($networks['macAddress']) > 1) {
                    $f->push(new Table());
                    $macs_choice = new MySelectItem("choose_network", 'exclusive_orders');
                    $elements = array();
                    $values = array();
                    foreach (range(0, count($networks['macAddress']) - 1) as $i) {
                        $elements[] = sprintf("%s [%s]", $networks['ipHostNumber'][$i], $networks['macAddress'][$i]);
                        $values[] = $networks['networkUuids'][$i];
                    }
                    $macs_choice->setElements($elements);
                    $macs_choice->setElementsVal($values);
                    $f->add(new TrFormElement(_T("Choose the MAC address you want to use", "imaging"), $macs_choice));
                    $f->pop();
                } elseif (count($networks['macAddress']) == 1) {
                    $f->add(new HiddenTpl("choose_network"),           array("value" => $networks['networkUuids'][0],            "hide" => True));
                }
            }
        }

        if (!isExpertMode()) {
            $f->add(new TitleElement(_T("Please switch to expert mode now if you want to change more parameters.", "imaging"), 3));
        } else {
            $f->add(new TitleElement(_T("You can switch to standard mode now if you want less parameters.", "imaging"), 3));
        }

        $f->push(new DivExpertMode());
        expertModeDisplay($f, $has_profile, $type, $menu, $opts, $target, $real_target);

        $f->pop();

        $f->addValidateButton("bvalid");
        if ($type == '' && !$has_profile && ($whose && $whose[0] == $target['uuid'])) {
            $f->addButton("bunregister", _T("Unregister this computer", 'imaging'), 'btnSecondary');
        }

        $f->pop(); // Div expert mode

        $f->display();
    }
}
?>
