<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: members.php 273 2007-11-23 15:25:32Z cedric $
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

$name = quickGet('name');
$id = quickGet('id');
$visibility = quickGet('visible');

if ($id) {
    $group = new Group($id, true);
    if (!$name) { $name = $group->getName(); }
    if (!$visibility) { $visibility = $group->canShow(); }
} else {
    $group = new Group();
}

$members = unserialize(base64_decode($_POST["lmembers"]));
$machines = unserialize(base64_decode($_POST["lmachines"]));
$listOfMembers = unserialize(base64_decode($_POST["lsmembers"]));

if (isset($_POST["bdelmachine_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            $ma = preg_split("/##/", $member);
            unset($members[$member]);
            unset($listOfMembers[$ma[1]]);
        }
    }
} else if (isset($_POST["baddmachine_x"])) {
    if (isset($_POST["machines"])) {
        foreach ($_POST["machines"] as $machine) {
            $ma = preg_split("/##/", $machine);
            $members[$machine] = $ma[0];
            $listOfMembers[$ma[1]] = array('hostname'=>$ma[0], 'uuid'=>$ma[1]);
        }
    }
} else if (isset($_POST["bconfirm"])) {
    $listOfCurMembers = $group->members();
    $curmem = array();
    foreach ($listOfCurMembers as $member) {
        $curmem[$member['hostname']."##".$member['uuid']] = $member['hostname'];
    }

    if (!$curmem) { $curmem = array(); }
    if (!$listOfCurMembers) { $listOfCurMembers = array(); }

    $listN = array();
    $listC = array();
    foreach ($listOfMembers as $member) { $listN[$member['uuid']] = $member; }
    foreach ($listOfCurMembers as $member) { $listC[$member['uuid']] = $member; }

    $newmem = array_diff_assoc($listN, $listC);
    $delmem = array_diff_assoc($listC, $listN);

    if ($group->id) {
        $group->setName($name);
        if ($visibility == 'show') { $group->show(); } else { $group->hide(); }
    } else {
        $group->create($name, ($visibility == 'show'));
    }
    
    $res = $group->addMembers($newmem) && $group->delMembers($delmem);

    if ($res) { //group->save($name)) {
        new NotifyWidgetSuccess(_T("Group successfully modified", "dyngroup"));
        $list = $group->members();
        $members = array();
        foreach ($list as $member) {
            $listOfMembers[$member['uuid']] = $member['hostname'];
            $members[$member['hostname']."##".$member['uuid']] = $member['hostname'];
        }
    } else {
        new NotifyWidgetFailure(_T("Group failed to modify", "dyngroup"));
    }
} else {
    $list = $group->members();
    $members = array();
    foreach ($list as $member) {
        $members[$member['hostname']."##".$member['uuid']] = $member['hostname'];
        $listOfMembers[$member['uuid']] = $member;
    }
    
    if (!$members) { $members = array(); }
    if (!$listOfMembers) { $listOfMembers = array(); }

    $truncate_limit = 2000;
    $listOfMachines = getRestrictedComputersList(0, $truncate_limit, null, False);
    $count = getRestrictedComputersListLen();
    if ($truncate_limit < $count) {
        new NotifyWidgetWarning(sprintf(_T("Machine list has been truncated at %d machines", "dyngroup"), $truncate_limit));
    }
    $machines = array();
    foreach ($listOfMachines as $machine) {
        $machines[$machine[1]['cn'][0]."##".$machine[1]['objectUUID'][0]] = $machine[1]['cn'][0];
    }
}
ksort($members);
reset($members);
ksort($machines);

$diff = array_diff_assoc($machines, $members);
natcasesort($diff);

?>

<form action="<? echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<table style="border: none;" cellspacing="0">
<tr><td><?= _T('Group name', 'dyngroup') ?></td><td></td><td><input name='name' value='<?= $name ?>' type='text'/></td></tr>
<tr><td><?= _T('Is the group visible', 'dyngroup') ?></td><td></td><td>
    <input name='visible' value='show' <? if ($visibility == 'show') { echo 'checked'; }?> type='radio'/><?= _T('Yes', 'dyngroup') ?>, 
    <input name='visible' value='hide' <? if ($visibility != 'show') { echo 'checked'; }?> type='radio'/><?= _T('No', 'dyngroup') ?>
</td></tr>
<!-- add all group inupts -->
</table>

<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr><td style="border: none;">
  <div class="list">
        <h3><?= _T("All machines", "dyngroup");?></h3>
    <select multiple size="15" class="list" name="machines[]">
<?php
foreach ($diff as $idx => $machine) {
    if ($machine == "") {
        unset($machines[$idx]);
        continue;
    }
    echo "<option value=\"".$idx."\">".$machine."</option>\n";
}
?>
    </select>

    <br>

  </div>
  </td><td style="border: none;">
  <div>
  <input type="image" name="bdelmachine" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" /><br/>
  <input type="image" name="baddmachine" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/>
  </div>
  </td><td style="border: none;">

  <div class="list" style="padding-left: 10px;">
      <h3><?= _T("Group members"); ?></h3>
    <select multiple size="15" class="list" name="members[]">
<?php
foreach ($members as $idx => $member) {
    if ($member == "") {
        unset($members[$idx]);
        continue;
    }

    echo "<option value=\"".$idx."\">".$member."</option>\n";
}
?>
    </select>

    <br>

  </div>
  <div class="clearer"></div>
  </td></tr>
</table>
</div>

<input type="hidden" name="lmachines" value="<?php echo base64_encode(serialize($machines)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
<input type="hidden" name="lsmembers" value="<?php echo base64_encode(serialize($listOfMembers)); ?>" />
<input type="hidden" name="id" value="<?php echo $group->id; ?>" />
<!-- input type="hidden" name="name" value="< ?php echo $group->getName(); ?>" /-->
<input type="submit" name="bconfirm" class="btnPrimary" value="<?= _("Confirm"); ?>" />
<input type="submit" name="breset" class="btnSecondary" value="<?= _("Cancel"); ?>" />
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


