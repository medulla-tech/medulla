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

require("modules/base/users/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/ppolicy/includes/ppolicy.inc.php");
require_once("includes/FormHandler.php");

global $errorStatus;
$error = "";
$result = "";

// Class managing $_POST array
if($_POST) {
    $FH = new FormHandler("editPPolicyFH", $_POST);
}
else {
    $FH = new FormHandler("editPPolicyFH", array());
}

if ($_GET["action"] == "addppolicy") {
    $mode = "add";
    $title = _T("Add a password policy", "ppolicy");
}
else {
    $mode = "edit";
    $title = _T("Edit password policy", "ppolicy");;
    $sidemenu->forceActiveItem("indexppolicy");
    $ppolicy = $_GET['ppolicy'];
    $FH->setArr(getAllPPolicyAttributes($ppolicy));
}

if ($_POST) {
    $name = $FH->getPostValue("cn");
    $desc = $FH->getPostValue("description");
    // Some sanity checks...
    if ($FH->isUpdated("pwdMaxAge") or $FH->isUpdated("pwdMinAge")) {
        $max = $FH->getPostValue("pwdMaxAge");
        $min = $FH->getPostValue("pwdMinAge");
        if ($min && $max && $min > $max) {
            $error .= _T('"Maximum age" must be greater than "Minimum age".', 'ppolicy') . "<br />";
            setFormError("pwdMinAge");
        }
    }
    if ($mode == "add") {
        if (!checkPPolicy($name)) {
            addPPolicy($name, $desc);
            if (!isXMLRPCError())
                $result .= _T(sprintf("Password policy %s created.", $name), "ppolicy") . "<br />";
            else
                $error .= _T(sprintf("Failed to create %s password policy.", $name), "ppolicy") . "<br />";
        }
        else {
            $error .= _T(sprintf("Password policy %s already exists.", $name), "ppolicy") . "<br />";
        }
    }

    if (!$error && !isXMLRPCError()) {
        $ppolicyattr = getPPolicyAttributesKeys();
        $update = "";
        foreach ($ppolicyattr as $attr => $info) { /* foreach supported attributes */
            if ($FH->isUpdated($attr) && $info[1] == "bool") {
                if ($FH->getValue($attr) == "on") $value = "TRUE";
                if ($FH->getValue($attr) == "off") $value = "FALSE";
                setPPolicyAttribute($attr, $value, $name);
                $update .= "<li>" . $info[0] . "</li>";
            }
            else if ($FH->isUpdated($attr)) {
                setPPolicyAttribute($attr, $FH->getValue($attr), $name);
                $update .= "<li>" . $info[0] . "</li>";
            }
        }
        if ($update)
            $result .= _T("Attributes updated", "ppolicy") . ": <ul>" . $update . "</ul>";
    }

    if ($error)
        new NotifyWidgetFailure($error);
    if (isXMLRPCError())
        $FH->isError(true);
    else {
        $FH->isError(false);
        if ($result)
            new NotifyWidgetSuccess($result);
        header("Location: ". urlStrRedirect("base/users/editppolicy", array("ppolicy" => $name)));
    }
}

$p = new PageGenerator($title);
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm();

$f->push(new Table());

if ($mode == "add")
    $nameTpl = new InputTpl("cn", '/^[0-9a-zA-Z_ -]*$/');
else
    $nameTpl = new HiddenTpl("cn");
$f->add(new TrFormElement(
        _T("Name", "ppolicy"),
        $nameTpl
    ),
    array("value" => $FH->getArrayOrPostValue("cn"), "required" => true)
);
$f->add(new TrFormElement(
        _T("Description", "ppolicy"),
        new InputTpl("description")
    ),
    array("value" => $FH->getArrayOrPostValue("description"))
);
$f->add(new TrFormElement(
        _T("Minimum length", "ppolicy"),
        new InputTpl("pwdMinLength",'/^[0-9]*$/'),
        array("tooltip" => ppolicyTips("pwdMinLength"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdMinLength"))
);
$f->add(new TrFormElement(
        _T("Password quality check", "ppolicy"),
        new InputTpl("pwdCheckQuality",'/^[012]$/'),
        array("tooltip" => ppolicyTips("pwdCheckQuality"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdCheckQuality"))
);
$f->add(new TrFormElement(
        _T("Minimum age (seconds)", "ppolicy"),
        new InputTpl("pwdMinAge",'/^[0-9]*$/'),
        array("tooltip" => ppolicyTips("pwdMinAge"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdMinAge"))
);
$f->add(new TrFormElement(
        _T("Maximum age (seconds)", "ppolicy"),
        new InputTpl("pwdMaxAge",'/^[0-9]*$/'),
        array("tooltip" => ppolicyTips("pwdMaxAge"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdMaxAge"))
);
$f->add(new TrFormElement(
        _T("Number of grace authentications", "ppolicy"),
        new InputTpl("pwdGraceAuthNLimit",'/^[0-9]*$/'),
        array("tooltip" => ppolicyTips("pwdGraceAuthNLimit"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdGraceAuthNLimit"))
);

if ($FH->getArrayOrPostValue("pwdMustChange") == 'TRUE' ||
    $FH->getArrayOrPostValue("pwdMustChange") == 'on') {
    $pwdMustChange = "checked";
} else {
    $pwdMustChange = "";
}
$f->add(new TrFormElement(
        _T("Force users to change their passwords on the first connection ?", "ppolicy"),
        new CheckboxTpl("pwdMustChange"),
        array("tooltip" => ppolicyTips("pwdMustChange"))
    ),
    array("value" => $pwdMustChange)
);
$f->add(new TrFormElement(
        _T("Password history", "ppolicy"),
        new InputTpl("pwdInHistory",'/^[0-9]*$/'),
        array("tooltip" => ppolicyTips("pwdInHistory"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdInHistory"))
);

if ($FH->getArrayOrPostValue("pwdLockout") == 'TRUE' ||
    $FH->getArrayOrPostValue("pwdLockout") == 'on') {
    $pwdLockout = "checked";
} else {
    $pwdLockout = "";
}
$f->add(new TrFormElement(
        _T("Preventive user lockout ?", "ppolicy"),
        new CheckboxTpl("pwdLockout"),
        array("tooltip" => ppolicyTips("pwdLockout"))
    ),
    array("value" => $pwdLockout, "extraArg" => 'onclick="toggleVisibility(\'lockoutdiv\');"')
);
$f->pop();

$lockoutdiv = new Div(array("id" => "lockoutdiv"));
$lockoutdiv->setVisibility($pwdLockout);
$f->push($lockoutdiv);

$f->push(new Table());
$f->add(new TrFormElement(
        _T("Password maximum failure", "ppolicy"),
        new InputTpl("pwdMaxFailure",'/^[0-9]*$/'),
        array("tooltip" => ppolicyTips("pwdMaxFailure"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdMaxFailure"))
);
$f->add(new TrFormElement(
        _T("Lockout duration (seconds)", "ppolicy"),
        new InputTpl("pwdLockoutDuration",'/^[0-9]*$/'),
        array("tooltip" => ppolicyTips("pwdLockoutDuration"))
    ),
    array("value" => $FH->getArrayOrPostValue("pwdLockoutDuration"))
);

$f->pop();
$f->pop();

$f->addValidateButton("bppolicy");

$f->pop();

$f->display();
?>
