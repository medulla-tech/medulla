<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2011 Mandriva, http://www.mandriva.com
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

if (isset($_POST["bconfirm"])) {
    $ppolicy = $_POST["ppolicy"];
    removePPolicy($ppolicy);
    if (!isXMLRPCError()) {
        $result = _T("The password policy has been deleted.", "ppolicy");
        new NotifyWidgetSuccess($result);
    }
    header("Location: " . urlStrRedirect("base/users/indexppolicy"));
}
else {
    $ppolicy = urldecode($_GET["ppolicy"]);
}

?>

<p><?php echo _T(sprintf("You will delete the password policy <strong>%s</strong>. Default password policy will be applied to users that use this password policy.", $ppolicy), "ppolicy"); ?></p>

<form action="<?php echo urlStrRedirect('base/users/deleteppolicy'); ?>" method="post">
    <input type="hidden" name="ppolicy" value="<?php echo $ppolicy; ?>" />
    <input type="submit" name="bconfirm" class="btnPrimary" value="<?php echo _('Delete'); ?>" />
    <input type="submit" name="bback" class="btnSecondary" value="<?php echo _('Cancel'); ?>" onclick="new Effect.Fade('popup'); return false;" />
</form>
