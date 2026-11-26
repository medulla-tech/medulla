<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require_once("modules/base/includes/computers.inc.php");
require_once("modules/xmppmaster/includes/functions.php");

if ($_GET['type'] !== 0) $grouptype = ""; else $grouptype = "("._T("Imaging", "xmppmaster").")";
$id  = $_GET['id'];
$gid = $_GET['gid'];
$groupname = htmlspecialchars($_GET['groupname'] ?? '');

$list = getRestrictedComputersList(0, -1, array('gid' => $_GET['gid']), False);
$count = getRestrictedComputersListLen(array('gid' => $_GET['gid']));
$nbr_presense = 0;
foreach($list as $key => $value) {
    if (xmlrpc_getPresenceuuid($key) != 0) {
        $nbr_presense++;
    }
}
$nbr_absent = $count - $nbr_presense;
?>

<div class="quick-actions-popup">
    <h1><?php echo _T("Quick Actions group", "xmppmaster"); ?></h1>

    <!-- Group info bar -->
    <div class="machine-info">
        <div class="info-item">
            <span class="info-label"><?php echo _T("Group", "xmppmaster"); ?> <?php echo $grouptype; ?></span>
            <span class="info-value"><?php echo $groupname; ?></span>
        </div>
        <div class="info-item">
            <span class="info-label"><?php echo _T("Total machines", "xmppmaster"); ?></span>
            <span class="info-value"><?php echo $count; ?></span>
        </div>
        <div class="info-item">
            <span class="info-label"><?php echo _T("Online", "xmppmaster"); ?></span>
            <span class="info-value"><?php echo $nbr_presense; ?> / <?php echo $count; ?></span>
        </div>
        <div class="info-item">
            <span class="info-label"><?php echo _T("Offline", "xmppmaster"); ?></span>
            <span class="info-value"><?php echo $nbr_absent; ?> / <?php echo $count; ?></span>
        </div>
    </div>

    <?php if ($nbr_presense == 0 && $nbr_absent == 0): ?>
        <p><?php echo _T("No machines in this group.", "xmppmaster"); ?></p>
    <?php endif; ?>

    <!-- Actions for online machines -->
    <?php if ($nbr_presense > 0): ?>
    <div class="actions-section" data-title="<?php echo _T("Actions", "xmppmaster"); ?>">
        <div class="actions-grid">
            <div class="action-item" id="shutdown0" title="<?php echo _T("Shutdown all online machines", "xmppmaster"); ?>">
                <img src="img/actions/power.svg" alt="<?php echo _T("Shutdown", "xmppmaster"); ?>">
                <span id="shutdown"><?php echo _T("Shutdown", "xmppmaster"); ?></span>
            </div>
            <div class="action-item" id="reboot0" title="<?php echo _T("Reboot all online machines", "xmppmaster"); ?>">
                <img src="img/actions/restart.svg" alt="<?php echo _T("Reboot", "xmppmaster"); ?>">
                <span id="reboot"><?php echo _T("Reboot", "xmppmaster"); ?></span>
            </div>
            <div class="action-item" id="inventory0" title="<?php echo _T("Run inventory on all online machines", "xmppmaster"); ?>">
                <img src="img/actions/inventory.svg" alt="<?php echo _T("Run inventory", "xmppmaster"); ?>">
                <span id="inventory"><?php echo _T("Run inventory", "xmppmaster"); ?></span>
            </div>
            <div class="action-item" id="vncchangeperms0" title="<?php echo _T("Change VNC settings on all online machines", "xmppmaster"); ?>">
                <img src="img/actions/control.svg" alt="<?php echo _T("Change VNC settings", "xmppmaster"); ?>">
                <span id="vncchangeperms"><?php echo _T("Change VNC settings", "xmppmaster"); ?></span>
                <label class="action-option" onclick="event.stopPropagation();">
                    <input type="checkbox" id="checkboxvncchangeperms" checked> <?php echo _T("Ask user approval", "xmppmaster"); ?>
                </label>
            </div>
            <div class="action-item" id="installkey0" title="<?php echo _T("Install ARS key on all online machines", "xmppmaster"); ?>">
                <img src="img/actions/key.svg" alt="<?php echo _T("Install ARS key", "xmppmaster"); ?>">
                <span id="installkey"><?php echo _T("Install ARS key", "xmppmaster"); ?></span>
            </div>
        </div>
    </div>
    <?php endif; ?>

    <!-- WOL for offline machines -->
    <?php if ($nbr_absent > 0): ?>
    <div class="actions-section" data-title="<?php echo _T("Actions", "xmppmaster"); ?>">
        <div class="actions-grid">
            <div class="action-item" id="wol0" title="<?php echo _T("Wake on LAN for all offline machines", "xmppmaster"); ?>">
                <img src="img/actions/power.svg" alt="<?php echo _T("Wake on LAN", "xmppmaster"); ?>">
                <span id="wol"><?php echo _T("Wake on LAN", "xmppmaster"); ?></span>
                <label class="action-option" onclick="event.stopPropagation();">
                    <input type="checkbox" id="checkboxwol"> <?php echo _T("Imaging", "xmppmaster"); ?>
                </label>
            </div>
        </div>
    </div>
    <?php endif; ?>

    <!-- Custom Command Section -->
    <?php
    $qacomand = array();
    $mm = array();
    $qacomand = xmlrpc_getlistcommandforuserbyos("root");
    ?>

    <div class="custom-command-section">
        <h3><?php echo _T("Custom command", "xmppmaster"); ?></h3>
        <div class="command-row">
            <select id="select">
                <option value="" data-placeholder="1" selected><?php echo htmlspecialchars(_T("Choose a command", "xmppmaster")); ?></option>
                <?php
                foreach($qacomand['command'] as $tabblecommand) {
                    if ($tabblecommand['namecmd'] != "Restart machine agent") {
                        $tabblecommand['customcmd'] = preg_replace('/\r?\n|\r/', ' ', $tabblecommand['customcmd']);
                        $tabblecommand['customcmd'] = trim($tabblecommand['customcmd'], " \t\n\r");
                        echo '<option value="'.htmlspecialchars($tabblecommand['customcmd']).'">'.htmlspecialchars(xmppmaster_qa_label($tabblecommand['namecmd'])).' ('.$tabblecommand['os'].')</option>';
                        $mm[] = '"'.addslashes($tabblecommand['namecmd']).'": {
                            "description" : "'.addslashes($tabblecommand['description']).'",
                            "customcmd" : "'.addslashes($tabblecommand['customcmd']).'",
                            "os" : "'.addslashes($tabblecommand['os']).'",
                            "user" : "'.addslashes($tabblecommand['user']).'"}';
                    }
                }
                ?>
            </select>
            <button id="buttoncmd" class="btn btn-primary" disabled><?php echo _T("Send custom command", "xmppmaster"); ?></button>
        </div>
    </div>
