<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2011 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("modules/base/includes/users.inc.php");
require("includes/languages.php");

function _base_enableUser($paramsArr) {
    return xmlCall("base.enableUser", $paramsArr);
}

function _base_disableUser($paramsArr) {
    return xmlCall("base.disableUser", $paramsArr);
}

function _base_changeUserPasswd($paramsArr) {
    return xmlCall("base.changeUserPasswd", $paramsArr);
}

function _base_changeUserPrimaryGroup($uid, $group) {
    return xmlCall("base.changeUserPrimaryGroup", array($uid, $group));
}

function _base_delGroup($group) {
    $ret = xmlCall("base.delGroup", $group);
    if($ret == 2) {
        $msg = sprintf(_("Group %s can't be deleted.<br/>%s is the primary group of some users."), $group, $group);
    }
    else {
        $msg = sprintf(_("Group %s successfully deleted."), $group);
    }
    return array("code" => $ret, "info" => $msg);
}

function _base_completeUserEntry(&$entry) {
    $attrs = array("title", "mail", "mobile", "facsimileTelephoneNumber", "homePhone");
    foreach($attrs as $attr) {
        if (!isset($entry[$attr])) {
            $entry[$attr] = array(null);
        }
    }
}

/**
 * Function called before changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _base_verifInfo($FH, $mode) {

    global $error;

    $base_errors = "";
    $uid = $FH->getPostValue("uid");
    $pass = $FH->getPostValue("pass");
    $confpass = $FH->getPostValue("confpass");
    $homedir = $FH->getPostValue("homeDirectory");
    $primary = $FH->getPostValue("primary");

    if (!preg_match("/^[a-zA-Z0-9][A-Za-z0-9_.-]*$/", $uid)) {
        $base_errors .= _("User's name invalid !")."<br/>";
        setFormError("uid");
    }

    if ($mode == "add" && $uid && userExists($uid)) {
        $base_errors .= sprintf(_("The user %s already exists."), $uid)."<br/>";
        setFormError("uid");
    }

    if ($mode == "add" && $pass == '') {
        $base_errors .= _("Password is empty.")."<br/>";
        setFormError("pass");
    }

    if ($pass != $confpass) {
        $base_errors .= _("The confirmation password does not match the new password.")." <br/>";
        setFormError("pass");
        setFormError("confpass");
    }

    /* Check that the primary group name exists */
    if (!strlen($primary)) {
        $base_errors .= _("The primary group field can't be empty.")."<br />";
        setFormError("primary");
    }
    else if (!existGroup($primary)) {
        $base_errors .= sprintf(_("The group %s does not exist, and so can't be set as primary group."), $primary) . "<br />";
        setFormError("primary");
    }

    /* Check that the homeDir does not exists */
    if ($mode == "add") {
        if ($FH->getPostValue("createHomeDir") == "on" && $FH->getPostValue("ownHomeDir") != "on" && $uid) {
            getHomeDir($uid, $FH->getValue("homeDirectory"));
        }
    }
    else {
        /* If we want to move the userdir check the destination */
        if ($FH->isUpdated("homeDirectory"))
            getHomeDir($uid, $FH->getValue("homeDirectory"));
    }

    $error .= $base_errors;

    return $base_errors ? 1 : 0;

}

