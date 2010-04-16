<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
 * Add form on edit user page
 *
 */
function _ppolicy_baseEdit($ldapArr, $postArr) {

    # get current values
    $pwdMinLength = isset($ldapArr["pwdMinLength"][0]) ? $ldapArr["pwdMinLength"][0] : "";
    $pwdCheckQuality = isset($ldapArr["pwdCheckQuality"][0]) ? $ldapArr["pwdCheckQuality"][0] : "";
    $pwdMinAge = isset($ldapArr["pwdMinAge"][0]) ? $ldapArr["pwdMinAge"][0] : "";
    $pwdMaxAge = isset($ldapArr["pwdMaxAge"][0]) ? $ldapArr["pwdMaxAge"][0] : "";
    $pwdGraceAuthNLimit = isset($ldapArr["pwdGraceAuthNLimit"][0]) ? $ldapArr["pwdGraceAuthNLimit"][0] : "";
    $pwdInHistory = isset($ldapArr["pwdInHistory"][0]) ? $ldapArr["pwdInHistory"][0] : "";
    $pwdLockout = isset($ldapArr["pwdLockout"][0]) ? $ldapArr["pwdLockout"][0] : "";
    $pwdMustChange = isset($ldapArr["pwdMustChange"][0]) ? $ldapArr["pwdMustChange"][0] : "";
    $pwdMaxFailure = isset($ldapArr["pwdMaxFailure"][0]) ? $ldapArr["pwdMaxFailure"][0] : "";
    $pwdLockoutDuration = isset($ldapArr["pwdLockoutDuration"][0]) ? $ldapArr["pwdLockoutDuration"][0] : "";

    $f = new DivForModule(_T("Password policy plugin", "ppolicy"), "#FDF");

    $hasPPolicy = "";
    $pwdReset = "";

    if (isset($ldapArr['uid'][0])) {
        if (hasPPolicyObjectClass($ldapArr['uid'][0])) {
            $hasPPolicy = "checked";
        }
        if (passwordHasBeenReset($ldapArr['uid'][0])) {
            $pwdReset = "checked";
        }
    }

    $f->push(new Table());
    $f->add(
            new TrFormElement(_T("Password reset flag", "ppolicy"),
                              new CheckboxTpl("pwdReset"),
                              array("tooltip" => _T("If checked, the user must change her password when she first binds to the LDAP directory after password is set or reset by a password administrator"))),
            array("value" => $pwdReset)
            );

    $f->add(
        new TrFormElement(_T("Enable a specific password policy for this user", "ppolicy"), new CheckboxTpl("ppolicyactivated"),
			      array("tooltip" => _T("You can enable a specific password policy for this user. If disabled, the default password policy is enforced.", "ppolicy"))),
        array("value"=>$hasPPolicy, "extraArg"=>'onclick="toggleVisibility(\'ppolicydiv\');"')
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
            array("value"=>$pwdMinLength));
    $f->add(new TrFormElement(_T("Password quality check", "ppolicy"),
                              new InputTpl("pwdCheckQuality",'/^[012]$/'),
                              array("tooltip" => ppolicyTips("pwdCheckQuality"))),
            array("value"=>$pwdCheckQuality));
    $f->pop();

    $f->push(new Table());

    $f->add(new TrFormElement(_T("Minimum age (seconds)", "ppolicy"),new InputTpl("pwdMinAge",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdMinAge"))),
                              array("value"=>$pwdMinAge));

    $f->add(new TrFormElement(_T("Maximum age (second)", "ppolicy"),new InputTpl("pwdMaxAge",'/^[0-9]*$/'),
			      array("tooltip" => ppolicyTips("pwdMaxAge"))),
                              array("value"=>$pwdMaxAge));

    $f->add(new TrFormElement(_T("Number of grace authentications", "ppolicy"),new InputTpl("pwdGraceAuthNLimit",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdGraceAuthNLimit"))),
            array("value"=>$pwdGraceAuthNLimit));


    $f->pop();

    $f->push(new Table());

    if (strcmp($pwdMustChange, 'TRUE') == 0) {
        $pwdMustChange = "checked";
    } else {
        $pwdMustChange = "";
    }

    $f->add(new TrFormElement(_T("Force user to change her password on the first connection ?", "ppolicy"), new CheckboxTpl("pwdMustChange"),
                              array("tooltip" => ppolicyTips("pwdMustChange"))),
            array("value" => $pwdMustChange));
    $f->pop();


    $f->push(new Table());

    $f->add(new TrFormElement(_T("Password history", "ppolicy"),
                              new InputTpl("pwdInHistory",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdInHistory"))),
            array("value"=>$pwdInHistory));

    $f->pop();


    $f->push(new Table());

    if (strcmp($pwdLockout,'TRUE') == 0) {
        $pwdLockout = "checked";
    } else {
        $pwdLockout = "";
    }

    $f->add(new TrFormElement(_T("Preventive user lockout ?", "ppolicy"), new CheckboxTpl("pwdLockout"),
                              array("tooltip" => ppolicyTips("pwdLockout"))),
            array("value" => $pwdLockout,"extraArg"=>'onclick="toggleVisibility(\'lockoutdiv\');"'));
    $f->pop();

    $lockoutdiv = new Div(array("id" => "lockoutdiv"));
    $lockoutdiv->setVisibility($pwdLockout);
    $f->push($lockoutdiv);

    $f->push(new Table());
    $f->add(new TrFormElement(_("Password maximum failure"),new InputTpl("pwdMaxFailure",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdMaxFailure"))),
            array("value"=>$pwdMaxFailure));

    $f->add(new TrFormElement(_("Lockout duration (seconds)"),new InputTpl("pwdLockoutDuration",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdLockoutDuration"))),
                              array("value"=>$pwdLockoutDuration));

    $f->pop();
    $f->pop();
    $f->pop();

    $f->display();
}


/**
 * Check ppolicy information
 * @param $postArr $_POST array of the page
 */
function _ppolicy_verifInfo($postArr) {
    if (isset($postArr["ppolicyactivated"])) {
        /* check Valide attributes rules */
        if ( $postArr["pwdMinAge"] != null && $postArr["pwdMaxAge"] != null &&              /* if attributes exists */
             $postArr["pwdMinAge"] != 0 && $postArr["pwdMaxAge"] != 0 &&                    /* if attributes are not deactivated */
             $postArr["pwdMinAge"] > $postArr["pwdMaxAge"] ) {                              /* if they have authorized values */
            global $error;
            $error .= _T("\"Maximum age\" must be greater than \"Minimum age\".", "ppolicy") . "<br />";
            setFormError("ppolicy");
        }
    }
}

/**
 * function call when you submit change on a user
 * @param $FH FormHandler class of the page
 */
function _ppolicy_changeUser($FH) {
    $ppolicyattr = getPPolicyAttributesKeys();
    $updated = False;
    if ($FH->getPostValue("ppolicyactivated")) {
        if (!hasPPolicyObjectClass($FH->getPostValue("nlogin"))) {
            addPPolicyObjectClass($FH->getPostValue("nlogin"));
        }

        $detailArr = getDetailedUser($FH->getPostValue("nlogin"));
        _ppolicy_completeUserEntry($detailArr);
        foreach ($ppolicyattr as $key => $info) { // foreach the list of Supported Attributes
            // check if the value has been updated
            if($FH->isUpdated($key)) {
                // checkboxes
                if ($info[1] == "bool") {
                    if($FH->getValue($key) == "off") {
                        setUserPPolicyAttribut($FH->getPostValue("nlogin"),$key,'FALSE');
                        $action = _('disabled');
                    } else {
                        setUserPPolicyAttribut($FH->getPostValue("nlogin"),$key,'TRUE');
                        $action = _('enabled');
                    }
                }
                // other ppolicy attributes
                else {
                    setUserPPolicyAttribut($FH->getPostValue("nlogin"), $key, $FH->getValue($key));
                }
                $updated = True;
            }
        }
    } else {
        /* if ppolicy plugin is unchecked */
        if (hasPPolicyObjectClass($FH->getPostValue("nlogin"))) {
            removePPolicyObjectClass($FH->getPostValue("nlogin"));
        }
        /* Handle special pwdReset case, which doesn't require the PPolicy
           object class */
        if ($FH->isUpdated('pwdReset')) {
            if($FH->getValue('pwdReset') == "off") {
                setUserPPolicyAttribut($FH->getPostValue("nlogin"),
                                       'pwdReset', 'FALSE');
                $action = _('disabled');
            } else {
                setUserPPolicyAttribut($FH->getPostValue("nlogin"),
                                       'pwdReset', 'TRUE');
                $action = _('enabled');
            }
            $updated = True;
        }
    }
    if ($updated) {
        global $result;
        $result .= "<br/>". _T("Password policy attributes updated.", "ppolicy") ."<br>";
    }
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