</div>

<!-- Hidden form for custom command -->
<form name="formcmdcustom" id="formcmdcustom" action="main.php" method="GET" style="display:none;">
    <?php foreach ($_GET as $key => $valu): ?>
        <?php if ($key == "mod" || $key == "id" || $key == "type") continue; ?>
        <input type="hidden" name="<?php echo htmlspecialchars($key); ?>" value="<?php echo htmlspecialchars($valu); ?>">
    <?php endforeach; ?>
    <input type="hidden" id="action" name="action" value="ActionQuickGroup">
    <input type="hidden" id="namecmd" name="namecmd" value="">
    <input type="hidden" id="namecmdos" name="namecmdos" value="">
    <input type="hidden" id="user" name="user" value="root">
    <input type="hidden" id="cmdid" name="cmdid" value="">
</form>

<script type="text/javascript">
var groupinfo = <?php echo json_encode($_GET); ?>;
groupinfo.auth_token = <?php echo json_encode($_SESSION['auth_token'] ?? ''); ?>;

function qaSelectedOption() {
    var opt = jQuery('#select option:selected');
    if (!opt.length || opt.is('[data-placeholder]')) {
        return null;
    }
    return opt;
}

function qaSyncCommand() {
    var opt = qaSelectedOption();
    jQuery('#namecmd').val(opt ? opt.val() : '');
    jQuery('#namecmdos').val(opt ? opt.text() : '');
    jQuery('#buttoncmd').prop('disabled', !opt);
    return opt;
}

jQuery(qaSyncCommand);

jQuery('#select').on('change', qaSyncCommand);

jQuery('#buttoncmd').click(function() {
    if (!qaSyncCommand()) {
        return;
    }
    groupinfo["namecmd"] = jQuery('#namecmd').val();
    groupinfo["namecmdos"] = jQuery('#namecmdos').val();
    groupinfo["user"] = jQuery('#user').val();
    groupinfo["actionqa"] = jQuery('#action').val();
    groupinfo["groupname"] = jQuery('#groupname').val();
    groupinfo["type"] = jQuery('#type').val();
    jQuery.post("modules/xmppmaster/xmppmaster/actioncustomquickactiongrp.php", groupinfo)
        .done(function(data) {
            jQuery('#cmdid').val(data);
            jQuery('#formcmdcustom').submit();
        });
});

