<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require("modules/base/includes/groups.inc.php");
require("modules/base/includes/users.inc.php");

function transform_users($users)
{
    return array_map(function ($user) {
        foreach ($user as $key => $value) {
            if (is_object($value) && property_exists($value, 'scalar')) {
                $user[$key] = $value->scalar;
            } elseif (is_array($value)) {
                $user[$key] = array_map(function ($item) {
                    return is_object($item) && property_exists($item, 'scalar') ? $item->scalar : $item;
                }, $value);
            }
        }
        return $user;
    }, $users);
}
?>

<style type="text/css">

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

</style>

<?php

require("localSidebar.php");
require("graph/navbar.inc.php");

if (isset($_GET["group"])) {
    $group = urldecode($_GET["group"]);
} else {
    $group = $_POST["group"];
}

if (isset($_POST)) {
    if(isset($_POST['lmembers'], $_POST['lusers'])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $users = unserialize(base64_decode($_POST["lusers"]));
    } else {
        $members = [];
        $users = [];
    }
}
$forbidden = array();

if (isset($_POST["bdeluser_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            if ($group == getUserPrimaryGroup($member)->scalar) {
                /* A user can't be removed from his/her primary group */
                $forbidden[] = $member;
                continue;
            }
            $idx = array_search($member, $members);
            if ($idx !== false) {
                unset($members[$idx]);
            }
        }
    }
} elseif (isset($_POST["badduser_x"])) {
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
} elseif (isset($_POST["bconfirm"])) {
    $curmem = get_members($group);
    $curmem = array_map(function ($member) {
        return is_object($member) && property_exists($member, 'scalar') ? $member->scalar : $member;
    }, $curmem);

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
    if (!isXMLRPCError()) {
        new NotifyWidgetSuccess(_("Group successfully modified"));
        header("Location: " . urlStrRedirect("base/groups/index"));
        exit;
    }

    $members = get_members($group);
    $members = array_map(function ($member) {
        return is_object($member) && property_exists($member, 'scalar') ? $member->scalar : $member;
    }, $members);
} else {
    $members = get_members($group);
    $members = array_map(function ($member) {
        return is_object($member) && property_exists($member, 'scalar') ? $member->scalar : $member;
    }, $members);
    # get an array with all user's attributes
    $users = get_users(true);
    $users = transform_users($users);
}

$diff = array();
foreach ($users as $user) {
    if (!in_array($user['uid'], $members)) {
        $diff[] = $user;
    }
}

if (safeCount($forbidden)) {
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
  <input type="image" name="badduser" style="padding: 5px;" src="img/other/right.svg" width="25" height="25" value = "-->"/><br/>
  <input type="image" name="bdeluser" style="padding: 5px;" src="img/other/left.svg" width="25" height="25" value="<--" />
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

function formatUsername($user)
{
    if ($user['givenName'] != $user['uid']) {
        return $user['givenName'] . " " . $user['sn'] . " (" . $user['uid'] . ")";
    } else {
        return $user['uid'];
    }
}

?>
