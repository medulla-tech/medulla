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
require("includes/FormHandler.php");

# infos messages
global $result;
# error messages
global $error;

// Class managing $_POST array
if($_POST) {
    $FH = new FormHandler($_POST);
}
else {
    $FH = new FormHandler(array());
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
    $uid = $_POST['uid'];
    /* Check sent data */
    $ret = callPluginFunction("verifInfo", array($FH, $mode));
    if (!$error) {
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
                        $result .= sprintf(_("Failed to change primary group in %s plugin."), $plugin)."<br />";
                    }
                }
            }
        }
        /* Secondary groups management */
        if($FH->isUpdated("memberOf_secondary")) {
            $old = getUserSecondaryGroups($uid);
            $new = $FH->getValue('memberOf_secondary');
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
                foreach($ret as $info) {
                    // if the faultCode is in the form :
                    // {'info': 'Password fails quality checking policy',
                    // 'desc': 'Constraint violation'}
                    // keep only the 'info' part
                    if(preg_match("/{'info': '([^']*)/", $info, $match)) {
                        $info = $match[1];
                    }
                    $result .= "<strong>"._("Password not updated")."</strong><br />";
                    $result .= "<strong>"._($info)."</strong><br/>";
                }
            }
            else {
                $result .= _("Password updated.")."<br />";
            }
        }
        /* Global disable account */
        if ($mode == 'edit') {
            if ($FH->getPostValue('disableAccount')) {
                $ret = callPluginFunction("disableUser", array($uid));
                foreach($ret as $plugin => $err) {
                    if ($err != 0 && $err != NULL) {
                        $result .= sprintf(_("Failed to disable user in %s plugin."), $plugin)."<br />";
                    }
                }
                $result = sprintf(_("User %s disabled."), $uid);
            }
            if ($FH->getPostValue('enableAccount')) {
                $ret = callPluginFunction("enableUser", array($uid));
                foreach($ret as $plugin => $err) {
                    if ($err != 0 && $err != NULL) {
                        $result .= sprintf(_("Failed to enable user in %s plugin."), $plugin)."<br />";
                    }
                }
                $result = sprintf(_("User %s enabled."), $uid);
            }
            if ($FH->getPostValue('unlockAccount')) {
                if (in_array("ppolicy", $_SESSION["supportModList"])) {
                    require_once("modules/ppolicy/includes/ppolicy-xmlrpc.php");
                    unlockAccount($uid);
                }
            }
        }
        
        /*if(!$error)
            $redirect = true;
        else*/
            $redirect = false;
    }
}

// prepare the result popup
$resultPopup = new NotifyWidget();
// add error messages
if ($error) {
    $resultPopup->add('<div id="errorCode">' . $error . '</div>');
    $resultPopup->setLevel(5);
}
// add info messages
if ($result) {
    $resultPopup->add('<div id="validCode">' . $result . '</div>');
}
// in case of modification/creation success, redirect to the index
if ($redirect)
    header('Location: ' . urlStrRedirect("base/users/index"));

$p = new PageGenerator($title);
$sidemenu->forceActiveItem($activeItem);
$p->setSideMenu($sidemenu);
$p->display();

?>
<form id="edit" enctype="multipart/form-data" method="post" onsubmit="selectAll(); return validateForm();">

    <?php
    // check if account is locked by ppolicy
    $lockedAccount = false;
    if (in_array("ppolicy", $_SESSION["supportModList"])) {
        require_once("modules/ppolicy/includes/ppolicy-xmlrpc.php");
        if ($uid && isAccountLocked($uid) != 0) {
            $lockedAccount = true;
            $em = new ErrorMessage(_("This account is locked by the LDAP directory."));
            print $em->display();
        }
    }
    // check if all modules are disabled
    // TODO
    $disabledAccount = false;
    // call all plugins edit function
    callPluginFunction("baseEdit", array($FH, $mode));
    ?>

    <input name="buser" type="submit" class="btnPrimary" value="<?php echo _("Confirm"); ?>" />

    <?php

    if($mode == 'edit') {
        $lockButton = new Button();
        if ($lockedAccount) {
            print $lockButton->getButtonString("unlockAccount",_("Unlock account"));
        }
        $disableButton = new Button();
        if ($disabledAccount) {
            print $disableButton->getButtonString("enableAccount",_("Enable account"));
        }
        else {
            print $disableButton->getButtonString("disableAccount",_("Disable account"));
        }
    }
    ?>

    <input name="breset" type="reset" class="btnSecondary" onclick="window.location.reload( false );" value="<?=_('Cancel')?>" />
</form>
