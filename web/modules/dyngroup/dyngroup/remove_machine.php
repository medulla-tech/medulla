<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require_once("modules/dyngroup/includes/includes.php");

$gid = quickGet('gid');
$group = new Dyngroup($gid);
$machine = quickGet('name');

if (quickGet('valid')) {
    $group->removeMachine($machine);
    header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$gid)));
}

?> <h2><?= _T("Remove a machine") ?></h2> <?php

?>

<form action="<?= urlStr("base/computers/remove_machine", array('gid'=>$gid, 'name'=>$machine)) ?>" method="post">
<p>
<?  
    printf(_T("You will remove machine <b>%s</b> from group <b>%s</b>."), $machine, $group->getName());
?>
</p>
<input name='valid' type="submit" class="btnPrimary" value="<?= _T("Remove Machine"); ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?= _T("Cancel"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>
    