jQuery('#checkboxshutdown').click(function() {
    jQuery('#shutdowninfo').toggle();
});

function wol(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_not_present.length == 0) {
        alert(<?php echo json_encode(_T("All machines are running", "xmppmaster")); ?>);
    } else {
        text = "";
        for (var i = 0; i < machine_not_present.length; i++) {
            text = text + machine_not_present[i] + ", ";
        }
        alert(<?php echo json_encode(_T("Wakeonlan on the following machines in progress", "xmppmaster")); ?> + "\n" + text, "", "alert-info");
    }
}

function inventory(data) {
    var uuid = data.result[0];
    var cn = data.result[1];
    var presence = data.result[2];
    var machine_already_present = data.result[3];
    var machine_not_present = data.result[4];

    if (data.notif && data.notif.strings && data.notif.strings[0]) {
        jQuery('#notif').html(data.notif.strings[0]);
        const redirectUrl = window.location.href;
        window.location.href = redirectUrl;
    }
}

function reboot(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_already_present.length == 0) {
        alert(<?php echo json_encode(_T("No machines are running\nReboot possible only on running machine", "xmppmaster")); ?>);
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_not_present[i] + ", ";
        }
        alert(<?php echo json_encode(_T("Reboot on the following machines in progress", "xmppmaster")); ?> + "\n" + text, "", "alert-info");
    }
}

function shutdownfunction(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_already_present.length == 0) {
        alert(<?php echo json_encode(_T("All machines are off\nShutdown possible only on running machines", "xmppmaster")); ?>);
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_already_present[i] + ", ";
        }
        alert(<?php echo json_encode(_T("shutdown on the following machines in progress", "xmppmaster")); ?> + "\n" + text, "", "alert-info");
    }
}

function vncchangepermsfunction(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_already_present.length == 0) {
        alert(<?php echo json_encode(_T("All machines are off\nVNC settings change available only on running machines", "xmppmaster")); ?>);
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_already_present[i] + ", ";
        }
        alert(<?php echo json_encode(_T("VNC settings change on the following machines in progress", "xmppmaster")); ?> + "\n" + text, "", "alert-info");
    }
}

function installkey(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_already_present.length == 0) {
        alert(<?php echo json_encode(_T("No machines are running\nARS key installation possible only on running machine", "xmppmaster")); ?>);
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_already_present[i] + ", ";
        }
        alert(<?php echo json_encode(_T("ARS key installation on the following machines in progress", "xmppmaster")); ?> + "\n" + text, "", "alert-info");
    }
}

jQuery('#wol,#wol0').unbind().on('click', function() {
    groupinfo['wol'] = jQuery('#checkboxwol').is(':checked');
    jQuery.post("modules/xmppmaster/xmppmaster/actionwakeonlan.php", groupinfo)
        .done(function(data) {
            wol(data);
        });
});

jQuery('#inventory,#inventory0').on('click', function() {
    jQuery.post("modules/xmppmaster/xmppmaster/actioninventory.php", groupinfo)
        .done(function(data) {
            inventory(data);
        });
});

jQuery('#reboot,#reboot0').on('click', function() {
    jQuery.post("modules/xmppmaster/xmppmaster/actionrestart.php", groupinfo)
        .done(function(data) {
            reboot(data);
        });
});

jQuery('#installkey,#installkey0').on('click', function() {
    jQuery.post("modules/xmppmaster/xmppmaster/actionkeyinstall.php", groupinfo)
        .done(function(data) {
            installkey(data);
        });
});

jQuery('#shutdown,#shutdown0').on('click', function() {
    groupinfo['time'] = jQuery('#mytimeshutdown').val();
    groupinfo['msg'] = jQuery('#msgshutdown').val();
    jQuery.post("modules/xmppmaster/xmppmaster/actionshutdown.php", groupinfo)
        .done(function(data) {
            shutdownfunction(data);
        });
});

jQuery('#vncchangeperms,#vncchangeperms0').on('click', function() {
    if (jQuery('#checkboxvncchangeperms').is(":checked")) {
        groupinfo['askpermission'] = 1;
    } else {
        groupinfo['askpermission'] = 0;
    }
    jQuery.post("modules/xmppmaster/xmppmaster/actionvncchangeperms.php", groupinfo)
        .done(function(data) {
            vncchangepermsfunction(data);
        });
});
</script>