/**
 * Function called for changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _base_changeUser($FH, $mode) {

    global $result;
    global $error;

    $update = false;
    $base_errors = "";
    $uid = $FH->getPostValue("uid");

    if ($mode == "add") {
        // add mode
        if($FH->getPostValue("createHomeDir") == "on")
            $createHomeDir = true;
        else
            $createHomeDir = false;

        if($FH->getPostValue("ownHomeDir") == "on")
            $ownHomeDir = true;
        else
            $ownHomeDir = false;

        # create the user
        $ret = add_user($uid,
            $FH->getPostValue("pass"),
            $FH->getPostValue("givenName"),
            $FH->getPostValue("sn"),
            $FH->getPostValue("homeDirectory"),
            $createHomeDir, $ownHomeDir,
            $FH->getPostValue("primary")
        );
        $result .= $ret["info"];
        # password doesn't match the pwd policies
        # we set a random password for other plugins
        if($ret["code"] == 5) {
            $randomPass = uniqid(rand(), true);
            $FH->setPostValue("pass", $randomPass);
            $FH->setValue("pass", $randomPass);
        }
        # add mail attribute
        if ($FH->getPostValue('mail'))
            changeUserAttributes($uid, "mail", $FH->getPostValue("mail"));
        if ($FH->getPostValue('loginShell'))
            changeUserAttributes($uid, "loginShell",
                $FH->getPostValue('loginShell'));

    }
    else {
        // edit mode
        if ($FH->getPostValue("deletephoto")) {
            changeUserAttributes($uid, "jpegPhoto", null);
            $result .= _("User photo deleted")."<br />";
        }
        if ($FH->isUpdated("homeDirectory")) {
            move_home($uid, $FH->getValue("homeDirectory"));
            $result .= _(sprintf("Home user directory moved to %s",
                $FH->getValue("homeDirectory"))) . "<br />";
        }
    }

    // common stuff to add/edit mode
    if($FH->isUpdated('isBaseDesactive')) {
        $shells = getDefaultShells();
        if ($FH->getValue('isBaseDesactive') == "on") {
            changeUserAttributes($uid, 'loginShell', $shells['disabledShell']);
            $result .= _("User disabled")."<br />";
        }
        else {
            changeUserAttributes($uid, 'loginShell', $shells['enabledShell']);
            $result .= _("User enabled")."<br />";
        }
    }

    if($FH->isUpdated('telephoneNumber')) {
        changeUserTelephoneNumbers($uid, $FH->getValue("telephoneNumber"));
        $update = true;
    }

    if($FH->isUpdated('givenName') or $FH->isUpdated('sn')) {
        change_user_main_attr($uid, $uid, $FH->getValue('givenName'), $FH->getValue('sn'));
        $update = true;
    }

    foreach(array('title', 'mobile', 'facsimileTelephoneNumber', 'homePhone',
        'cn', 'mail', 'displayName', 'preferredLanguage') as $attr) {
        if ($FH->isUpdated($attr)) {
            changeUserAttributes($uid, $attr, $FH->getValue($attr));
            $update = true;
        }
    }

    /* Change photo */
    if (!empty($_FILES["photofilename"]["name"])) {
        $pfile = $_FILES["photofilename"]["tmp_name"];
        $size = getimagesize($pfile);
        if ($size["mime"] == "image/jpeg") {
            $maxwidth = 320;
            $maxheight = 320;
            if (in_array("gd", get_loaded_extensions())) {
                /* Resize file if GD extension is installed */
                $pfile = resizeJpg($_FILES["photofilename"]["tmp_name"],
                        $maxwidth, $maxheight);
            }
            list($width, $height) = getimagesize($pfile);
            if (($width <= $maxwidth) && ($height <= $maxheight)) {
                $obj = new Trans();
                $obj->scalar = "";
                $obj->xmlrpc_type = "base64";
                $f = fopen($pfile, "r");
                while (!feof($f)) $obj->scalar .= fread($f, 4096);
                fclose($f);
                unlink($pfile);
                changeUserAttributes($uid, "jpegPhoto", $obj, False);

            }
            else {
                $base_errors .= sprintf(_("The photo is too big. The max size is %s x %s.
                    Install php gd extension to resize the photo automatically"),
                    $maxwidth, $maxheight) . "<br/>";
            }
        }
        else $base_errors .= _("The photo is not a JPG file") . "<br/>";
    }

    if ($mode == "edit" && $update)
        $result .= _("User attributes updated") . "<br />";

    $error .= $base_errors;

    return $base_errors ? 1 : 0;
}

