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

$primary = getUserPrimaryGroup($detailArr["uid"][0]);
$secondaries = getUserSecondaryGroups($detailArr["uid"][0]);
sort($secondaries);
?>

   <table>
    <tr>
     <td width="40%" style="text-align:right"><?= _("Primary Group");?></td>
     <td>
      <?= $primary; ?>
    </td>
    </tr>
    <tr><td width="40%" style="text-align:right; vertical-align: top;"><?= _("Groups");?></td><td>
            <?php
            foreach ($secondaries as $group)
                echo $group . "<br>";
            ?>

    </td>
    </tr>
    </table>
