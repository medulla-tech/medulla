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

if (isset($_POST["bback"])) {
    header("Location: ".urlStrRedirect("base/users/index"));
    exit;
}
require("modules/base/includes/users.inc.php");
require("graph/header.inc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");

$user = $_SESSION["login"];

$p = new PageGenerator(_("Change your password"));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_POST["bchpasswd"]) && ($_POST["curpass"] != "") && ($_POST["newpass"] != "") && ($_POST["newpass"] == $_POST["confpass"]) && (check_auth($_SESSION['login'], $_POST["curpass"], $error))) {
    callPluginFunction("changeUserPasswd", array(array($user, prepare_string($_POST["newpass"]), prepare_string($_POST["curpass"]), True)));
    if (!isXMLRPCError())
        $n = new NotifyWidgetSuccess(_("Your password has been changed."));

    header("Location: " . urlStrRedirect("base/users/index"));

?>

<form action="<?php echo "main.php?module=base&submod=users&action=index"; ?>" method="post">
<input type="submit" name="bback" class="btnPrimary" value="<?php echo  _("Change your user's password") ?>" />
</form>

<?php
}
else
{
?>
<form action="<?php echo "main.php?module=base&submod=users&action=passwd"; ?>" method="post">
<p>
<?php echo  _("You are going to change your password") ?>
</p>

<table cellspacing="0">
<tr><td><?php echo  _("Current password") ?></td>
    <td><input name="curpass" type="password" size="23" /></td></tr>
<tr><td><?php echo  _("New password") ?></td>
    <td><input name="newpass" type="password" size="23" /></td></tr>
<tr><td><?php echo  _("Confirm your password") ?></td>
    <td><input name="confpass" type="password" size="23" /></td></tr>
</table>

<input name="user" type="hidden" value="<?php echo $user; ?>" />
<input name="bchpasswd" type="submit" class="btnPrimary" value="<?php echo  _("Change your password") ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?php echo  _("Return") ?>" />
<?php
if (isset($_POST["bchpasswd"]))
{
  if (isset($_POST["bchpasswd"]) && ($_POST["newpass"] == $_POST["confpass"]) && ($_POST["newpass"])) {
    echo _("Invalid current password. Please retry.");
  } else {
    echo _("Passwords are mismatching. Please retry.");
  }
}
?>
</form>

<?php
}

?>
