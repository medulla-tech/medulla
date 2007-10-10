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
    $filename = $_POST["filename"];
    $size = $_POST["media"] + 0;
    
    # FIXME: should do some check on $newname (not empty, no bad chars, ...)
    
    $ret = createIsoFromImage($name, $filename, $size);
    if (isXMLRPCError()) {
        new NotifyWidgetFailure(_T("The ISO image creation has failed"));
    } else {
        $str .=  '
        <p>';
        $str.=sprintf(_("CD creation is launched in background"),$user);
        $str.="</p>
        <p>";
        $str.=sprintf(_("The ISO files will be stored as"));
        $str.=" <b>$filename-??.iso</b> ";
        $str.=sprintf(_("file on share « iso » at the end of the process"));
        $str.="</p>
        <p>";
        $str.=_("Operation duration depend of the amount of data");
        $str.="</p>";

        $n = new NotifyWidgetSuccess(_T("The ISO image creation is being done"));
        $n->add($str);
    }    
    header("Location: main.php?module=imaging&submod=publicimages&action=index");
} else {
    $name = urldecode($_GET["name"]);
}

$infos = getPublicImageInfos($name);

printf(_T("<H2>Autobootable deployment CD</H2>"));

?>

<form action="main.php?module=imaging&submod=publicimages&action=mkiso" method="post">
<input type="hidden" name="name" value="<? echo $name; ?>" />

<p>
<? echo _T("Please input file name (without « .iso »):"); ?>
</p>
<input type="text" name="filename" class="textfield" value="<? echo sprintf("%s", $infos['title']); ?>"
<br/><br/>

<p>
<? echo _T("Please select media size. If your data exceeds the volume size, several files of your media size will be created."); ?>
</p>
<select name="media" />
<option value="<? echo 640*1024*1024; ?>"><?= sprintf(_T("CD 74 mins")) ?></option>
<option value="<? echo 700*1024*1024; ?>"><?= sprintf(_T("CD 80 mins")) ?></option>
<option value="<? echo 4.2*1024*1024*1024; ?>"><?= sprintf(_T("DVD SL (4.2 Go)")) ?></option>
<option value="<? echo 8.4*1024*1024*1024; ?>"><?= sprintf(_T("DVD DL (8.4 Go)")) ?></option>
</select>
<br/><br/>
<input type="submit" name="bconfirm" class="btnPrimary" value="<?= _T("Create ISO File"); ?>" />
<input type="submit" name="bback" class="btnSecondary" value="<?= _("Cancel"); ?>" onClick="new Effect.Fade('popup'); return false;" />
</form>
