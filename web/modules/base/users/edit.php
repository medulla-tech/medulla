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

require("modules/base/includes/users.inc.php");
require("modules/base/includes/groups.inc.php");
require_once("modules/base/includes/logging-xmlrpc.inc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");
require("modules/base/includes/AjaxFilterLog.inc.php");
require_once("includes/FormHandler.php");

# infos messages
global $result;
# error messages
global $error;
# xmlrpc status
global $errorStatus;

// Class managing $_POST array
if($_POST) {
    $FH = new FormHandler("editUserFH", $_POST);
}
else {
    $FH = new FormHandler("editUserFH", array());
}

switch($_GET["action"]) {
    case "add":
        $mode = "add";
        $title = _("Add user");
        $activeItem = "add";
        break;
    case "edit":
        $mode = "edit";
        $title = _("Edit user");
        $activeItem = "index";
        $uid = $_GET["user"];
        $FH->setArr(getDetailedUser($uid));
        break;
    default:
        $mode = false;
        break;
}

$redirect = false;
// if data is sent
if ($_POST) {
    $uid = $FH->getPostValue('uid');
    /* Check sent data */
    $ret = callPluginFunction("verifInfo", array($FH, $mode));
    if (!$error && !isXMLRPCError()) {
        /* Add or edit user attributes */
        $ret = callPluginFunction("changeUser", array($FH, $mode));
        /* Primary group management */
        if($FH->isUpdated("primary")) {
            $primaryGroup = getUserPrimaryGroup($uid);
            if ($FH->getValue("primary") != $primaryGroup) {
                /* Update the primary group */
                $ret = callPluginFunction("changeUserPrimaryGroup",
                    array($uid, $FH->getValue("primary"), $primaryGroup)
                );
                foreach($ret as $plugin => $err) {
                    if ($err != 0 && $err != NULL) {
                        $result .= sprintf(_("Failed to change primary group in %s plugin"), $plugin)."<br />";
                    }
                }
            }
        }
        /* Secondary groups management */
        if($FH->isUpdated("secondary")) {
            $old = getUserSecondaryGroups($uid);
            $new = $FH->getValue('secondary');
            foreach (array_diff($old, $new) as $group) {
                del_member($group, $uid);
                callPluginFunction("delUserFromGroup", array($uid, $group));
            }
            foreach (array_diff($new, $old) as $group) {
                add_member($group, $uid);
                callPluginFunction("addUserToGroup", array($uid, $group));
            }
        }
        /* Password change management */
        if ($mode == 'edit' && $FH->getValue('pass')) {
            $ret = callPluginFunction("changeUserPasswd",
                array(array($uid, prepare_string($FH->getValue('pass'))))
            );
            if(isXMLRPCError()) {
                $error .= _("Password not updated") . "<br />";
            }
            else {
                $result .= _("Password updated") . "<br />";
            }
        }
        /* Global disable account */
        if ($mode == 'edit') {
            if ($FH->getPostValue('disableAccount')) {
                $ret = callPluginFunction("disableUser", array($uid));
                foreach($ret as $plugin => $err) {
                    if ($err != 0 && $err != NULL) {
                        $result .= sprintf(_("Failed to disable user in %s plugin"), $plugin)."<br />";
                    }
                }
                $result = sprintf(_("User %s disabled."), $uid);
            }
            if ($FH->getPostValue('enableAccount')) {
                $ret = callPluginFunction("enableUser", array($uid));
                foreach($ret as $plugin => $err) {
                    if ($err != 0 && $err != NULL) {
                        $result .= sprintf(_("Failed to enable user in %s plugin"), $plugin)."<br />";
                    }
                }
                $result = sprintf(_("User %s enabled"), $uid);
            }
        }
        if(!$error) {
            $redirect = true;
            $FH->isError(false);
        }
    }
    else {
        $FH->isError(true);
    }
}

// prepare the result popup
$resultPopup = new NotifyWidget();
// add error messages
if ($error) {
    $resultPopup->add('<div class="errorCode">' . $error . '</div>');
    $resultPopup->setLevel(5);
}
// add info messages
if ($result) {
    $resultPopup->add('<div class="validCode">' . $result . '</div>');
}
// in case of modification/creation success, redirect to the edit page
if ($redirect)
    header('Location: ' . urlStrRedirect("base/users/edit",
        array("user" => $uid)));

// in case of failure, set errorStatus to 0 in order to display the edit form
$errorStatus = 0;

// edit form page starts here
$p = new PageGenerator($title);
$sidemenu->forceActiveItem($activeItem);
$p->setSideMenu($sidemenu);
$p->display();
// create the form
$f = new ValidatingForm(array('method' => 'POST',
    'enctype' => 'multipart/form-data'));
// add submit button
$f->addValidateButton("buser");

// check if all modules are disabled
// TODO
$disabledAccount = false;
if($mode == 'edit') {
    if ($disabledAccount)
        $f->addButton("enableAccount", _("Enable account"), "btnSecondary");
    else
        $f->addButton("disableAccount", _("Disable account"), "btnSecondary");
}
// add reset form button
$f->addCancelButton("breset");
// add all modules forms to the edit form
$modules = callPluginFunction("baseEdit", array($FH, $mode));
foreach($modules as $module => $editForm) {
    $f->push($editForm);
    $f->pop();
}
// display the form
$f->display();

?>
