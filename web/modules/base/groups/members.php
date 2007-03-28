<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
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
require("modules/base/includes/users.inc.php");

require("graph/header.inc.php");
?>

<style type="text/css">
<!--

<?php
require("modules/base/graph/groups/index.css");
?>

#grouplist
{
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        padding: 10px 5px 5px 10px;
        margin: 0 5px 20px 0;
        width: 632px;
}

#grouplist div.list
{
        float: left;
}

select.list
{
        width: 250px;
}

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Groups"),
                    "link" => "main.php?module=base&submod=groups&action=index"),
              array("name" => _("Group members")));

require("localSidebar.php");

require("graph/navbar.inc.php");

if (isset($_GET["group"]))
{
  $group = urldecode($_GET["group"]);
}
else
{
  $group = $_POST["group"];
}

$members = unserialize(base64_decode($_POST["lmembers"]));
$users = unserialize(base64_decode($_POST["lusers"]));

$forbidden = array();

if (isset($_POST["bdeluser_x"]))
{
  foreach ($_POST["members"] as $member) {
      if ($group == getUserPrimaryGroup($member)) {
          /* A user can't be removed from his/her primary group */
          $forbidden[] = $member;
          continue;
      }
      $idx = array_search($member, $members);
      if ($idx !== false)
	{
	  unset($members[$idx]);
	}
    }
}
else if (isset($_POST["badduser_x"]))
{
  foreach ($_POST["users"] as $user)
    {
      $idx = array_search($user, $members);
      if ($idx === false)
	{
	  $members[] = $user;
	}
    }

  sort($members);
  reset($members);
}
else if (isset($_POST["bconfirm"]))
{
  $curmem = get_members($group);

  $newmem = array_diff($members, $curmem);
  $delmem = array_diff($curmem, $members);

  foreach ($newmem as $new)
    {
      add_member($group, $new);
      callPluginFunction("addUserToGroup", array($new, $group));
    }
  foreach ($delmem as $del)
    {
      del_member($group, $del);
      callPluginFunction("delUserFromGroup", array($del, $group));
    }
  if (!isXMLRPCError()) {
    $n = new NotifyWidget();
    $n->add(_T("Group successfully modified"));
  }


  $members = get_members($group);
}
else // breset
{
  $members = get_members($group);
  $users = get_users($error);

}

 $diff = array_diff($users,$members);

if (count($forbidden)) {
    $n = new NotifyWidget();
    $n->flush();
    $n->add("<div id=\"validCode\">" . _("Some users can't be removed from this group because this group is their primary group.") . "</div>");
    $n->setLevel(0);
    $n->setSize(600);
}
?>

<h2><?= _("Group members"); ?> <?php echo $group; ?></h2>

<div class="fixheight"></div>

<form action="<? echo $_SERVER["REQUEST_URI"]; ?>" method="post">

<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr><td style="border: none;">
  <div class="list">
        <h3><?= _("All users");?></h3>
    <select multiple size="15" class="list" name="users[]">
<?php
foreach ($diff as $idx => $user)
{
  if ($user == "")
  {
    unset($users[$idx]);
    continue;
  }

  echo "<option value=\"".$user."\">".$user."</option>\n";
}
?>
    </select>

    <br>

  </div>
  </td><td style="border: none;">
  <div>
  <input type="image" name="bdeluser" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" /><br/>
  <input type="image" name="badduser" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/>
  </div>
  </td><td style="border: none;">

  <div class="list" style="padding-left: 10px;">
      <h3><?= _("Group members"); ?></h3>
    <select multiple size="15" class="list" name="members[]">
<?php
foreach ($members as $idx => $member)
{
  if ($member == "")
  {
    unset($members[$idx]);
    continue;
  }

  echo "<option value=\"".$member."\">".$member."</option>\n";
}
?>
    </select>

    <br>

  </div>
  <div class="clearer"></div>
  </td></tr>
</table>
</div>

<input type="hidden" name="lusers" value="<?php echo base64_encode(serialize($users)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
<input type="hidden" name="group" value="<?php echo $group; ?>" />
<input type="submit" name="bconfirm" class="btnPrimary" value="<?= _("Confirm"); ?>" />
<input type="submit" name="breset" class="btnSecondary" value="<?= _("Cancel"); ?>" />
</form>
