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
require_once("modules/backuppc/includes/xmlrpc.php");

$computer_name = $_GET['cn'];
$uuid = $_GET['objectUUID'];

// ==========================================================
// Receiving POST data for user actions
// ==========================================================

if (isset($_POST['startFullBackup'])) {
    $response = start_full_backup($_POST['host']);
    sleep(2);
} elseif (isset($_POST['startIncrBackup'])) {
    $response = start_incr_backup($_POST['host']);
    sleep(2);
} elseif (isset($_POST['stopBackup'])) {
    $response = stop_backup($_POST['host']);
    sleep(2);
}

// Check if error occured
if (isset($response)) {
    if (isXMLRPCError() || $response['err']) {
        new NotifyWidgetFailure(nl2br($response['errtext']));
    } else {
        new NotifyWidgetSuccess(_T('Action requested successfully', 'backuppc'));
    }
}
// ==========================================================
// Test if UUID is set on BackupPC Hosts DB
// ==========================================================

if (get_backupserver_for_computer($uuid) != '') {
    if (!host_exists($uuid)) {
        printf(_T("Backup is not set for this computer.", 'backuppc'));
        // Propose to set
        $f = new PopupForm("");
        $hidden = new HiddenTpl("host");
        $f->add($hidden, array("value" => $uuid, "hide" => True));
        $f->addButton("setBackup", _T("Configure", 'backuppc'));
        $f->display();
        return;
    }
} else {
    printf(_T("There is no backup server assigned for the computer entity.", 'backuppc'));
    return;
}

$response = get_host_status($uuid);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

// ==========================================================
// Status lines
// ==========================================================
$status_strings = array(
    'no ping' => '<span style="color:red">' . _T('No ping response', 'backuppc') . '</span>',
    'backup failed' => '<span style="color:red">' . _T('Backup failed', 'backuppc') . '</span>',
    'restore failed' => '<span style="color:red">' . _T('Restore failed', 'backuppc') . '</span>',
    'backup_done' => '<span style="color:green">' . _T('Backup up to date', 'backuppc') . '</span>',
    'restore done' => '<span style="color:green">' . _T('Restore done', 'backuppc') . '</span>',
    'nothing' => '<span style="color:red">' . _T('This computer has never been backed up', 'backuppc') . '</span>',
    'idle' => '<span style="color:black">' . _T('Idle', 'backuppc') . '</span>',
    'canceled' => '<span style="color:black">' . _T('Cancelled by user', 'backuppc') . '</span>',
    'in progress' => '<img src="modules/msc/graph/images/status/inprogress.gif" width="14" alt="" /> <span style="color:orange">' . _T('Backup in progress') . '</span>'
);

print '<table><tr><td width="130" valign="top">' . _T('Current state: ', 'backuppc') . '</td><td><b id="statustext">';
foreach ($response['status'] as $line)
    print $status_strings[$line] . '<br/>';
if ($line == 'nothing')
    $nerverbackuped = 1;
print "</b></td></tr></table>";


// ==========================================================
// User actions Form
// ==========================================================

$f = new PopupForm("");
$hidden = new HiddenTpl("host");
$f->add($hidden, array("value" => $uuid, "hide" => True));
$f->addButton("startFullBackup", _T("Start Full Backup", 'backuppc'));
if (!isset($nerverbackuped))
    $f->addButton("startIncrBackup", _T("Sart Incr Backup", 'backuppc'));
$f->addButton("stopBackup", _T("Stop Backup", 'backuppc'));
$f->display();


// ==========================================================
// Backup status table
// ==========================================================

if ($response['data']) {

    $backup_nums = $response['data']['backup_nums'];
    $types = $response['data']['type'];
    $ages = $response['data']['ages'];
    $start_dates = $response['data']['start_dates'];
    $durations = $response['data']['durations'];
    $xfer_errs = $response['data']['xfer_errs'];
    $total_file_count = $response['data']['total_file_count'];
    $total_file_size = $response['data']['total_file_size'];
    $new_file_count = $response['data']['new_file_count'];
    $new_file_size = $response['data']['new_file_size'];

    $count = count($backup_nums);

    $params = array();
    $times = array();
    for ($i = 0; $i < $count; $i++) {
        $params[] = array('host' => $uuid, 'backupnum' => $backup_nums[$i], 'cn' => $_GET['cn']);
        preg_match("#.+ (.+)#", $start_dates[$i], $result);
        $time = time() - floatval($ages[$i]) * 24 * 60 * 60;
        $times[] = strftime(_T("%A, %B %e %Y"), $time) . ' - ' . $result[1];
        $durations[$i] = max(1, intval($durations[$i]));
        $total_file_count[$i] .= ' (' . $new_file_count[$i] . ')';
        $total_file_size[$i] = intval($total_file_size[$i]) . ' (' . intval($new_file_size[$i]) . ')';
        $types[$i] = _T($types[$i], 'backuppc');
    }

    $n = new OptimizedListInfos($times, _T("Backup time", "backuppc"));
    $n->addExtraInfo($types, _T("Type", "backuppc"));
    $n->addExtraInfo($durations, _T("Duration (min.)", "backuppc"));
    $n->addExtraInfo($xfer_errs, _T("Errors", "backuppc"));
    $n->addExtraInfo($total_file_count, _T("File count (new)", "backuppc"));
    $n->addExtraInfo($total_file_size, _T("Backup size (new) [Mb]", "backuppc"));
    $n->setCssClass("file"); // CSS for icons
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter1));
    $n->start = 0;
    $n->end = 50;

    $n->setParamInfo($params); // Setting url params
    $n->addActionItem(new ActionItem(_T("Browse", "backuppc"), "BrowseShareNames", "display", "host", "backuppc", "backuppc"));
    $n->addActionItem(new ActionPopupItem(_T("View errors"), "viewXferLog", "file", "dir", "backuppc", "backuppc"));

    print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

    $n->display();
}
?>

