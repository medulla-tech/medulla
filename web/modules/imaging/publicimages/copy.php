<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id: delete.php 126 2007-09-10 09:47:40Z cedric $
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

if (isset($_POST["bconfirm"])) {
    $name = $_POST["name"];
    $newname = $_POST["newname"];
    if (dupPublicImage($name, $newname) == False)
        new NotifyWidgetFailure(_T("The image has not been duplicated to $newname, as $newname already exists"));
    elseif (!isXMLRPCError())
        new NotifyWidgetSuccess(_T("The image has been duplicated to $newname."));
    header("Location: main.php?module=imaging&submod=publicimages&action=index");
} else {
    $name = urldecode($_GET["name"]);
}
?>

<p>
<?= sprintf(_T("You will duplicate the image %s"), "<strong>$name</strong>"); ?>
</p>

<form action="main.php?module=imaging&submod=publicimages&action=copy" method="post">
<input type="hidden" name="name" value="<? echo $name; ?>" />
<input type="text" name="newname" value="<? echo sprintf(_("copy of %s"), $name); ?>" />
<input type="submit" name="bconfirm" class="btnPrimary" value="<?= _T("Duplicate Image"); ?>" />
<input type="submit" name="bback" class="btnSecondary" value="<?= _("Cancel"); ?>" onClick="new Effect.Fade('popup'); return false;" />
</form>
