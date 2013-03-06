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

require_once("modules/dyngroup/includes/includes.php");

$id = quickGet('gid');
$group = new Group($id, False);
$type = quickGet('type');
if ($type == 1) { // Imaging group
    $stype = "_profiles";
    $ltype = 'profile';
    $title = _T("Delete imaging group", "dyngroup");
    $popup = _T("Are you sure you want to delete imaging group <b>%s</b>?<br/>", "dyngroup");
    $delete = _T("Delete imaging group", "dyngroup");
} else { // Simple group
    $stype = '';
    $ltype = 'group';
    $title = _T("Delete group", "dyngroup");
    $popup = _T("Are you sure you want to delete group <b>%s</b>?<br/> (it can be used in an other group).", "dyngroup");
    $delete = _T("Delete group", "dyngroup");
}

if (quickGet('valid')) {
    $group->delete();
    if ($type == 1) { // Imaging group
        header("Location: " . urlStrRedirect("imaging/manage/list$stype" ));
        new NotifyWidgetSuccess(sprintf(_T("Imaging group %s was successfully deleted", "imaging"), $group->getName()));
    }
    else { // simple group
        header("Location: " . urlStrRedirect("base/computers/list$stype" ));
        new NotifyWidgetSuccess(sprintf(_T("Group %s was successfully deleted", "imaging"), $group->getName()));
    }
    exit;
}

?>

<h2><?php echo  $title ?></h2>

<form action="<?php echo  urlStr("base/computers/delete_group", array('gid'=>$id, 'type'=>$type)) ?>" method="post">
<p>

<?php
    printf($popup, $_GET["groupname"]);
?>

</p>
<input name='valid' type="submit" class="btnPrimary" value="<?php echo  $delete ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?php echo  _T("Cancel", "dyngroup"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>
