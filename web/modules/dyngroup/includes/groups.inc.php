<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

if(in_array("imaging", $_SESSION["modulesList"]))
    require_once('modules/imaging/includes/xmlrpc.inc.php');

require_once('modules/dyngroup/includes/dyngroup.php'); // for getPGobject method

function drawGroupShare($nonmemb, $members, $listOfMembers, $diff, $gid, $name) {
?>
<form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<input name="name" value="<?php echo  $name ?>" type="hidden" />
<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr>
 <td style="border: none;">
  <div class="list">
    <h3><?php echo  _T("All share entities", "dyngroup"); ?></h3>
    <select multiple size="15" class="list" name="nonmemb[]">
    <?php
    foreach ($diff as $idx => $user) {
        if ($user == "") { unset($nonmemb[$idx]); continue; }
        $style = '';
        $ma = preg_split("/##/", $idx);
        if ($ma[0] == 1) { $style = ' style="background-color: #eedd00;"'; }
        echo "<option$style value=\"".$idx."\">".$user."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
 </td>
 <td style="border: none;">
  <div>
   <input type="image" name="badduser" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/><br/>
   <input type="image" name="bdeluser" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" />
  </div>
 </td>
 <td style="border: none;">
  <div class="list" style="padding-left: 10px;">
    <h3><?php echo  _T("Group share", "dyngroup"); ?></h3>
    <select multiple size="15" class="list" name="members[]">
    <?php
    foreach ($members as $idx => $member) {
        if ($member == "") { unset($members[$idx]); continue; }
        $style = '';
        $ma = preg_split("/##/", $idx);
        if ($ma[0] == 1) { $style = ' style="background-color: #eedd00;"'; }
        echo "<option$style value=\"".$idx."\">".$member."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
  <div class="clearer"></div>
 </td>
</tr>
</table>
</div>

<input type="hidden" name="lnonmemb" value="<?php echo base64_encode(serialize($nonmemb)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
<input type="hidden" name="lsmembers" value="<?php echo base64_encode(serialize($listOfMembers)); ?>" />
<input type="hidden" name="id" value="<?php echo  $gid ?>" />
<input type="submit" name="bconfirm" class="btnPrimary" value="<?php echo  _("Confirm"); ?>" />
<input type="submit" name="breset" class="btnSecondary" value="<?php echo  _("Cancel"); ?>" />
</form>

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
}

function drawGroupList($machines, $members, $listOfMembers, $visibility, $diff, $gid, $name, $filter = '', $type = 0) {
    if ($type == 0) {
        $label_name = _T('Group name', 'dyngroup');
        $label_visible = _T('Make favourite', 'dyngroup');
        $label_members = _T("Group members", "dyngroup");
    } else {
        $label_name = _T('Group name', 'dyngroup'); // Imaging group
        $label_visible = _T('Make favourite', 'dyngroup');
        $label_members = _T("Group members", "dyngroup");
    }
    $willBeUnregistered = array();
    if ($type == 1) {
        $listOfMembersUuids = array_keys($listOfMembers);
        foreach ($listOfMembersUuids as $target_uuid) {
            $ret = xmlrpc_canIRegisterThisComputer($target_uuid);
            if (!$ret[0]) {
                $willBeUnregistered[] = $target_uuid;
            }
            elseif ($ret[0] && isset($ret[1]) && $ret[1] != False) {
                $willBeUnregistered[] = $target_uuid;
            }
        }
    }

    $currentGroup = getPGobject($gid, true);
    if ($type == 1) {
        // Check if machines who are displayed are part of an existing profile
        $machinesInProfile = arePartOfAProfile(array_keys($listOfMembers));

        // If we edit an imaging group, exclude machines of current group. else they
        // will be reported as machines in imaging group
        $computersgroupedit = 0;
        if (isset($_GET['action']) && $_GET['action'] == 'computersgroupedit') {
            $computersgroupedit = 1;
            $i = 0;
            foreach ($machinesInProfile as $uuid => $group) {
                if ($group['groupname'] == $currentGroup->name) {
                    unset($machinesInProfile[$uuid]);
                    unset($willBeUnregistered[array_search($uuid, $willBeUnregistered)]);
                }
                $i++;
            }
        }
    }

?>

<form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<table style="border: none;" cellspacing="0">
<tr><td><?php echo  $label_name; ?></td><td></td><td><input name="name" value="<?php echo  $name ?>" type="text"/></td></tr>
<tr><td><?php echo  $label_visible; ?></td><td></td><td>
    <input name='visible' value='show' <?php if ($visibility == 'show') { echo 'checked'; } ?> type='radio'/><?php echo  _T('Yes', 'dyngroup') ?> 
    <input name='visible' value='hide' <?php if ($visibility != 'show') { echo 'checked'; } ?> type='radio'/><?php echo  _T('No', 'dyngroup') ?>
</td></tr>
<!-- add all group inupts -->
</table>

<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr>
 <td style="border: none;">
  <div class="list">
    <h3><?php echo  _T("All machines", "dyngroup"); ?></h3>
    <input name='filter' type='text' value='<?php echo  $filter ?>'/>
    <input type="image" name="bfiltmachine" style="padding: 5px;" src="img/common/icn_show.gif" value = "-->"/>
    <br/><br/>
    <select multiple size="13" class="list" name="machines[]">
    <?php
    foreach ($diff as $idx => $machine) {
        if ($machine == "") { unset($machines[$idx]); continue; }
        echo "<option value=\"".$idx."\">".$machine."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
 </td>
 <td style="border: none;">
  <div>
   <input type="image" name="baddmachine" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/><br/>
   <input type="image" name="bdelmachine" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" />
  </div>
 </td>
 <td style="border: none;">
  <div class="list" style="padding-left: 10px;">
    <h3><?php echo  $label_members; ?></h3>
    <select multiple size="15" class="list" name="members[]">
    <?php
    foreach ($members as $idx => $member) {
        $currentUuid = explode('##', $idx);
        $currentUuid = $currentUuid[1];
        if ($member == "") {
            unset($members[$idx]);
            continue;
        }

        $style = '';
        if ($type == 1) { // Imaging group

            // Check if machines who are displayed are part of an existing profile
            if (in_array($currentUuid, array_keys($machinesInProfile))) {
                $style = 'background: red; color: white;';
            }
            // Or if they're registered in imaging as stand-alone machines
            elseif (in_array($currentUuid, $willBeUnregistered)) {
                $style = 'background: purple; color: white;';
            }
        }
        echo "<option style=\"" . $style . "\" value=\"".$idx."\">".$member."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
  <div class="clearer"></div>
 </td>
</tr>
</table>
</div>

<?php
    if ($type == 1) { // Imaging group
        $warningMessage = False;
        if (count($machinesInProfile) > 0) {
            $warningMessage = True;
            print '<p>';
            print _T('Computers listed below are already part of another imaging group.', 'dyngroup');
            echo '<ul>';
            foreach($machinesInProfile as $machineUuid => $group) {
                printf(_T('<li>%s is part of <a href="%s">%s</a></li>'),
                    $listOfMembers[$machineUuid]['hostname'],
                    urlStrRedirect('imaging/manage/display', array('gid' => $group['groupid'], 'groupname' => $group['groupname'])),
                    $group['groupname']);
            }
            echo '</ul>';
            print '</p>';
        }
        $standAloneImagingRegistered = array_diff($willBeUnregistered, array_keys($machinesInProfile));
        if (count($standAloneImagingRegistered) > 0) {
            $warningMessage = True;
            print '<p>';
            print _T('Computers listed below are already stand-alone registered in imaging.', 'dyngroup');
            echo '<ul>';
            foreach($standAloneImagingRegistered as $machineUuid) {
                printf('<li>%s</li>', $listOfMembers[$machineUuid]['hostname']);
            }
            echo '</ul>';
            print '</p>';
        }

        if ($warningMessage) {
            echo _T('<p>These computers will move to this group and their bootmenus <strong>will be rewritten</strong></p>', 'dyngroup');
            echo '<p>' . _T('All related images to these computers will be <strong>DELETED</strong>', 'dyngroup') . '</p>';
        }
    }
?>

<input type="hidden" name="type" value="<?php echo  $type; ?>" />
<input type="hidden" name="lmachines" value="<?php echo base64_encode(serialize($machines)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
<input type="hidden" name="lsmembers" value="<?php echo base64_encode(serialize($listOfMembers)); ?>" />
<input type="hidden" name="willBeUnregistered" value="<?php echo base64_encode(serialize($willBeUnregistered)); ?>" />
<input type="hidden" name="computersgroupedit" value="<?php echo $computersgroupedit; ?>" />
<input type="hidden" name="id" value="<?php echo  $gid ?>" />
<input type="submit" name="bconfirm" class="btnPrimary" value="<?php echo  _("Confirm"); ?>" />
<input type="submit" name="breset" class="btnSecondary" value="<?php echo  _("Cancel"); ?>" />
</form>

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
}
?>

