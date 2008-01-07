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


$name = '';
if ($_POST['id'] || $_GET['id']) {
    if ($_GET['id']) {
        $group = new Stagroup($_GET['id']);
        if ($_POST['name']) { $group->save($_POST['name']); }
        if ($_POST['visible'] == 'show') { $group->show(); } elseif ($_POST['visible'] == 'hide') { $group->hide(); }
        
        $name = $group->getName();
    } elseif ($_POST['id']) {
        $group = new Stagroup($_POST['id']);
        if ($_POST['name']) { $group->save($_POST['name']); }
        if ($_POST['visible'] == 'show') { $group->show(); } elseif ($_POST['visible'] == 'hide') { $group->hide(); }
        $name = $group->getName();
    }
} else {
    $group = new Stagroup(get_next_dyngroup_id());
}

$members = unserialize(base64_decode($_POST["lmembers"]));
$machines = unserialize(base64_decode($_POST["lmachines"]));

if (isset($_POST["bdelmachine_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            $idx = array_search($member, $members);
            if ($idx !== false) unset($members[$idx]);
        }
    }
} else if (isset($_POST["baddmachine_x"])) {
    if (isset($_POST["machines"])) {
        foreach ($_POST["machines"] as $machine) {
            $idx = array_search($machine, $members);
            if ($idx === false) {
                $members[] = $machine;
            }
        }
    }
    sort($members);
    reset($members);
} else if (isset($_POST["bconfirm"])) {
    $curmem = $group->members();
    if (!$curmem) { $curmem = array(); }
    $newmem = array_diff($members, $curmem);
    $delmem = array_diff($curmem, $members);

    $group->addMembers($newmem);
    $group->delMembers($delmem);

    /*if ($group->save($name)) {
        new NotifyWidgetSuccess(_T("Group successfully modified"));
    }*/
    $members = $group->members();
} else {
    $members = $group->members();
    if (!$members) {
        $members = array();
    }
    #$machines = getComputersName();
    $machines = getRestrictedComputersName(0, 10000);
}

$diff = array_diff($machines, $members);

?>

<form action="<? echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<table style="border: none;" cellspacing="0">
<tr><td><?= _T('Group name', 'dyngroup') ?></td><td></td><td><input name='name' value='<?= $group->getName() ?>' type='text'/></td></tr>
<tr><td><?= _T('Is the group visible', 'dyngroup') ?></td><td></td><td>
    <input name='visible' value='show' <? if ($group->canShow()) { echo 'checked'; }?> type='radio'/><?= _T('Yes', 'dyngroup') ?>, 
    <input name='visible' value='hide' <? if (!$group->canShow()) { echo 'checked'; }?> type='radio'/><?= _T('No', 'dyngroup') ?>
</td></tr>
<!-- add all group inupts -->
</table>

<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr><td style="border: none;">
  <div class="list">
        <h3><?= _T("All machines");?></h3>
    <select multiple size="15" class="list" name="machines[]">
<?php
foreach ($diff as $idx => $machine) {
    if ($machine == "") {
        unset($machines[$idx]);
        continue;
    }
    echo "<option value=\"".$machine."\">".$machine."</option>\n";
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

<input type="hidden" name="lmachines" value="<?php echo base64_encode(serialize($machines)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
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


