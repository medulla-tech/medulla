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

$id = $_GET['itemid'];
$label = urldecode($_GET['itemlabel']);

if ($_POST) {
    $isopath = "/tmp";
    $label = $_POST['label'];
    // create iso
    // ...
    $str = "<h2>"._("Create iso from master")."</h2>";
    $str .= "<p>";
    $str .= sprintf(_("Iso of master <strong>%s</strong> has been launched in background."), $label);
    $str .= "</p><p>";
    $str .= sprintf(_("The files will be stored in the directory %s of the server at the end of the backup."), $isopath);
    $str .= "</p><p>";
    $str .= _("Please go to the status page to check the iso creation status.");
    $str .= "</p><p>";
    $str .= _("This operation will last according to the amount of data of the master.");
    $str .= "</p>";

    new NotifyWidgetSuccess($str);
    header("Location: " . urlStrRedirect("imaging/manage/master"));
}

?>
<form action="<?=urlStr("imaging/manage/master_iso")?>" method="post">
<h2><?= sprintf(_T("Create iso for <strong>%s</strong>", "imaging"), $label) ?></h2>
<p>Please select media size. If your data exceeds the volume size, 
several files of your media size will be created.</p>
<?= _("Media size"); ?> : 
<select name="media" />
<option value="600">CD (650 Mo)</option>
<option value="4200">DVD (4.7 Go)</option>
</select>
<br/><br/>
<input name="label" type="hidden" value="<?=$label?>" />
<input name="bgo" type="submit" class="btnPrimary" value="<?= _("Launch backup"); ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?= _("Cancel"); ?>" onclick="new Effect.Fade('popup'); return false;" />
</form>
