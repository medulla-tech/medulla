<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

require('modules/msc/includes/scheduler_xmlrpc.php');

if (isset($_POST["bconfirm"])) {
    $ret = scheduler_download_file('', $_GET['objectUUID']);
    if ($ret === False) {
        new NotifyWidgetFailure(_T("The download has failed.", "msc"));
        header("Location: " . urlStrRedirect("base/computers/index"));
    } else {
        $filename = $ret[0];
        ob_end_clean();
        header("Content-type: application/octet-stream");
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        print $ret[1]->scalar;
    }
} else {
    $f = new PopupForm(_T("Download a file from a computer", "msc"));
    $f->addText(sprintf(_T("Warning: this operation may last a long time.", "msc")));
    $f->addValidateButtonWithFade("bconfirm");
    $f->addCancelButton("bback");
    $f->display();    
}
?>
