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

global $result;
global $error;
$detailArr = array();

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
        if ($_POST) verify_infos($FH, $mode);
        break;
    case "edit":
        $mode = "edit";
        if ($_POST) verify_infos($FH, $mode);
        break;
    default:
        $mode = false;
        break;
}

function verify_infos($FH, $mode) {

    global $error;

    // verify validity with plugin function
    callPluginFunction("verifInfo", array($FH->getPostValues(), $mode));

    //if this user does not exist (not editing a user)
    if (!$error && $mode == "add") {
        
        $uid = $FH->getPostValue("uid");
        
        if (!exist_user($uid)) {

            if($FH->getPostValue("createHomeDir"))
                $createHomeDir = true;
            else
                $createHomeDir = false;
                
            $ret = add_user($uid, $FH->getPostValue("pass"), $FH->getPostValue("firstname"), $FH->getPostValue("name"), $FH->getPostValue("homeDir"), $createHomeDir, $FH->getPostValue("primary_autocomplete"));
            
            $result = $ret["info"];
            # password doesn't match the pwd policies
            # set randomSmbPwd for samba plugin
            if($ret["code"] == 5) {
                $FH->setValue("randomSmbPwd", 1);
            }
            else {
                $FH->setValue("randomSmbPwd", 0);
            }
            if (strlen($FH->getPostValue('mail')) > 0) 
                changeUserAttributes($uid, "mail", $FH->getPostValue("mail"));
	        if (strlen($FH->getPostValue('loginShell')) > 0) 
	            changeUserAttributes($uid, "loginShell", $FH->getPostValue('loginShell'));

            $_GET["user"] = $uid;
            $newuser = true;

        }
        else { // if user exist
            $error.= _("This user already exists.")."<br/>";
        }
    }
}


/*if (isset($_POST["benable"])) {
    $ret = callPluginFunction("enableUser", $_GET["user"]);
    $result = _("User enabled.");
} elseif (isset($_POST["bdisable"])) {
    $ret = callPluginFunction("disableUser", $_GET["user"]);
    $result = _("User disabled.");
} elseif (isset($_POST["ldapaccountunlock"])) {
    if (in_array("ppolicy", $_SESSION["supportModList"])) {
        require_once("modules/ppolicy/includes/ppolicy-xmlrpc.php");
        unlockAccount($_GET["user"]);
    }
}*/


// if we edit a user
// /!\ if we create a user... add smb attr or OX attr it'll be consider as modification
if (!empty($_GET["user"])) {

    if (!$error) {
    
        global $result;
        $uid = $FH->getPostValue("uid");
        
        if ($FH->isUpdated("deletephoto")) {
            changeUserAttributes($_POST["uid"], "jpegPhoto", null);
        }
        else if (isset($_POST["buser"])) { //if we submit modification        

            // Change user attributes
            if($FH->isUpdated('isBaseDesactive')) {
                if ($FH->getValue('isBaseDesactive') == "on") { //desactive user
                    changeUserAttributes($uid, 'loginShell', '/bin/false');
                    $result .= _("User disabled.")."<br />";
                }
                else {
                    changeUserAttributes($uid, 'loginShell', '/bin/bash');
                    $result .= _("User enabled.")."<br />";
                }
            }            
            if ($FH->isUpdated("homeDir"))
                move_home($uid, $_POST["homeDir"]);
            if($FH->isUpdated('telephoneNumber'))
                changeUserTelephoneNumbers($uid, $_POST["telephoneNumber"]);
            if($FH->isUpdated('title'))
                changeUserAttributes($uid, "title", $_POST["title"]);
            if($FH->isUpdated('mobile'))
                changeUserAttributes($uid, "mobile", $_POST["mobile"]);
            if($FH->isUpdated('facsimileTelephoneNumber'))
                changeUserAttributes($uid, "facsimileTelephoneNumber", $_POST["facsimileTelephoneNumber"]);
            if($FH->isUpdated('homePhone'))
                changeUserAttributes($uid, "homePhone", $_POST["homePhone"]);
            if($FH->isUpdated('cn'))
                changeUserAttributes($uid, "cn", $_POST["cn"]);        
            if($FH->isUpdated('mail'))
                changeUserAttributes($uid, "mail", $_POST["mail"]);
            if($FH->isUpdated('displayName'))
                changeUserAttributes($uid, "displayName", $_POST["displayName"]);

            /* Change photo */
            if (!empty($_FILES["photofilename"]["name"])) {            
                if (strtolower(substr($_FILES["photofilename"]["name"], -3)) == "jpg") {
                    $pfile = $_FILES["photofilename"]["tmp_name"];
                    $size = getimagesize($pfile);
                    if ($size["mime"] == "image/jpeg") {
                        $maxwidth = 320;
                        $maxheight = 320;
                        if (in_array("gd", get_loaded_extensions())) {
                            /* Resize file if GD extension is installed */
                            $pfile = resizeJpg($_FILES["photofilename"]["tmp_name"], 
                                    $maxwidth, $maxheight);                         
                        }
                        list($width, $height) = getimagesize($pfile);
                        if (($width <= $maxwidth) && ($height <= $maxheight)) {
                            $obj = new Trans();
                            $obj->scalar = "";
                            $obj->xmlrpc_type = "base64";
                            $f = fopen($pfile, "r");
                            while (!feof($f)) $obj->scalar .= fread($f, 4096);  
                            fclose($f);
                            unlink($pfile);
                            changeUserAttributes($uid, "jpegPhoto", $obj, False);
                        } 
                        else {
                            $error .= sprintf(_("The photo is too big. The max size is %s x %s."), 
                                $maxwidth, $maxheight) . "<br/>";
                        }
                    } 
                    else $error .= _("The photo is not a JPG file.") . "<br/>";
                } 
                else $error .= _("The photo is not a JPG file.") . "<br/>";
            }	 

            if($FH->isUpdated('firstname') or $FH->isUpdated('name'))
                change_user_main_attr($_GET["user"], $uid, $firstname, $name);

            if (!$FH->getPostValue("groupsselected")) $FH->setPostValue("groupsselected", array());
            
            // Create/modify user in all enabled MMC modules
            callPluginFunction("changeUser", array($FH));

            /* Primary group management */
            if($FH->isUpdated("primary")) {
                $primaryGroup = getUserPrimaryGroup($uid);
                if ($FH->getValue("primary") != $primaryGroup) {
                    /* Update the primary group */
                    callPluginFunction("changeUserPrimaryGroup", array($uid, 
                    $FH->getValue("primary"), $primaryGroup));
                }
            }

            print_r($_POST);

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
            
            // If we change the password of an already existing user
            if (($_POST["pass"] == $_POST["confpass"]) && ($_POST["pass"] != "") && ($_GET["action"] != "add")) {
                $ret = callPluginFunction("changeUserPasswd", array(array($_GET["user"], prepare_string($_POST["pass"]))));
                if(isXMLRPCError()) {
                    foreach($ret as $info) {
                        $result .= "<strong>"._("Password not updated");
                        $result .= " "._($info)."</strong><br/>";
                    }
                    # set errorStatus to 0 in order to make next xmlcalls
                    global $errorStatus;
                    $errorStatus = 0;
                } 
                else {
                    //update result display
                    $result .= _("Password updated.")."<br />";
                }
            }                
            $result.=_("Attributes updated.")."<br />";
        }
    }
    $detailArr = getDetailedUser($_GET["user"]);

    // Fetch uid/gid if we create a user
    if ($_GET["action"] == "add") {
        $detailArr["uidNumber"][0] = maxUID() + 1;
        $detailArr["gidNumber"][0] = maxGID() + 1;
    }
    
    $enabled = isEnabled($_GET["user"]);
}

