<?php

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
function formatFileSize($size) {
    $size = intval($size);
    if (floor($size / pow(1024, 3)) > 0)
        return sprintf("%2.2f " . _T('GB', 'backuppc'), $size / pow(1024, 3));
    else if (floor($size / pow(1024, 2)) > 0)
        return sprintf("%2.2f " . _T('MB', 'backuppc'), $size / pow(1024, 2));
    else if (floor($size / 1024) > 0)
        return sprintf("%2.2f " . _T('KB', 'backuppc'), $size / 1024);
    else
        return sprintf("%d " . _T('Bytes', 'backuppc'), $size);
}

require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/msc/includes/utilities.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];


if (isset($_GET['filter'])) {
    $prm = explode('|mDvPulse|', $_GET['filter']);
    if (count($prm) == 2)
        list($_GET['folder'], $_GET['location']) = $prm;
    else
        list($_GET['folder'], $_GET['location']) = array('/', $_GET['filter']);
}

if (!isset($_GET['location']))
    $_GET['location'] = '';

if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

if (isset($_GET['host'], $_GET['sharename'], $_GET['backupnum'], $_GET['filename'], $_GET['minsize'], $_GET['maxsize'])) {

    if ($_GET['sharename'] == '-1')
        $_GET['sharename'] = array();
    if ($_GET['backupnum'] == '-1')
        $_GET['backupnum'] = array();

    //$folder = (isset($_GET['folder']) && trim($_GET['folder'])!='//')?$_GET['folder']:'/';
    $response = file_search($_GET['host'], $_GET['backupnum'], $_GET['sharename'], $_GET['filename'], $_GET['minsize'], $_GET['maxsize'], ' ');

    // Check if error occured
    if ($response['err']) {
        new NotifyWidgetFailure(nl2br($response['errtext']));
        return;
    }

    $data = $response['data'];

    $names = array();
    $paths = array();
    $types = array();
    $sizes = array();
    $bknums = array();
    $shares = array();
    $cssClasses = array();

    $i = 0;
    $params = array();
    foreach ($data as $entry) {

        $param = array('host' => $_GET['host'], 'backupnum' => $entry['backupnum'], 'sharename' => $entry['sharename'], 'dir' => $entry['filepath']);
        if ($entry['type'] == 'd') {

            $sizes[] = '';
            $name = '<a href="#" onclick="BrowseDir(\'' . $entry['filepath'] . '\')">' . $entry['filename'] . "</a>";
            $cssClasses[] = 'folder';
            $params['isdir'] = '1';
            //$viewVersionsActions[] = $emptyAction;
        } else {
            $sizes[] = formatFileSize($entry['filesize']);

            $param_str = "host=" . $_GET['host'] . "&backupnum=" . $entry['backupnum'] . "&sharename=" . urlencode($entry['sharename']);
            $param_str.= "&dir=" . urlencode($entry['filepath']);
            $name = '<a href="#" onclick="RestoreFile(\'' . $param_str . '\')">' . $entry['filename'] . "</a>";
            $cssClasses[$i] = 'file';

            //$viewVersionsActions[] = $viewVersionsAction;
        }
        $i++;
        $names[] = $name;
        $params[] = $param;
    }

    $count = count($data);

    $n = new OptimizedListInfos($names, _T('File', 'backuppc'));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($sizes, _T("Size", "backuppc"));
    $n->setMainActionClasses($cssClasses);
    $n->setItemCount($count);
    $filter = $_GET['folder'] . '|mDvPulse|' . $_GET['location'];
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->start = isset($_GET['start']) ? $_GET['start'] : 0;
    $n->end = isset($_GET['end']) ? $_GET['end'] : $maxperpage;
    $n->setParamInfo($params); // Setting url params

    $n->display();
}
?>

<script type="text/javascript">
    jQuery(function() {
        jQuery('input#btnRestoreZip').click(function() {
            form = jQuery('#restorefiles').serialize();

            // Test if no checkbox is checked
            if (jQuery('input[type=checkbox]:checked').length == 0)
            {
                alert('You must select at least on file.');
                return;
            }

            jQuery.ajax({
                type: "POST",
                url: "<?php echo 'main.php?module=backuppc&submod=backuppc&action=restoreZip'; ?>",
                data: form,
                success: function(data) {
                    jQuery('html').append(data);
                    setTimeout("refresh();", 3000);
                }
            });
            return false;

        });
    });

</script>
