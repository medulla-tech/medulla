<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<style type="text/css">
<!--

<?php



global $conf;
global $result;

if ($_GET["action"]=="add") {
    require("modules/base/graph/users/add.css");
}
require("modules/base/includes/users.inc.php");
require("modules/base/includes/groups.inc.php");

//unset form local var
unset($_SESSION["affectGroup"]);
unset($_SESSION["possibleGroup"]);


?>

#expertMode table {
	background-color: #FEE;
}


-->
</style>
<?php

require("localSidebar.php");

require("graph/navbar.inc.php");


//verify validity of information
if (isset($_POST["buser"])) {

global $error;
$nlogin = $_POST["nlogin"];
$name = $_POST["name"];
$firstname = $_POST["firstname"];
$confpass = $_POST["confpass"];
$homedir = $_POST["homeDir"];

$detailArr["cn"][0]=$nlogin;
$detailArr["givenName"][0]=$firstname;
$detailArr["sn"][0]=$name;
$pass = $_POST["pass"];
$desactive = $_POST["isBaseDesactive"];

if ($pass != $confpass) {
    $error.= _("Password confirmation mismatch")." <br/>";
    setFormError("pass");
}

if (!preg_match("/^[a-zA-Z][A-Za-z0-9_.-]*$/", $nlogin)) {
    $error.= _("User's name invalid !")."<br/>";
    setFormError("login");
}

if (!preg_match('/^((\+){0,1}[a-zA-Z0-9 ]+){0,1}$/', $_POST["telephoneNumber"]))  {
    global $error;
    setFormError("telephoneNumber");
    $error.= _("This is not a valid telephone number.")."<br />";
}

/* Check that the primary group name exists */
 $primary = $_POST["primary_autocomplete"];
 if (!strlen($primary)) {
   global $error;
    setFormError("primary_autocomplete");
    $error.= _("The primary group field can't be empty.")."<br />";
} else if (!existGroup($primary)) {
    global $error;
    setFormError("primary_autocomplete");
    $error.= sprintf(_("The group %s does not exist, and so can't be set as primary group."), $primary) . "<br />";
 }


//verify validity with plugin function
callPluginFunction("verifInfo",array($_POST));


    //if this user does not exist (not editing a user)
    if (!$error&&($_GET["action"]=="add")) {
        if (!exist_user($nlogin)) {
            if ($pass =='') {//if we not precise a password
                $error.= _("Password is empty.")."<br/>"; //refuse addition
                setFormError("pass");
            } else {  //if no problem
                $result = add_user($nlogin, $pass, $firstname, $name, $homedir, $_POST["primary_autocomplete"]);
                changeUserAttributes($nlogin, 'telephoneNumber', $_POST['telephoneNumber']);
                changeUserAttributes($nlogin, 'mail', $_POST['mail']);
                $_GET["user"]=$nlogin;
                $newuser=true;
            }
        }
        else { //if user exist
            $error.= _("This user already exists.")."<br/>";
        }
    }
} elseif ($_POST["benable"]) {
    $ret = callPluginFunction("enableUser", $_GET["user"]);
    $result = _("User enabled.");
} elseif ($_POST["bdisable"]) {
    $ret = callPluginFunction("disableUser",$_GET["user"]);
    $result = _("User disabled.");
}


//if we edit a user
// /!\ if we create a user... add smb attr or OX attr
// it'll be consider as modification
if ($_GET["user"]) {

  if (!$error) {
      global $result;
      if ($_POST["buser"]) { //if we submit modification

         if ($_POST['isBaseDesactive']) { //desactive user
            changeUserAttributes($nlogin,'loginShell','/bin/false');
            $result .= _("User disabled.")."<br />";
         } else { //else if it desactive, reactive him
            $detailArr = getDetailedUser($_GET["user"]);
            if ($detailArr["loginShell"][0]=='/bin/false') {
                changeUserAttributes($nlogin,'loginShell','/bin/bash');
                $result .= _("User enabled.")."<br />";
            }
         }

         if ($_POST["homeDir"]) {
            move_home($nlogin,$_POST["homeDir"]);
         }

         //change phone number
         changeUserAttributes($nlogin,'telephoneNumber',$_POST['telephoneNumber']);
         changeUserAttributes($nlogin,'mail',$_POST['mail']);

         change_user_main_attr($_GET["user"], $nlogin, $firstname, $name);
         $result.=_("Attributes updated.")."<br />";

         //modification/creation for all plugins
         callPluginFunction("changeUser",array($_POST));

          //if we change the password
          if (($_POST["pass"] == $_POST["confpass"]) && ($_POST["pass"] != "")) {
	    callPluginFunction("changeUserPasswd", array(array($_GET["user"], $_POST["pass"])));

            //update result display
            $result.=_("Password updated.")."<br />";
          }

	  /* Primary group management */
          if ($_POST["primary_autocomplete"] != getUserPrimaryGroup($_POST['nlogin'])) {
              /* Update the primary group */
              callPluginFunction("changeUserPrimaryGroup", array($_POST['nlogin'], $_POST["primary_autocomplete"]));
	  }

         /* Secondary groups management */
         if (!isset($_POST["groupsselected"])) $_POST["groupsselected"] = array();
         $old = getUserSecondaryGroups($_POST['nlogin']);
         $new = $_POST['groupsselected'];
         foreach (array_diff($old,$new) as $group) {
             del_member($group,$_POST['nlogin']);
         }
         foreach (array_diff($new,$old) as $group) {
             add_member($group,$_POST['nlogin']);
         }

     }
  }
  $detailArr = getDetailedUser($_GET["user"]);

  $enabled = isEnabled($_GET["user"]);
  //updating /homedir if needed
}

