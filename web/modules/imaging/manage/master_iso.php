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
include('modules/imaging/includes/xmlrpc.inc.php');

$id = $_GET['itemid'];
$label = urldecode($_GET['itemlabel']);
$params = getParams();

if ($_POST) {
    $isopath = "/tmp";
    $label = $_POST['label'];
    $title = $_POST['title'];
    $size = $_POST['media'];
    $image_uuid = $_POST['itemid'];

    $ret = xmlrpc_imagingServerISOCreate($image_uuid, $size, $title);
    // goto images list
    if ($ret[0] and !isXMLRPCError()) {
        $str = "<h2>"._T("Create iso from master", "imaging")."</h2>";
        $str .= "<p>";
        $str .= sprintf(_T("Iso of master <strong>%s</strong> has been launched in background.", "imaging"), $label);
        $str .= "</p><p>";
        $str .= sprintf(_T("The files will be stored in the directory %s of the server at the end of the backup.", "imaging"), $isopath); # TODO get the path
        $str .= "</p><p>";
        $str .= _T("Please go to the status page to check the iso creation status.", "imaging");
        $str .= "</p><p>";
        $str .= _T("This operation will last according to the amount of data of the master.", "imaging");
        $str .= "</p>";

        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/master", $params));
        exit;
    } elseif ($ret[0]) {
        header("Location: " . urlStrRedirect("imaging/manage/master", $params));
        exit;
    } else {
        new NotifyWidgetFailure($ret[1]);
    }
}

?>
<form action="<?php echo urlStr("imaging/manage/master_iso") ?>" method="post">
<h2><?php echo  sprintf(_T("Create iso for <strong>%s</strong>", "imaging"), $label) ?></h2>
<table>
<tr><td><?php echo  _T('Title', 'imaging'); ?></td><td> <input name="title" type="text" value="" /></td></tr>
<tr><td colspan="2">
<p>Please select media size. If your data exceeds the volume size,
several files of your media size will be created.</p>
</td></tr>
<tr><td><?php echo  _T("Media size", "imaging"); ?></td><td>
<select name="media" />
<option value="681574400">CD (650 Mo)</option>
<option value="734003200">CD (700 Mo)</option>
<option value="5046586572">DVD (4.7 Go)</option>
</select>
</td></tr></table>
<br/><br/>
<input name="label" type="hidden" value="<?php echo $label ?>" />
<input name="itemid" type="hidden" value="<?php echo $id; ?>" />
<input name="bgo" type="submit" class="btnPrimary" value="<?php echo  _T("Launch backup", "imaging"); ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?php echo  _("Cancel"); ?>" onclick="new Effect.Fade('popup'); return false;" />
</form>
