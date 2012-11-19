<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

require_once("modules/pkgs/includes/functions.php");

if (isset($_SESSION['random_dir'])) {
    $upload_tmp_dir = sys_get_temp_dir();
    delete_directory($upload_tmp_dir . '/' . $_SESSION['random_dir']);
}

$m = new MultiFileTpl('filepackage');
_T("Click here to select files", "pkgs");
_T("Upload Queued Files", "pkgs");
$m->display();
?>
<script type="text/javascript">
    var sexyArray = new Array('label', 'version', 'description', 'commandcmd');
    for (var dummy in sexyArray) {
        try {
            $(sexyArray[dummy]).setStyle("background: #FFF;");
            $(sexyArray[dummy]).enable();
        }
        catch (err){
            // this php file is prototype ajax request with evalscript
            // enabled.
        }
    }
</script>
