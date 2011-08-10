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
    
    if ($mode == "edit") {
        $uid =  $FH->getArrayOrPostValue('uid');
        if (hasPPolicyObjectClass($uid)) {
            $hasPPolicy = true;
        }
        if (passwordHasBeenReset($uid)) {
            $pwdReset = true;
        }        
    }

    $f->push(new Table());
    $f->add(new TrFormElement(_T("Password reset flag", "ppolicy"),
        new CheckboxTpl("pwdReset"), array("tooltip" => _T("If checked, the user must change her password when she first binds to the LDAP directory after password is set or reset by a password administrator", "ppolicy"))),
        array("value" => $pwdReset ? "checked" : "")
    );

    $f->add(new TrFormElement(_T("Enable a specific password policy for this user", "ppolicy"), 
        new CheckboxTpl("ppolicyactivated"), array("tooltip" => _T("You can enable a specific password policy for this user. If disabled, the default password policy is enforced.", "ppolicy"))),
        array("value" => $hasPPolicy ? "checked" : "", 
            "extraArg"=>'onclick="toggleVisibility(\'ppolicydiv\');"')
    );
    $f->pop();

    $ppolicydiv = new Div(array("id" => "ppolicydiv"));
    $ppolicydiv->setVisibility($hasPPolicy);
    $f->push($ppolicydiv);

    /* Password Policies Attributes List Section */
    $f->push(new Table());
    
    $f->add(new TrFormElement(_T("Minimum length", "ppolicy"),
        new InputTpl("pwdMinLength",'/^[0-9]*$/'),
            array("tooltip" => ppolicyTips("pwdMinLength"))),
        array("value" => $FH->getArrayOrPostValue("pwdMinLength"))
    );
    $f->add(new TrFormElement(_T("Password quality check", "ppolicy"),
        new InputTpl("pwdCheckQuality",'/^[012]$/'),
            array("tooltip" => ppolicyTips("pwdCheckQuality"))),
        array("value" => $FH->getArrayOrPostValue("pwdCheckQuality"))
    );
    $f->add(new TrFormElement(_T("Minimum age (seconds)", "ppolicy"),
        new InputTpl("pwdMinAge",'/^[0-9]*$/'),
            array("tooltip" => ppolicyTips("pwdMinAge"))),
        array("value" => $FH->getArrayOrPostValue("pwdMinAge"))
    );
    $f->add(new TrFormElement(_T("Maximum age (second)", "ppolicy"),
        new InputTpl("pwdMaxAge",'/^[0-9]*$/'),
            array("tooltip" => ppolicyTips("pwdMaxAge"))),
        array("value" => $FH->getArrayOrPostValue("pwdMaxAge"))
    );
    $f->add(new TrFormElement(_T("Number of grace authentications", "ppolicy"),
        new InputTpl("pwdGraceAuthNLimit",'/^[0-9]*$/'),
            array("tooltip" => ppolicyTips("pwdGraceAuthNLimit"))),
        array("value" => $FH->getArrayOrPostValue("pwdGraceAuthNLimit"))
    );

    $pwdMustChange = false;
    if ($FH->getArrayOrPostValue("pwdMustChange") == 'TRUE' ||
        $FH->getArrayOrPostValue("pwdMustChange") == 'on')
        $pwdMustChange = true;
    $f->add(new TrFormElement(_T("Force user to change her password on the first connection ?", "ppolicy"), 
        new CheckboxTpl("pwdMustChange"),
            array("tooltip" => ppolicyTips("pwdMustChange"))),
        array("value" => $pwdMustChange ? "checked" : "")
    );
            
    $f->add(new TrFormElement(_T("Password history", "ppolicy"),
        new InputTpl("pwdInHistory",'/^[0-9]*$/'),
            array("tooltip" => ppolicyTips("pwdInHistory"))),
        array("value" => $FH->getArrayOrPostValue("pwdInHistory"))
    );

    $pwdLockout = false;
    if ($FH->getArrayOrPostValue("pwdLockout") == 'TRUE' ||
        $FH->getArrayOrPostValue("pwdLockout") == 'on')
        $pwdLockout = true;
    $f->add(new TrFormElement(_T("Preventive user lockout ?", "ppolicy"),
        new CheckboxTpl("pwdLockout"),
            array("tooltip" => ppolicyTips("pwdLockout"))),
        array("value" => $pwdLockout ? "checked" : "",
            "extraArg"=>'onclick="toggleVisibility(\'lockoutdiv\');"'));
    $f->pop();

    $lockoutdiv = new Div(array("id" => "lockoutdiv"));
    $lockoutdiv->setVisibility($pwdLockout);
    $f->push($lockoutdiv);

    $f->push(new Table());
    
    $f->add(new TrFormElement(_("Password maximum failure"),
        new InputTpl("pwdMaxFailure",'/^[0-9]*$/'),
            array("tooltip" => ppolicyTips("pwdMaxFailure"))),
        array("value" => $FH->getArrayOrPostValue("pwdMaxFailure"))
    );

    $f->add(new TrFormElement(_("Lockout duration (seconds)"),
        new InputTpl("pwdLockoutDuration",'/^[0-9]*$/'),
            array("tooltip" => ppolicyTips("pwdLockoutDuration"))),
        array("value" => $FH->getArrayOrPostValue("pwdLockoutDuration"))
    );

    $f->pop();
    $f->pop();
    $f->pop();

    return $f;
}


