<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

function _base_infoUser($userObjClass) {
    if (array_search("posixAccount", $userObjClass)!==false) {
        print "posix ";
    }
}

function _base_enableUser($uid) {
    xmlCall("base.enableUser", array($uid));
}

function _base_disableUser($uid) {
    xmlCall("base.disableUser", array($uid));
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

function _base_verifInfo($postArr, $mode) {

    global $error;

    $nlogin = $postArr["uid"];
    $name = $postArr["name"];
    $firstname = $postArr["givenName"];
    $pass = $postArr["pass"];
    $confpass = $postArr["confpass"];
    $homedir = $postArr["homeDir"];
    $loginShell = $postArr["loginShell"];
    $cn = $postArr["cn"];

    if(isset($postArr["isBaseDesactive"])) {
        $desactive = $postArr["isBaseDesactive"];
    }
    else {
        $desactive = false;
    }

    if ($mode == "add" && $pass == '') {
        $error.= _("Password is empty.")."<br/>";
        setFormError("pass");
    }

    if ($pass != $confpass) {
        $error.= _("The confirmation password does not match the new password.")." <br/>";
        setFormError("pass");
    }

    if (!preg_match("/^[a-zA-Z0-9][A-Za-z0-9_.-]*$/", $nlogin)) {
        $error.= _("User's name invalid !")."<br/>";
        setFormError("login");
    }

    /* Check that the primary group name exists */
    $primary = $postArr["primary"];
    if (!strlen($primary)) {
        setFormError("primary");
        $error.= _("The primary group field can't be empty.")."<br />";
    }
    else if (!existGroup($primary)) {
        setFormError("primary");
        $error.= sprintf(_("The group %s does not exist, and so can't be set as primary group."), $primary) . "<br />";
    }
}

function _base_baseEdit($FH, $mode) {

    $uid = $FH->getArrayOrPostValue("uid");

    $f = new DivForModule(_T("Base plugin","base"), "#F4F4F4");
    $f->push(new Table());

    $ldapAccountLocked = False;
    if (in_array("ppolicy", $_SESSION["supportModList"])) {
        require_once("modules/ppolicy/includes/ppolicy-xmlrpc.php");
        if (isset($_GET['user']) && isAccountLocked($_GET["user"]) != 0) {
            $ldapAccountLocked = True;
            $em = new ErrorMessage(_("This account is locked by the LDAP directory."));
            print $em->display();
        }
    }

    if ($mode == "add") {
        $loginTpl = new InputTpl("uid",'/^[a-zA-Z0-9][A-Za-z0-9_.-]*$/');
    } else {
        $loginTpl = new HiddenTpl("uid");
    }
    $f->add(
        new TrFormElement(_("Login"), $loginTpl),
        array("value" => $uid)
    );

    if($mode == "edit") {
        $lastlog = get_last_log_user($uid);
        if ($lastlog[0] != 0) {
        	$f->add(
        	    new LinkTrFormElement(_("Last action"), new HiddenTpl("lastaction")),
                array("value" => urlStr("base/users/loguser", array("user" => $uid)), "name" => $lastlog[1][0]["date"])
            );
        }
    }

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
        array("value" => $uid, "action" => $mode)
    );

    $f->add(
        new TrFormElement(_("Last name"), new InputTpl("name")),
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

    $email = new InputTpl("mail",'/^([A-Za-z0-9._%-]+@[A-Za-z0-9.-]+){0,1}$/');
    $f->add(
        new TrFormElement(_("Mail address"), $email),
        array("value"=> $FH->getArrayOrPostValue("mail"))
    );

    $f->pop();

    $phoneregexp = "/^[a-zA-Z0-9(-/ ]*$/";

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
        $primary = getUserPrimaryGroup($uid);
    }
    $f->add(
        new TrFormElement(_("Primary group"), $groupsTpl),
        array("value" => $primary)
    );

    /* Secondary groups */
    /*$groupsTpl = new MembersTpl("secondary");
    $groupsTpl->setTitle(_("User groups"), _("All groups"));
    // get the user's groups
    $user_groups = getUserSecondaryGroups($uid);
    $member = array();
    foreach($user_groups as $group) {
        $member[$group] = $group;
    }
    $available = array();
    foreach($groups as $group) {
        $available[$group] = $group;
    }
    $f->add(
        new TrFormElement(_("Secondary groups"), $groupsTpl),
        array("memberOf" => $member, "available" => $available)
    );*/

    $f->pop();
    $f->push(new DivExpertMode());
    $f->push(new Table());

    $f->add(
        new TrFormElement(_("Home directory"), new InputTpl("homeDir")),
        array("value" => $FH->getArrayOrPostValue("homeDir"))
    );

    if ($mode == "add") {
        $f->add(
            new TrFormElement(_("Create home directory on filesystem"), new CheckboxTpl("createHomeDir")),
            array("value" => "checked")
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

    $f->add(
        new TrFormElement(_("UID"), new HiddenTpl("uidNumber")),
        array("value"=> $FH->getArrayOrPostValue("uidNumber"))
    );

    $f->add(
        new TrFormElement(_("GID"), new HiddenTpl("gidNumber")),
        array("value"=> $FH->getArrayOrPostValue("uidNumber"))
    );

    $f->pop();
    $f->pop();
    $f->pop();
    $f->display();
}

?>
