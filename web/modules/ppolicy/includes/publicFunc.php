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
        $pwdMustChange = "CHECKED";
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
        $pwdLockout = "CHECKED";
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
 * @param $postArr $_POST array of the page
 */
function _ppolicy_changeUser($postArr) {
    if (isset($postArr["ppolicyactivated"])) {
        if (!hasPPolicyObjectClass($postArr["nlogin"])) {
            addPPolicyObjectClass($postArr["nlogin"]);
        }

        $detailArr = getDetailedUser($postArr["nlogin"]);
        _ppolicy_completeUserEntry($detailArr);
        $ppolicyattr = getPPolicyAttributesKeys();

        $msg = '<br />';

        foreach ($ppolicyattr as $key=>$info) {     // foreach the list of Supported Attributes
            if ($info[1]=="bool") { 
                if (empty($postArr[$key])) {
                    if ($detailArr[$key][0] != "FALSE") {
                        setUserPPolicyAttribut($postArr["nlogin"],$key,'FALSE');
                        $msg .= "- ".$info[0]."<br />";
                    }                   
                } else {
                    if ($detailArr[$key][0] != "TRUE") {
                        setUserPPolicyAttribut($postArr["nlogin"],$key,'TRUE');
                        $msg .= "- ".$info[0]."<br />";
                    }                    
                }
            } elseif ($detailArr[$key][0] != $postArr[$key]) {
                setUserPPolicyAttribut($postArr["nlogin"],$key,$postArr[$key]);
                $msg .= "- ".$info[0]."<br />";
            }
        }

        if ($msg != '<br />') {
            global $result;
            $result .= $msg;
            $result .= _("has been updated")."<br />";
        }
    } else {
        /* if ppolicy plugin is unchecked */
        if (hasPPolicyObjectClass($postArr["nlogin"])) {
            removePPolicyObjectClass($postArr["nlogin"]);
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
