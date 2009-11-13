<?

/*
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

include('modules/imaging/includes/includes.php');
$params = getParams();
$id = $_GET['itemid'];
$label = urldecode($_GET['itemlabel']);

if(isset($_GET['gid'])) 
    $type = 'group';
else
    $type = '';

if (quickGet('valid')) {
    // remove from bootmenu
    // ...
    $params['mod'] = 'remove_success';
    header("Location: " . urlStrRedirect("base/computers/imgtabs", $params));
}

// show popup
$params['id'] = $id;
$params['mod'] = 'remove';
?>
<h2><?= _T("Remove from boot menu", "imaging") ?></h2>

<form action="<?=urlStr("base/computers/bootmenu_remove",$params)?>" method="post">
    <p><? printf(_T("Are you sure you want to remove <b>%s</b> from the boot menu ?", "imaging"), $label); ?></p>
    <input name='valid' type="submit" class="btnPrimary" value="<?= _T("Remove", "imaging"); ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?= _T("Cancel", "imaging"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>
