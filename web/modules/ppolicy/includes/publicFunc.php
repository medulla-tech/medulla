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
    $f = new DivForModule(_T("Password policy plugin", "ppolicy"), "#FDF");
    
    if ((isset($ldapArr['uid'][0])) && (hasPPolicyObjectClass($ldapArr['uid'][0]))) {
        $hasPPolicy = "checked";
    } else {
        $hasPPolicy = "";
    }
    
    $f->push(new Table());
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
    if (False) {
        $f->push(new Table());
        $f->add(new TrFormElement(_T("Minimum length", "ppolicy"),
                                  new InputTpl("pwdMinLength",'/^[0-9]*$/'),
                                  array("tooltip" => ppolicyTips("pwdMinLength"))),
                array("value"=>$ldapArr["pwdMinLength"][0]));
    
        $f->pop();
    }

    $f->push(new Table());

    $f->add(new TrFormElement(_T("Minimum age (seconds)", "ppolicy"),new InputTpl("pwdMinAge",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdMinAge"))),
                              array("value"=>$ldapArr["pwdMinAge"][0]));

    $f->add(new TrFormElement(_T("Maximum age (second)", "ppolicy"),new InputTpl("pwdMaxAge",'/^[0-9]*$/'),
			      array("tooltip" => ppolicyTips("pwdMaxAge"))),
                              array("value"=>$ldapArr["pwdMaxAge"][0]));
            
    $f->pop();

    $f->push(new Table());

    if (strcmp($ldapArr["pwdMustChange"][0], 'TRUE') == 0) {
        $pwdMustChange = "checked";
    } else {
        $pwdMustChange = "";
    }

    $f->add(new TrFormElement(_T("Force users to change their passwords on the first connection ?", "ppolicy"), new CheckboxTpl("pwdMustChange"),
                              array("tooltip" => ppolicyTips("pwdMustChange"))),
            array("value" => $pwdMustChange));
    $f->pop();


    $f->push(new Table());

    $f->add(new TrFormElement(_T("Password history", "ppolicy"),
                              new InputTpl("pwdInHistory",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdInHistory"))),
            array("value"=>$ldapArr["pwdInHistory"][0]));

    $f->pop();


    $f->push(new Table());

    if (strcmp($ldapArr["pwdLockout"][0],'TRUE') == 0) {
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
            array("value"=>$ldapArr["pwdMaxFailure"][0]));

    $f->add(new TrFormElement(_("Lockout duration (seconds)"),new InputTpl("pwdLockoutDuration",'/^[0-9]*$/'),
                              array("tooltip" => ppolicyTips("pwdLockoutDuration"))),
                              array("value"=>$ldapArr["pwdLockoutDuration"][0]));

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
    if ($FH->getPostValue("ppolicyactivated")) {
        if (!hasPPolicyObjectClass($FH->getPostValue("nlogin"))) {
            addPPolicyObjectClass($FH->getPostValue("nlogin"));
        }

        $detailArr = getDetailedUser($FH->getPostValue("nlogin"));
        _ppolicy_completeUserEntry($detailArr);
        $ppolicyattr = getPPolicyAttributesKeys();

        $msg = '<br />';

        foreach ($ppolicyattr as $key => $info) { // foreach the list of Supported Attributes
            // check if the value has been updated
            if($FH->isUpdated($key)) {
                // checkboxes
                if ($info[1] == "bool") {
                    if($FH->getValue($key) == "off") {
                        setUserPPolicyAttribut($FH->getPostValue("nlogin"),$key,'FALSE');
                        $action = _('disabled');
                    }
                    else {
                        setUserPPolicyAttribut($FH->getPostValue("nlogin"),$key,'TRUE');
                        $action = _('enabled');
                    }
                    $msg .= "- ".$info[0]." ".$action."<br />";                
                }
                // other ppolicy attributes
                else {                
                    setUserPPolicyAttribut($FH->getPostValue("nlogin"), $key, $FH->getValue($key));
                    $msg .= "- ".$info[0]." "._("updated")."<br />";
                }
            }
        }

        if ($msg != '<br />') {
            global $result;
            $result .= $msg;
        }
    } else {
        /* if ppolicy plugin is unchecked */
        if (hasPPolicyObjectClass($FH->getPostValue("nlogin"))) {
            removePPolicyObjectClass($FH->getPostValue("nlogin"));
        }
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