/**
 * Form on user edit page
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _base_baseEdit($FH, $mode) {

    $uid = $FH->getArrayOrPostValue("uid");

    $f = new DivForModule(_("User attributes"), "#F4F4F4");
    $f->push(new Table());

    if ($mode == "add") {
        $loginTpl = new InputTpl("uid",'/^[a-zA-Z0-9][A-Za-z0-9_.\-]*$/');
    } else {
        $loginTpl = new HiddenTpl("uid");
    }
    $f->add(
        new TrFormElement(_("Login"), $loginTpl),
        array("value" => $uid)
    );

    /*if($mode == "edit") {
        $lastlog = get_last_log_user($uid);
        if ($lastlog[0] != 0) {
        	$f->add(
        	    new LinkTrFormElement(_("Last action"), new HiddenTpl("lastaction")),
                array("value" => urlStr("base/users/loguser", array("user" => $uid)), "name" => $lastlog[1][0]["date"])
            );
        }
    }*/

    $f->add(
        new TrFormElement(_("Password"), new PasswordTpl("pass")),
        array("value" => "")
    );
    $f->add(
        new TrFormElement(_("Confirm password"), new PasswordTpl("confpass")),
        array("value" => "")
    );

    $f->add(
        new TrFormElement(_("Photo"), new ImageTpl("jpegPhoto")),
        array("value" => $FH->getArrayOrPostValue("jpegPhoto"), "action" => $mode)
    );

    $f->add(
        new TrFormElement(_("Last name"), new InputTpl("sn")),
        array("value"=> $FH->getArrayOrPostValue("sn"))
    );

    $f->add(
        new TrFormElement(_("First name"), new InputTpl("givenName")),
        array("value"=> $FH->getArrayOrPostValue("givenName"))
    );

    $f->add(
        new TrFormElement(_("Title"), new InputTpl("title")),
        array("value"=> $FH->getArrayOrPostValue("title"))
    );

    $f->add(
        new TrFormElement(_("Email address"), new MailInputTpl("mail")),
        array("value"=> $FH->getArrayOrPostValue("mail"))
    );

    $f->pop();

    $phoneregexp = "/^[a-zA-Z0-9(/ +\-]*$/";

    $tn = new MultipleInputTpl("telephoneNumber",_("Telephone number"));
    $tn->setRegexp($phoneregexp);
    $f->add(
        new FormElement(_("Telephone number"), $tn),
        $FH->getArrayOrPostValue("telephoneNumber", "array")
    );

    $f->push(new Table());

    $f->add(
        new TrFormElement(_("Mobile number"), new InputTpl("mobile", $phoneregexp)),
        array("value" => $FH->getArrayOrPostValue("mobile"))
    );

    $f->add(
        new TrFormElement(_("Fax number"), new InputTpl("facsimileTelephoneNumber", $phoneregexp)),
        array("value" => $FH->getArrayOrPostValue("facsimileTelephoneNumber"))
    );

    $f->add(
        new TrFormElement(_("Home phone number"), new InputTpl("homePhone", $phoneregexp)),
        array("value" => $FH->getArrayOrPostValue("homePhone"))
    );

    $languages = new SelectItem("preferredLanguage");
    $labels = array(_("Choose language")) + array_values(getLanguages());
    $values = array("") + array_keys(getLanguages());
    $languages->setElements($labels);
    $languages->setElementsVal($values);
    $f->add(
        new TrFormElement(_("Preferred language"), $languages),
        array("value" => $FH->getArrayOrPostValue("preferredLanguage"))
    );

    $checked = "checked";
    if ($FH->getArrayOrPostValue("loginShell") != '/bin/false')
        $checked = "";
    $f->add(
        new TrFormElement(_("User is disabled, if checked"), new CheckboxTpl("isBaseDesactive"),
            array("tooltip"=>_("A disabled user can't log in any UNIX services. <br/>
                                Her/his login shell command is replaced by /bin/false"))
            ),
        array("value" => $checked)
    );

    /* Primary group */
    $groupsTpl = new SelectItem("primary");
    $all_groups = search_groups();
    $groups = array();
    foreach($all_groups as $key => $infos) {
        $groups[] = $infos[0];
    }
    $groupsTpl->setElements($groups);
    if ($mode == "add") {
        $primary = getUserDefaultPrimaryGroup();
    }
    else if($mode == "edit") {
        /* In case of error, display the POST values */
        if ($FH->isUpdated("primary"))
            $primary = $FH->getValue("primary");
        else {
            $primary = getUserPrimaryGroup($uid);
            /* If the group is not an LDAP group */
            if (!in_array($primary, $groups)) {
                $primaryGroups = $groups;
                $primaryGroups[] = $primary;
                $groupsTpl->setElements($primaryGroups);
            }
        }
    }
    $f->add(
        new TrFormElement(_("Primary group"), $groupsTpl),
        array("value" => $primary)
    );

    /* Secondary groups */
    $groupsTpl = new MembersTpl("secondary");
    $groupsTpl->setTitle(_("User's groups"), _("All groups"));
    // get the user's groups
    /* In case of error, display the POST values */
    if ($FH->getPostValue("secondary"))
            $user_groups = $FH->getPostValue("secondary");
    else {
        if ($mode == 'edit')
            $user_groups = getUserSecondaryGroups($uid);
        else
            $user_groups = array();
    }
    $member = array();
    foreach($user_groups as $group) {
        $member[$group] = $group;
    }
    // get all groups
    $available = array();
    foreach($groups as $group) {
        if (!in_array($group, $member))
            $available[$group] = $group;
    }

    $f->add(
        new TrFormElement(_("Secondary groups"), $groupsTpl),
        array("member" => $member, "available" => $available)
    );

    $f->pop();
    $f->push(new DivExpertMode());
    $f->push(new Table());

    $f->add(
        new TrFormElement(_("Home directory"), new InputTpl("homeDirectory")),
        array("value" => $FH->getArrayOrPostValue("homeDirectory"))
    );

    if ($mode == "add") {
        $f->add(
            new TrFormElement(_("Create home directory on filesystem"), new CheckboxTpl("createHomeDir")),
            array("value" => "checked")
        );
        $f->add(
            new TrFormElement(_("Force to use the home directory if it exists"), new CheckboxTpl("ownHomeDir"),
                array("tooltip" => _("Warning: an existing directory may belong to another user !"))),
            array("value" => "")
        );
    }

    $f->add(
        new TrFormElement(_("Login shell"), new InputTpl("loginShell")),
        array("value" => $FH->getArrayOrPostValue("loginShell"))
    );

    $f->add(
        new TrFormElement(_("Common name"), new InputTpl("cn"),
            array("tooltip" => _("This field is used by some LDAP clients (for example Thunderbird address book) to display user entries."))),
        array("value"=> $FH->getArrayOrPostValue("cn"))
	);

    $f->add(
        new TrFormElement(_("Preferred name to be used"), new InputTpl("displayName"),
            array("tooltip" => _("This field is used by SAMBA (and other LDAP clients) to display user name."))),
        array("value"=> $FH->getArrayOrPostValue("displayName"))
    );

    if ($mode == "edit") {
        $f->add(
            new TrFormElement(_("UID"), new HiddenTpl("uidNumber")),
            array("value"=> $FH->getArrayOrPostValue("uidNumber"))
        );

        $f->add(
            new TrFormElement(_("GID"), new HiddenTpl("gidNumber")),
            array("value"=> $FH->getArrayOrPostValue("gidNumber"))
        );
    }

    $f->pop();
    $f->pop();

    return $f;
}

/**
 * Resize a jpg file if it is greater than $maxwidth or $maxheight
 *
 * @returns: the file name of the resized JPG file
 */
function resizeJpg($source, $maxwidth, $maxheight) {
    list($width, $height) = getimagesize($source);
    if (($width > $maxwidth) || ($height > $maxheight)) {
        if ($width > $height) {
            $newwidth = $maxwidth;
            $newheight = $newwidth * $height / $width;
        } else {
            $newheight = $maxheight;
            $newwidth = $newheight * $width / $height;
        }
        $image = imagecreatefromjpeg($source);
        $newimage = imagecreatetruecolor($newwidth, $newheight);
        imagecopyresized($newimage, $image, 0, 0, 0, 0, $newwidth, $newheight, $width, $height);
        $ret = tempnam("/notexist", ".jpg");
        imagejpeg($newimage, $ret);
        imagedestroy($image);
        imagedestroy($newimage);
    } else {
        /* No resize needed */
        $ret = $source;
    }
    return $ret;
}

?>
