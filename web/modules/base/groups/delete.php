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


require("modules/base/includes/groups.inc.php");

if (isset($_POST["bback"]))
{
  header("Location: main.php?module=base&submod=groups&action=index");
  exit;
}

?>

<style type="text/css">
<!--

<?php
require("modules/base/graph/groups/index.css");
?>

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Groups"),
                    "link" => "main.php?module=base&submod=groups&action=index"),
              array("name" => _("Delete a group")));

//require("localSidebar.php");

//require("graph/navbar.inc.php");

if (isset($_POST["bconfirm"]))
{
  $group = $_POST["groupname"];

  $result = del_group($group);
}
else
{
  $group = urldecode($_GET["group"]);
}

?>

<h2><?= _("Delete group"); ?> <?php echo $group; ?></h2>

<!--<div class="fixheight"></div>!-->

<?php
if (isset($_POST["bconfirm"]))
{

$n = new NotifyWidget();
$n->add($result);
header("Location: main.php?module=base&submod=groups&action=index");
exit;

}
else
{
?>

<p>
<?= _("You will delete group"); ?> <strong><?php echo $group; ?></strong>.
</p>
<p>
<?= _("This group will be deleted even though it is not empty"); ?>
</p>

<form action="main.php?module=base&submod=groups&action=delete" method="post">
<input type="hidden" name="groupname" value="<?php echo $group; ?>" />
<input type="submit" name="bconfirm" class="btnPrimary" value="<?= _("Delete group"); ?>" />
<input type="submit" name="bback" class="btnSecondary" value="<?= _("Return"); ?>" onClick="new Effect.Fade('popup'); return false;" />
</form>

<?php
}
?>