// message is set from add_user xml call, line 135
/*if (strstr($_SERVER['HTTP_REFERER'],'module=base&submod=users&action=add') && isset($_GET["user"])) {
    if (!isXMLRPCError()) {
        $result = sprintf(_("User %s has been successfully created."), $_GET["user"]);
    }
}*/

$FH->setArr($detailArr);

//display result message
if (isset($result)&&!isXMLRPCError()) {
    new NotifyWidgetSuccess($result);
}

//display error message
if (isset($error)) {
    new NotifyWidgetFailure($error);
}

if (isset($_SESSION["addusererror"])) {
    new NotifyWidgetWarning("The user has not been completely created because of the following error(s):" . "<br/><br/>" .  $_SESSION["addusererror"]);
    unset($_SESSION["addusererror"]);
}

// title differ with action
if ($mode == "add") {
    $title = _("Add user");
    $activeItem = "add";
} else {
    $title = _("Edit user");
    $activeItem = "index";
}

$p = new PageGenerator($title);
$sidemenu->forceActiveItem($activeItem);
$p->setSideMenu($sidemenu);
$p->display();

?>
<form id="edit" enctype="multipart/form-data" method="post" onsubmit="selectAll(); return validateForm();">
<?php

//call plugin baseEdit form
callPluginFunction("baseEdit", array($FH, $mode));

?>
    <input name="buser" type="submit" class="btnPrimary" value="<?= _("Confirm"); ?>" />
<?
    if ($ldapAccountLocked) {
        $unlockButton = new Button();
        print $unlockButton->getButtonString("ldapaccountunlock",_("Unlock LDAP account"));
    }
?>
    <input name="breset" type="reset" class="btnSecondary" onclick="window.location.reload( false );" value="<?=_('Cancel')?>" />
</form>

<?php

//if we create a new user redir in edition
if (isset($newuser) && !isXMLRPCError()) {
    if (isset($error)) {
        /* We will use this variable to display a warning on the edit page */
        $_SESSION["addusererror"] = $error;
    }
    header("Location: " . urlStrRedirect("base/users/edit", array("user" => $uid)));
}

/**
 * Resize a jpg file if it is greater than $maxwidth or $maxheight
 * 
 * @returns: the file name of the resized JPG file
 */
function resizeJpg($source, $maxwidth, $maxheight) {
    list($width, $height) = getimagesize($source);
    if (($width > $maxwidth) || ($height > $maxheight)) {
        if ($width > $height) {
            $newwidth = $maxwidth;
            $newheight = $newwidth * $height / $width;
        } else {
            $newheight = $maxheight;
            $newwidth = $newheight * $width / $height;
        }
        $image = imagecreatefromjpeg($source);
        $newimage = imagecreatetruecolor($newwidth, $newheight);
        imagecopyresized($newimage, $image, 0, 0, 0, 0, $newwidth, $newheight, $width, $height);
        $ret = tempnam("/notexist", ".jpg");
        imagejpeg($newimage, $ret);
        imagedestroy($image);
        imagedestroy($newimage);
    } else {
        /* No resize needed */
        $ret = $source; 
    }
    return $ret;
}

?>
