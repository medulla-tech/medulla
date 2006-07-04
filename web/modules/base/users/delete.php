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
  header("Location: main.php?module=base&submod=users&action=index");
  exit;
}

require("modules/base/includes/users.inc.php");
//require("graph/header.inc.php");

?>


<style type="text/css">
<!--

<?php
require("modules/base/graph/users/index.css");
?>

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Users"),
                    "link" => "main.php?modules=base&submod=users&action=index"),
              array("name" => _("Delete a user")));

//require("localSidebar.php");

//require("graph/navbar.inc.php");

?>

<h2><?= _("Delete user") ?></h2>

<?php
if (isset($_GET["user"]))
{
  $user = urldecode($_GET["user"]);
}
if (isset($_POST["user"]))
{
  $user = $_POST["user"];
}

if (isset($_POST["bdeluser"]))
{
  del_user($user, $_POST["delfiles"]);
  $n = new NotifyWidget();
  $n->add(sprintf(_("User %s has been sucessfully deleted"),$user));
  header("Location: main.php?module=base&submod=users&action=index");
?>


<form action="main.php?module=base&submod=users&action=index" method="post">
<input type="submit" name="bback" class="btnPrimary" value="Retour" />
</form>

<?php
}
else
{
?>

<form action="main.php?module=base&submod=users&action=delete" method="post">
<p>
<?
    printf(_("You will delete user <b>%s</b>."),$user);
?>
</p>

<input type="checkbox" name="delfiles" /> <?= _("Delete all user's files"); ?>
<br>
<br>

<input name="user" type="hidden" value="<?php echo $user; ?>" />
<input name="bdeluser" type="submit" class="btnPrimary" value="<?= _("Delete user"); ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?= _("Cancel"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>

<?php
}
?>
