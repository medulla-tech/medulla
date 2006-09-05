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
?>
<?php
function sched_backup($user, $media) {
    $param = array($user,$media,$_SESSION["login"]);
    return xmlCall("base.backupUser",$param);
}

if (isset($_POST["bback"])) {
    header("Location: main.php?module=base&submod=users&action=index");
    exit;
}
?>

<h2><?= _("Backup a user's folder") ?></h2>

<?php
if (isset($_GET["user"])) {
  $user = urldecode($_GET["user"]);
}
if (isset($_POST["user"])) {
  $user = $_POST["user"];
}

if (isset($_POST["bgo"])) {
  sched_backup($user, $_POST["media"]);
?>

<?php
$str = "<h2>"._("Backup a user's folder")."</h2>";
$str .=  '
<p>';
$str.=sprintf(_("Backup of %s user's folder is launched in background"),$user);
$str.="</p>
<p>";
$str.=sprintf(_("Your files will be stored in"));
$str.=" <b>".$_SESSION["login"]."-".$user."-".date("Y-m-d")."</b> ";
$str.=sprintf(_("file on share %s at the end of the process"),$conf["backup"]["share"]);
$str.="</p>
<p>";
$str.=_("Operation duration depend of the amount of data");
$str.="</p>";

$n = new NotifyWidget();
$n->add($str);

header("Location: ".urlStr("base/users/index"));
?>
<?php
}
else
{
?>

<form action="main.php?module=base&submod=users&action=backup" method="post">
<p>
<?php
    printf(_("%s home directory will be archived."),$user);
?>
</p>
<p>
    <?php
        printf(_("Please select media size. If your data exceeds the volume size, several files of your media size will be created."));
    ?>
</p>

<?= _("Media size"); ?>
<select name="media" />
<option value="600">CD (650 Mo)</option>
<option value="4200">DVD (4.7 Go)</option>
</select>
<br><br>
<input name="user" type="hidden" value="<?php echo $user; ?>" />
<input name="bgo" type="submit" class="btnPrimary" value="<?= _("Launch backup"); ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?= _("Return"); ?>" />
</form>
<?php
}
?>