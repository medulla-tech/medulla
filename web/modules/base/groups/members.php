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

require("modules/base/includes/groups.inc.php");
require("modules/base/includes/users.inc.php");

?>

<style type="text/css">
<!--

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

require("localSidebar.php");
require("graph/navbar.inc.php");

if (isset($_GET["group"]))
    $group = urldecode($_GET["group"]);
else
    $group = $_POST["group"];

if (isset($_POST)) {
    $members = unserialize(base64_decode($_POST["lmembers"]));
    $users = unserialize(base64_decode($_POST["lusers"]));
}

$forbidden = array();

if (isset($_POST["bdeluser_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            if ($group == getUserPrimaryGroup($member)) {
                /* A user can't be removed from his/her primary group */
                $forbidden[] = $member;
                continue;
            }
            $idx = array_search($member, $members);
            if ($idx !== false) unset($members[$idx]);
        }
    }
} else if (isset($_POST["badduser_x"])) {
    if (isset($_POST["users"])) {
        foreach ($_POST["users"] as $user) {
            $idx = array_search($user, $members);
            if ($idx === false) {
                $members[] = $user;
            }
        }
    }
    sort($members);
    reset($members);
} else if (isset($_POST["bconfirm"])) {
    $curmem = get_members($group);
    $newmem = array_diff($members, $curmem);
    $delmem = array_diff($curmem, $members);

    foreach ($newmem as $new) {
        add_member($group, $new);
        callPluginFunction("addUserToGroup", array($new, $group));
    }
    foreach ($delmem as $del) {
        del_member($group, $del);
        callPluginFunction("delUserFromGroup", array($del, $group));
    }
    if (!isXMLRPCError()) new NotifyWidgetSuccess(_("Group successfully modified"));

    $members = get_members($group);
} else {
    $members = get_members($group);
    # get an array with all user's attributes
    $users = get_users(true);
}

$diff = array();
foreach ($users as $user) {
    if (!in_array($user['uid'], $members))
        $diff[] = $user;
}

if (count($forbidden)) {
    new NotifyWidgetWarning(_("Some users can't be removed from this group because this group is their primary group."));
}

$p = new PageGenerator(sprintf(_("Group members %s"), $group));
$sidemenu->forceActiveItem("index");
$p->setSideMenu($sidemenu);
$p->display();

?>

<form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">

<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr><td style="border: none;">
  <div class="list">
        <h3><?php echo  _("All users"); ?></h3>
    <select multiple size="15" class="list" name="users[]">
<?php
foreach ($diff as $user) {
    $name = formatUsername($user);
    echo "<option value=\"". $user['uid'] ."\">". $name ."</option>\n";
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
      <h3><?php echo  _("Group members"); ?></h3>
    <select multiple size="15" class="list" name="members[]">
<?php
foreach ($members as $member) {
    foreach ($users as $user) {
        if ($user['uid'] == $member) {
            $name = formatUsername($user);
            break;
        }
    }
    echo "<option value=\"".$member."\">". $name ."</option>\n";
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
<input type="submit" name="bconfirm" class="btnPrimary" value="<?php echo  _("Confirm"); ?>" />
<input type="submit" name="breset" class="btnSecondary" value="<?php echo  _("Cancel"); ?>" />
</form>

<?php

function formatUsername($user) {
    if ($user['givenName'] != $user['uid'])
        return $user['givenName'] . " " . $user['sn'] . " (" . $user['uid'] . ")";
    else
        return $user['uid'];
}

?>
