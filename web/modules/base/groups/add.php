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


require("modules/base/includes/groups.inc.php");

require("graph/header.inc.php");
?>

<style type="text/css">
<!--

<?php
require("modules/base/graph/groups/add.css");
?>

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Groups"),
                    "link" => "main.php?module=base&submod=groups&action=index"),
              array("name" => _("Add a group")));

require("localSidebar.php");

require("graph/navbar.inc.php");

if (isset($_POST["badd"]))
{
  if (!preg_match("/^[a-zA-Z][0-9\-_a-zA-Z ]*$/", $_POST["groupname"]))
    {
      $error = _("Invalid groupname");
    }
    else {

  $groupname = $_POST["groupname"];
  $groupdesc = $_POST["groupdesc"];

  $result = create_group($error, $groupname);
  change_group_desc($groupname,$groupdesc);
  }
}
?>

<h2><?= _("Creation of a new group")?> </h2>

<div class="fixheight"></div>

<p>
<?= _("The groupname can only contains lowercase letters and numeric, and must begin with a letter"); ?>
</p>

<form name="groupform" method="post" action="<? echo $PHP_SELF; ?>">
<table cellspacing="0">
<tr>
<td style="text-align:right;"><?= _("Group name")?></td>
    <td><input id="groupname" name="groupname" type="text" class="textfield" size="23" value="<?php if (isset($error)){echo $groupname;} ?>" /></td>
</tr>
<tr>
<td style="text-align:right;"><?= _("Description")?></td>
    <td><input id="groupdesc" name="groupdesc" type="text" class="textfield" size="23" value="<?php if (isset($error)){echo $groupdesc;} ?>" /></td>

</tr>
</table>

<input name="badd" type="submit" class="btnPrimary" value="<?= _("Create"); ?>" />
<?php
if (isset($_POST["badd"]) && (!isset($error)))
{
  echo $result;
}
if (isset($error))
{
  echo $error;
}
?>
</form>

<script>
document.body.onLoad = document.groupform.groupname.focus();
</script>
