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

$id = idGet();
$group = new Stagroup($id);
if ($group->isDyn()) {
    $group = $group->toDyn();
}

?> <h2><?php echo  sprintf(_T("%s's details", 'dyngroup'), $group->getName()) ?></h2> <?php

if ($_GET['bregen'] || $_POST['bregen']) {
    $group->reload();
    header("Location: " . urlStrRedirect("base/computers/list" ));
}
if ($_GET['bshow'] || $_POST['bshow']) {
    $group->show();
    header("Location: " . urlStrRedirect("base/computers/list" ));
}
if ($_GET['bhide'] || $_POST['bhide']) {
    $group->hide();
    header("Location: " . urlStrRedirect("base/computers/list" ));
}

//$group->prettyDisplay();

?> <form action="<?php echo  urlStr("base/computers/details", array('id'=>$id)) ?>" method="post"> <?php  
?> <input name="bback" type="submit" class="btnPrimary" value="<?php echo  _T("Close", "dyngroup") ?>" onClick="new Effect.Fade('popup'); return false;"/> <?

if ($group->isDyn() && $group->isGroup()) {
    print '<input name="bregen" type="submit" class="btnSecondary" value="'._T("Regenerate", "dyngroup").'"/>';
}
if ($group->canShow()) {
    print '<input name="bhide" type="submit" class="btnSecondary" value="'._T("Hide", "dyngroup").'"/>';
} else {
    print '<input name="bshow" type="submit" class="btnSecondary" value="'._T("Show", "dyngroup").'"/>';
}

?>

</form>
    




