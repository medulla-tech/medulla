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

/* public functions of the ppolicy module, included by the user edit page */

require_once("ppolicy-xmlrpc.php");
require_once("ppolicy.inc.php");

/**
 * Form on user edit page
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _ppolicy_baseEdit($FH, $mode) {

    $f = new DivForModule(_T("Password policy management", "ppolicy"), "#FDF");

    // default values
    $hasPPolicy = false;
    $pwdReset = false;
    $ppolicyName = "";
    $default = getDefaultPPolicyName();

    if ($mode == "edit") {
        $uid =  $FH->getArrayOrPostValue('uid');
        if (hasUserPPolicy($uid)) {
            $hasPPolicy = true;
            $ppolicyName = getUserPPolicy($uid);
        }
        if (passwordHasBeenReset($uid)) {
            $pwdReset = true;
        }
    }

    $f->push(new Table());

    if ($mode == "edit") {
        $pwdLock = false;
        if(isAccountLocked($uid) != "0") {
            $pwdLock = true;
            // Display an error message on top of the page
            $em = new ErrorMessage(_T("Password policy management", "ppolicy") . ' : ' .
                _T("This account is locked by the LDAP directory.", "ppolicy"));
            $em->display();
        }
        $pwdExpired = isPasswordExpired($uid);
        $nbGraceLogins = isAccountInGraceLogin($uid);
        if ($pwdExpired && in_array($nbGraceLogins, array(0, 1))) {
            // Display an error message on top of the page
            $em = new ErrorMessage(_T("Password policy management", "ppolicy") . ' : ' .
                _T("The password of this account has expired. The user cannot change his password.", "ppolicy"));
            $em->display();
        }
        if ($pwdExpired && ($nbGraceLogins == -1 || $nbGraceLogins > 1)) {
            if ($nbGraceLogins > 1) {
                // Display an error message on top of the page
                $em = new ErrorMessage(_T("Password policy management", "ppolicy") . ' : ' .
                    sprintf(_T("The password of this account has expired. The user has %s login(s) left to change his password.", "ppolicy"), $nbGraceLogins));
            }
            else {
                // Display an error message on top of the page
                $em = new ErrorMessage(_T("Password policy management", "ppolicy") . ' : ' .
                    _T("The password of this account has expired. The user can change his password.", "ppolicy"));
            }
            $em->display();
        }
        $f->add(new TrFormElement(_T("Lock account", "ppolicy"),
            new CheckboxTpl("pwdLock"), array("tooltip" => _T("If checked, permanently lock the user account", "ppolicy"))),
            array("value" => $pwdLock ? "checked" : "")
        );
    }

    $f->add(new TrFormElement(_T("Password reset flag", "ppolicy"),
        new CheckboxTpl("pwdReset"), array("tooltip" => _T("If checked, the user must change her password when she first binds to the LDAP directory after password is set or reset by a password administrator", "ppolicy"))),
        array("value" => $pwdReset ? "checked" : "")
    );

    $ppolicyList = listPPolicy();
    if (count($ppolicyList) > 1) {
        $ppolicyTpl = new SelectItem("ppolicyname");
        foreach($ppolicyList as $pp) {
            $name = $pp[1]['cn'][0];
            if (isset($pp[1]['description'][0]))
                $desc = $pp[1]['description'][0];
            else
                $desc = $name;
            if ($name == $default) {
                $name = "";
                $desc = _T($desc, "ppolicy");
            }

            $values[$desc] = $name;
        }
        $ppolicyTpl->setElements(array_keys($values));
        $ppolicyTpl->setElementsVal(array_values($values));
        $f->add(new TrFormElement(_T("Enable a specific password policy for this user", "ppolicy"),
            $ppolicyTpl, array("tooltip" => _T("If not set the default password policy is enforced.", "ppolicy"))),
            array("value" => $ppolicyName)
        );
    }

    $f->pop();

    return $f;
}


/**
 * Function called before changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _ppolicy_verifInfo($FH, $mode) {
    return 0;
}

/**
 * Function called for changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _ppolicy_changeUser($FH, $mode) {

    global $result;

    $uid = $FH->getPostValue("uid");
    $updated = False;

    if ($mode == "edit") {
        if ($FH->isUpdated("pwdLock")) {
            if ($FH->getValue("pwdLock") == "on")
                lockAccount($uid);
            else
                unlockAccount($uid);
        }
    }

    if ($FH->isUpdated("ppolicyname")) {
        $ppolicyName = $FH->getValue("ppolicyname");
        if ($ppolicyName) {
            updateUserPPolicy($uid, $ppolicyName);
            $result .= sprintf(_T("Password policy %s applied.", "ppolicy"), $ppolicyName) . "<br />";
        }
        else {
            removeUserPPolicy($uid);
            $result .= sprintf(_T("Password policy %s removed.", "ppolicy"), $ppolicyName) . "<br />";
        }
    }

    /* Handle special pwdReset case, which doesn't require the PPolicy
       object class */
    if ($FH->isUpdated('pwdReset')) {
        if($FH->getValue('pwdReset') == "off") {
            setUserPPolicyAttribut($uid, 'pwdReset', 'FALSE');
        } else {
            setUserPPolicyAttribut($uid, 'pwdReset', 'TRUE');
        }
        $result .= _T("Password policy attributes updated.", "ppolicy") . "<br />";
    }

    return 0;
}

/**
 * Function called when editing a group
 */
function _ppolicy_baseGroupEdit($ldapArr, $postArr) {

    if (!isset($ldapArr["cn"][0])) return;

    $default = getDefaultPPolicyName();

    $f = new DivForModule(_T("Password policy management", "ppolicy"), "#FDF");

    $f->push(new Table());

    $ppolicyList = listPPolicy();
    if (count($ppolicyList) > 1) {
        $ppolicyTpl = new SelectItem("ppolicyname");
        foreach($ppolicyList as $pp) {
            $name = $pp[1]['cn'][0];
            if (isset($pp[1]['description'][0]))
                $desc = $pp[1]['description'][0];
            else
                $desc = $name;
            if ($name == $default) {
                $name = "";
                $desc = _T($desc, "ppolicy");
            }

            $values[$desc] = $name;
        }
        $ppolicyTpl->setElements(array_keys($values));
        $ppolicyTpl->setElementsVal(array_values($values));
        $f->add(new TrFormElement(_T("Apply a password policy for all group users", "ppolicy"),
            $ppolicyTpl, array("tooltip" => _T("If not set the default password policy is enforced.", "ppolicy"))),
            array("value" => $ppolicyName)
        );
    }

    $f->pop();
    $f->display();
}

function _ppolicy_changeGroup($postArr) {
    $group = $postArr["groupname"];
    if (isset($postArr["ppolicyname"]) && trim($postArr["ppolicyname"])) {
        updateGroupPPolicy($group, $postArr["ppolicyname"]);
    }
}

?>