if (strstr($_SERVER[HTTP_REFERER],'module=base&submod=users&action=add') && $_GET["user"])
    if (!isXMLRPCError()) {
     $result = sprintf(_("User %s created without problems"), $_GET["user"]);
    }

//display result message
if (isset($result)&&!isXMLRPCError())
{
    $n = new NotifyWidget();
    $n->flush();
    $n->add("<div id=\"validCode\">$result</div>");
    $n->setLevel(0);
    $n->setSize(600);
}

//display error message
if (isset($error)) {
    $n = new NotifyWidget();
    $n->flush();
    $n->add("<div id=\"errorCode\">$error</div>");
    $n->setLevel(4);
    $n->setSize(600);
}



//title differ with action
if ($_GET["action"]=="add") {
    print "<h2>"._("Add user")."</h2>";
  }
  else {
    print '<h2>'._("Edit user").'</h2>';
  }

?>
<div class="fixheight"></div>

<div>
<form id="edit" method="post" action="<? echo $PHP_SELF; ?>" onSubmit="selectAll(); return validateForm();">
<div class="formblock" style="background-color: #F4F4F4;">
<table cellspacing="0">
<?php

 // Fetch uid/gid if we create a user
 if ($_GET["action"] == "add") {
     $detailArr["uidNumber"][0] = maxUID() + 1;
     $detailArr["gidNumber"][0] = maxGID() + 1;
 }
?>
<?php

//display form

if ($_GET["action"]=="add") {
    $formElt = new InputTpl("nlogin",'/^[a-zA-Z][A-Za-z0-9_.-]*$/');
} else {
    $formElt = new HiddenTpl("nlogin");
}


$test = new TrFormElement(_("Login"),$formElt);
$test->setCssError("login");
$test->display(array("value"=>$detailArr["uid"][0]));

$test = new TrFormElement(_("Name"),new InputTpl("name"));
$test->display(array("value"=>$detailArr["sn"][0]));

$test = new TrFormElement(_("First name"),new InputTpl("firstname"));
$test->display(array("value"=>$detailArr["givenName"][0]));


$test = new TrFormElement(_("Password"),new PasswordTpl("pass"));
$test->setCssError("pass");
$test->display(null);

$test = new TrFormElement(_("Confirm password"),new PasswordTpl("confpass"));
$test->setCssError("pass");
$test->display(null);


$test = new TrFormElement(_("Mail address"),new InputTpl("mail",'/^([A-Za-z0-9._%-]+@[A-Za-z0-9.-]+){0,1}$/'));
$test->setCssError("mail");
$test->display(array("value"=>$detailArr["mail"][0]));

$test = new TrFormElement(_("Telephone number"),new InputTpl("telephoneNumber"));
$test->setCssError("telephoneNumber");
$test->display(array("value"=>$detailArr["telephoneNumber"][0]));



$checked="";
if ($detailArr["uid"][0]) {
if ($detailArr["loginShell"][0]=='/bin/false') {
            $checked = "checked";
        }
}
$param = array ("value" => $checked);

$test = new TrFormElement(_("User is disabled, if checked"), new CheckboxTpl("isBaseDesactive"),
        array("tooltip"=>_("Disabled users cannot be logged into any services. <br/>
                            Shell command are replaced by /bin/false"))
        );
$test->setCssError("isBaseDesactive");
$test->display($param);

?>
</table>
<div id="expertMode" <?displayExpertCss();?>>
<table cellspacing="0">
<?php

$test = new TrFormElement(_("Home directory"),new InputTpl("homeDir"));
$test->display(array("value"=>$detailArr["homeDirectory"][0]));
?>

<tr><td style="text-align: right;"><? print "UID : ".$detailArr["uidNumber"][0]; ?></td>
<td><? print "GID : ".$detailArr["gidNumber"][0];?></td></tr>


</table>
</div>


<?php

setVar('detailArr',$detailArr);

$existACL = existAclAttr("groups");

if (!$existACL) {
    $aclattrright = "rw";
    $isAclattrright = true;
} else {
    $aclattrright = getAclAttr("groups");
    $isAclattrright = ($aclattrright != '');
}

if ($aclattrright=="rw") {
    renderTPL("editGroups");
} else {
    if ($aclattrright=="ro") {
        renderTPL("roGroups");
    }  else {
        renderTPL("norightGroups");
    }
}


print '</div>';

//call plugin baseEdit form
callPluginFunction("baseEdit",array($detailArr,$_POST));
?>

</table>

<input name="buser" type="submit" class="btnPrimary" value="<?= _("Confirm"); ?>" />
<input name="breset" type="reset" class="btnSecondary" onclick="window.location.reload( false );" value="<?= _("Cancel"); ?>" />



</form>
</div>

<?php

//if we create a new user redir in edition
if ($newuser&&!isXMLRPCError()) {
  header("Location: main.php?module=base&submod=users&action=edit&user=$nlogin");
}


?>
