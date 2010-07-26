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

/* Page that allows to define the default password policies for all users */

require("modules/base/users/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/ppolicy/includes/ppolicy.inc.php");

$detailArr = getAllPPolicyAttributes();
$ppolicyattr = getPPolicyAttributesKeys();


if (isset($_POST["bppolicy"])) {
    /* Check form content */
    $error = "";
    if ( $_POST["gpwdMinAge"] != 0 && $_POST["gpwdMaxAge"] != 0 &&
         $_POST["gpwdMinAge"] != null && $_POST["gpwdMaxAge"] != null &&
         $_POST["gpwdMinAge"] > $_POST["gpwdMaxAge"] ) {
        $error .= _T("Maximum age must be more than minimum age.", "ppolicy")."<br />";
    }

    /* Notify errors */
    if ($error) {
        new NotifyWidgetFailure($error);
    } else {
        $result = '';

        /* Set values */
        foreach ($ppolicyattr as $key=>$info) { /* foreach supported attributes */
            if ($info[1]=="bool") { 
                if ($detailArr[$key][0] == 'TRUE') {
                    if (!isset($_POST['g'.$key])) {
                        setPPolicyAttribute($key,'FALSE');
                        $result .= "- ".$info[0]."<br />";
                    }
                } elseif ( $_POST['g'.$key] == "on" ) {
                    setPPolicyAttribute($key,'TRUE');
                    $result .= "- ".$info[0]."<br />";
                }
            } elseif ($detailArr[$key][0] != $_POST['g'.$key]) {
                setPPolicyAttribute($key,$_POST['g'.$key]);
                $result .= "- ".$info[0]."<br />";
            }
        }

        if ($result) {
            $result .= _T("has been updated", "ppolicy")."<br />";
            new NotifyWidgetSuccess($result);
        }
    }
}

$detailArr = getAllPPolicyAttributes();

$p = new PageGenerator(_T("Default password policy", "ppolicy"));
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm();

$f->push(new Div(array("class" => "formblock", "style" => "background-color: #F4F4F4;")));
$f->push(new Table());

$f->add(new TrFormElement(_T("Minimum length", "ppolicy"),new InputTpl("gpwdMinLength",'/^[0-9]*$/'),
                          array("tooltip" => ppolicyTips("pwdMinLength"))),
        array("value"=>$detailArr["pwdMinLength"][0]));

$f->add(new TrFormElement(_T("Password quality check", "ppolicy"),new InputTpl("gpwdCheckQuality",'/^[012]$/'),
                          array("tooltip" => ppolicyTips("pwdCheckQuality"))),
        array("value"=>$detailArr["pwdCheckQuality"][0]));



$f->pop();
$f->push(new Table());

$f->add(new TrFormElement(_T("Minimum age (seconds)", "ppolicy"),new InputTpl("gpwdMinAge",'/^[0-9]*$/'),
                          array("tooltip" => ppolicyTips("pwdMinAge"))),
        array("value"=>$detailArr["pwdMinAge"][0]));

$f->add(new TrFormElement(_T("Maximum age (seconds)", "ppolicy"),new InputTpl("gpwdMaxAge",'/^[0-9]*$/'),
                          array("tooltip" => ppolicyTips("pwdMaxAge"))),
        array("value"=>$detailArr["pwdMaxAge"][0]));

$f->add(new TrFormElement(_T("Number of grace authentications", "ppolicy"),new InputTpl("gpwdGraceAuthNLimit",'/^[0-9]*$/'),
                          array("tooltip" => ppolicyTips("pwdGraceAuthNLimit"))),
        array("value"=>$detailArr["pwdGraceAuthNLimit"][0]));

$f->pop();
$f->push(new Table());

if (strcmp($detailArr["pwdMustChange"][0], 'TRUE') == 0) {
    $pwdMustChange = "CHECKED";
} else {
    $pwdMustChange = "";
}

$f->add(new TrFormElement(_T("Force users to change their passwords on the first connection ?", "ppolicy"), new CheckboxTpl("gpwdMustChange"),
                          array("tooltip" => ppolicyTips("pwdMustChange"))),
        array("value" => $pwdMustChange));

$f->pop();
$f->push(new Table());

$f->add(new TrFormElement(_T("Password history", "ppolicy"), new InputTpl("gpwdInHistory",'/^[0-9]*$/'),
                          array("tooltip" => ppolicyTips("pwdInHistory"))),
        array("value"=>$detailArr["pwdInHistory"][0]));

$f->pop();
$f->push(new Table());

if (strcmp($detailArr["pwdLockout"][0],'TRUE') == 0) {
    $pwdLockout = "CHECKED";
} else {
    $pwdLockout = "";
}

$f->add(new TrFormElement(_T("Preventive user lockout ?", "ppolicy"), new CheckboxTpl("gpwdLockout"),
    array("tooltip" => ppolicyTips("pwdLockout"))),
    array("value" => $pwdLockout,"extraArg"=>'onclick="toggleVisibility(\'lockoutdiv\');"'));
$f->pop();

$lockoutdiv = new Div(array("id" => "lockoutdiv"));
$lockoutdiv->setVisibility($pwdLockout);
$f->push($lockoutdiv);

$f->push(new Table());
$f->add(new TrFormElement(_T("Password maximum failure", "ppolicy"),new InputTpl("gpwdMaxFailure",'/^[0-9]*$/'),
                          array("tooltip" => ppolicyTips("pwdMaxFailure"))),
        array("value"=>$detailArr["pwdMaxFailure"][0]));

$f->add(new TrFormElement(_T("Lockout duration (seconds)", "ppolicy"),new InputTpl("gpwdLockoutDuration",'/^[0-9]*$/'),
                          array("tooltip" => ppolicyTips("pwdLockoutDuration"))),
        array("value"=>$detailArr["pwdLockoutDuration"][0]));

$f->pop();
$f->pop();
$f->pop();

$f->addValidateButton("bppolicy");
$f->addCancelButton("breset");

$f->pop();

$f->display();
?>
