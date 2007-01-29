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
<?php
/* $Id$ */


if (isset($_POST["bback"]))
{
    header("Location: ".urlStrRedirect("base/users/index"));
    exit;
}
require("modules/base/includes/users.inc.php");
require("graph/header.inc.php");

?>


<style type="text/css">
<!--

<?php
require("modules/base/graph/users/passwd.css");
?>

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Users"),
                    "link" => "main.php?module=base&submod=users&action=index"),
              array("name" => _("Change your password")));

require("localSidebar.php");
require("graph/navbar.inc.php");

$user = $_SESSION["login"];
?>

<h2><?= _("Change your password") ?></h2>

<div class="fixheight"></div>

<?php

if (isset($_POST["bchpasswd"]) && ($_POST["curpass"] != "") && ($_POST["newpass"] != "") && ($_POST["newpass"] == $_POST["confpass"]) && (check_auth($_SESSION['login'], $_POST["curpass"], $error)))
{
  callPluginFunction("changeUserPasswd", array(array($user, $_POST["newpass"])));

?>

<?
$n = new NotifyWidget();
$n->add(_("Your password has been changed."));

header("Location: " . urlStrRedirect("base/users/index"));
?>

<form action="<? echo "main.php?module=base&submod=users&action=index"; ?>" method="post">
<input type="submit" name="bback" class="btnPrimary" value="<?= _("Change your user's password") ?>" />
</form>

<?php
}
else
{
?>
<form action="<? echo "main.php?module=base&submod=users&action=passwd"; ?>" method="post">
<p>
<?= _("You are going to change your password") ?>
</p>

<table cellspacing="0">
<tr><td><?= _("Current password") ?></td>
    <td><input name="curpass" type="password" class="textfield" size="23" /></td></tr>
<tr><td><?= _("New password") ?></td>
    <td><input name="newpass" type="password" class="textfield" size="23" /></td></tr>
<tr><td><?= _("Confirm your password") ?></td>
    <td><input name="confpass" type="password" class="textfield" size="23" /></td></tr>
</table>

<input name="user" type="hidden" value="<?php echo $user; ?>" />
<input name="bchpasswd" type="submit" class="btnPrimary" value="<?= _("Change your password") ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?= _("Return") ?>" />
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