/**
 * Function called before changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _ppolicy_verifInfo($FH, $mode) {

    global $error;
    
    $ppolicy_errors = "";

    if ($FH->getPostValue("ppolicyactivated")) {
        if ($FH->isUpdated("pwdMaxAge") or $FH->isUpdated("pwdMinAge")) {
            $max = $FH->getPostValue("pwdMaxAge");
            $min = $FH->getPostValue("pwdMinAge");
            if ($min && $max && $min > $max) {
                $ppolicy_errors = _T('"Maximum age" must be greater than "Minimum age".', 'ppolicy') . "<br />";
                setFormError("pwdMinAge");
            }
        }
    }
    
    $error .= $ppolicy_errors;

    return $ppolicy_errors ? 1 : 0;
}

/**
 * Function called for changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _ppolicy_changeUser($FH, $mode) {

    $uid = $FH->getPostValue("uid");
    $ppolicyattr = getPPolicyAttributesKeys();
    $updated = False;
    
    if ($FH->getPostValue("ppolicyactivated")) {
        if (!hasPPolicyObjectClass($uid)) {
            addPPolicyObjectClass($uid);
            $updated = True;
        }

        $detailArr = getDetailedUser($uid);
        _ppolicy_completeUserEntry($detailArr);
        foreach ($ppolicyattr as $key => $info) { // foreach the list of Supported Attributes
            // check if the value has been updated
            if($FH->isUpdated($key)) {
                // checkboxes
                if ($info[1] == "bool") {
                    if($FH->getValue($key) == "off") {
                        setUserPPolicyAttribut($uid,$key,'FALSE');
                        $action = _('disabled');
                    } else {
                        setUserPPolicyAttribut($uid,$key,'TRUE');
                        $action = _('enabled');
                    }
                }
                // other ppolicy attributes
                else {
                    setUserPPolicyAttribut($uid, $key, $FH->getValue($key));
                }
                $updated = True;
            }
        }
    } else {
        /* if ppolicy plugin is unchecked */
        if (hasPPolicyObjectClass($uid)) {
            removePPolicyObjectClass($uid);
        }
        /* Handle special pwdReset case, which doesn't require the PPolicy
           object class */
        if ($FH->isUpdated('pwdReset')) {
            if($FH->getValue('pwdReset') == "off") {
                setUserPPolicyAttribut($uid,
                                       'pwdReset', 'FALSE');
                $action = _('disabled');
            } else {
                setUserPPolicyAttribut($uid,
                                       'pwdReset', 'TRUE');
                $action = _('enabled');
            }
            $updated = True;
        }
    }
    
    if ($updated) {
        global $result;
        $result .= _T("Password policy attributes updated.", "ppolicy") . "<br />";
    }
    
    return 0;
}

function _ppolicy_completeUserEntry(&$entry) {
    $attrs = getPPolicyAttributesKeys();
    foreach($attrs as $attr => $value) {
        if (!isset($entry[$attr])) {
            $entry[$attr] = array("");
        }
    }

}

?>