<script type="text/javascript">

        function refresh_status() {
                jQuery.get(
                "<?php echo 'main.php?module=backuppc&submod=backuppc&action=ajaxGetStatus&q=GET_STATUS&host=' . $_GET['objectUUID']; ?>",
                    function(data) {
                    jQuery('#statustext').html(data);
                setTimeout('refresh_status();', 3000);
    });
    }

    setTimeout('refresh_status();', 3000);
</script>
<style>
    body { min-width: 520px; }
    .column { width: 170px; float: left; padding-bottom: 100px; }
    .portlet { margin: 0 1em 1em 0; }
    .portlet-header { margin: 0.3em; padding-bottom: 4px; padding-left: 0.2em; }
    .portlet-header .ui-icon { float: right; }
    .portlet-content { padding: 0.4em; }
    .ui-sortable-placeholder { border: 1px dotted black; visibility: visible !important; height: 50px !important; }
    .ui-sortable-placeholder * { visibility: hidden; }
</style>

<script>
    // function that writes the list order to a cookie
        function saveOrder() {
            jQuery(".column").each(function(index, value) {
            var colid = value.id;
            var cookieName = "cookie-" + colid;
            // Get the order for this column.
            var order = jQuery('#' + colid).sortable("toArray");
            // For each portlet in the column
                for (var i = 0, n = order.length; i < n; i++) {
                // Determine if it is 'opened' or 'closed'
                var v = jQuery('#' + order[i]).find('.portlet-content').is(':visible');
                // Modify the array we're saving to indicate what's open and
                //  what's not.
            order[i] = order[i] + ":" + v;
            }
        jQuery.cookie(cookieName, order, {path: "/", expiry: new Date(2012, 1, 1)});
    });
    }

    // function that restores the list order from a cookie
        function restoreOrder() {
            jQuery(".column").each(function(index, value) {
            var colid = value.id;
            var cookieName = "cookie-" + colid
            var cookie = jQuery.cookie(cookieName);
                if (cookie == null) {
            return;
            }
            var IDs = cookie.split(",");
                for (var i = 0, n = IDs.length; i < n; i++) {
                var toks = IDs[i].split(":");
                    if (toks.length != 2) {
                continue;
                }
                var portletID = toks[0];
                var visible = toks[1]
                        var portlet = jQuery(".column")
                        .find('#' + portletID)
                .appendTo(jQuery('#' + colid));
                    if (visible === 'false') {
                    portlet.find(".ui-icon").toggleClass("ui-icon-minus");
                    portlet.find(".ui-icon").toggleClass("ui-icon-plus");
                portlet.find(".portlet-content").hide();
            }
        }
    });
    }


        jQuery(document).ready(function() {
            jQuery(".column").sortable({
            connectWith: ['.column'],
                stop: function() {
            saveOrder();
        }
        });

                jQuery(".portlet")
                .addClass("ui-widget ui-widget-content")
                .addClass("ui-helper-clearfix ui-corner-all")
                .find(".portlet-header")
                .addClass("ui-widget-header ui-corner-all")
                .prepend('<span class="ui-icon ui-icon-minus"></span>')
                .end()
        .find(".portlet-content");

        restoreOrder();

            jQuery(".portlet-header .ui-icon").click(function() {
            jQuery(this).toggleClass("ui-icon-minus");
            jQuery(this).toggleClass("ui-icon-plus");
            jQuery(this).parents(".portlet:first").find(".portlet-content").toggle();
        saveOrder(); // This is important
        });
                jQuery(".portlet-header .ui-icon").hover(
                    function() {
                jQuery(this).addClass("ui-icon-hover");
                },
                    function() {
                jQuery(this).removeClass('ui-icon-hover');
        }
    );
    });
</script>
