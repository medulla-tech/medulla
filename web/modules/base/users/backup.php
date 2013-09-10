<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
/* FIXME: this page needs to be cleaned up */

function sched_backup($user, $media) {
    $param = array($user, $media, $_SESSION["login"]);
    return xmlCall("base.backupUser", $param);
}

if (isset($_POST["bback"])) {
    header("Location: main.php?module=base&submod=users&action=index");
    exit;
}
?>

<h2><?php echo _("Backup a user's folder") ?></h2>

<?php
if (isset($_GET["user"])) {
    $user = urldecode($_GET["user"]);
}
if (isset($_POST["user"])) {
    $user = $_POST["user"];
}

if (isset($_POST["bgo"])) {
    $backuppath = sched_backup($user, $_POST["media"]);

    if (!isXMLRPCError()) {
        $str = "<h2>" . _("Backup a user's home directory") . "</h2>";
        $str .= "<p>";
        $str .= sprintf(_("Backup of <b>%s</b> user's folder has been launched in background."), $user);
        $str .= "</p><p>";
        $str .= sprintf(_("The files will be stored in the directory %s of the server at the end of the backup."), $backuppath);
        $str .= "</p><p>";
        $str .= _("Please go to the status page to check the backup status.");
        $str .= "</p><p>";
        $str .= _("This operation will last according to the amount of data to backup.");
        $str .= "</p>";

        new NotifyWidgetSuccess($str);
    }

    header("Location: " . urlStrRedirect("base/users/index"));
    exit;
} else {
    ?>

    <form action="main.php?module=base&submod=users&action=backup" method="post">
        <p>
            <?php
            printf(_("%s home directory will be archived."), $user);
            ?>
        </p>
        <p>
            <?php
            printf(_("Please select media size. If your data exceeds the volume size, several files of your media size will be created."));
            ?>
        </p>

        <?php echo _("Media size"); ?>
        <select name="media" />
        <option value="600">CD (650 Mo)</option>
        <option value="4200">DVD (4.7 Go)</option>
    </select>
    <br><br>
    <input name="user" type="hidden" value="<?php echo $user; ?>" />
    <input name="bgo" type="submit" class="btnPrimary" value="<?php echo _("Launch backup"); ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo _("Cancel"); ?>" onclick="closePopup();
            return false;" />
    </form>
    <?php
}
?>
