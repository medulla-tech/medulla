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

if ($_GET['type'] !== 0) $grouptype = ""; else $grouptype = "(Imaging)";
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
    <div class="actions-section">
        <div class="actions-grid">
            <div class="action-item" id="shutdown0" title="<?php echo _T("Shutdown all online machines", "xmppmaster"); ?>">
                <img src="img/actions/power.svg" alt="Shutdown">
                <span id="shutdown"><?php echo _T("Shutdown", "xmppmaster"); ?></span>
                <label class="action-option" onclick="event.stopPropagation();">
                    <input type="checkbox" id="checkboxshutdown"> <?php echo _T("options", "xmppmaster"); ?>
                </label>
            </div>
            <div class="action-item" id="reboot0" title="<?php echo _T("Reboot all online machines", "xmppmaster"); ?>">
                <img src="img/actions/restart.svg" alt="Reboot">
                <span id="reboot"><?php echo _T("Reboot", "xmppmaster"); ?></span>
            </div>
            <div class="action-item" id="inventory0" title="<?php echo _T("Run inventory on all online machines", "xmppmaster"); ?>">
                <img src="img/actions/inventory.svg" alt="Inventory">
                <span id="inventory"><?php echo _T("Run inventory", "xmppmaster"); ?></span>
            </div>
            <div class="action-item" id="vncchangeperms0" title="<?php echo _T("Change VNC settings on all online machines", "xmppmaster"); ?>">
                <img src="img/actions/control.svg" alt="VNC">
                <span id="vncchangeperms"><?php echo _T("Change VNC settings", "xmppmaster"); ?></span>
                <label class="action-option" onclick="event.stopPropagation();">
                    <input type="checkbox" id="checkboxvncchangeperms" checked> <?php echo _T("Ask user approval", "xmppmaster"); ?>
                </label>
            </div>
            <div class="action-item" id="installkey0" title="<?php echo _T("Install ARS key on all online machines", "xmppmaster"); ?>">
                <img src="img/actions/key.svg" alt="Key">
                <span id="installkey"><?php echo _T("Install ARS key", "xmppmaster"); ?></span>
            </div>
        </div>
    </div>
    <?php endif; ?>

    <!-- Shutdown options (hidden by default) -->
    <div id="shutdowninfo" class="shutdown-options" style="display: none;">
        <div class="option-row">
            <label><?php echo _T("Time before shutdown", "xmppmaster"); ?></label>
            <input type="number" id="mytimeshutdown" value="60" min="0" max="120">
        </div>
        <div class="option-row">
            <label><?php echo _T("Message", "xmppmaster"); ?></label>
            <input type="text" id="msgshutdown" value="Shutdown from admin">
        </div>
    </div>

    <!-- WOL for offline machines -->
    <?php if ($nbr_absent > 0): ?>
    <div class="actions-section">
        <div class="actions-grid">
            <div class="action-item" id="wol0" title="<?php echo _T("Wake on LAN for all offline machines", "xmppmaster"); ?>">
                <img src="img/actions/power.svg" alt="WOL">
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
                <?php
                foreach($qacomand['command'] as $tabblecommand) {
                    if ($tabblecommand['namecmd'] != "Restart machine agent") {
                        $tabblecommand['customcmd'] = preg_replace('/\r?\n|\r/', ' ', $tabblecommand['customcmd']);
                        $tabblecommand['customcmd'] = trim($tabblecommand['customcmd'], " \t\n\r");
                        echo '<option value="'.htmlspecialchars($tabblecommand['customcmd']).'">'.htmlspecialchars($tabblecommand['namecmd']).' ('.$tabblecommand['os'].')</option>';
                        $mm[] = '"'.addslashes($tabblecommand['namecmd']).'": {
                            "description" : "'.addslashes($tabblecommand['description']).'",
                            "customcmd" : "'.addslashes($tabblecommand['customcmd']).'",
                            "os" : "'.addslashes($tabblecommand['os']).'",
                            "user" : "'.addslashes($tabblecommand['user']).'"}';
                    }
                }
                ?>
            </select>
            <button id="buttoncmd" class="btn btn-primary"><?php echo _T("Send custom command", "xmppmaster"); ?></button>
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

jQuery(function() {
    var t = jQuery('#select option:selected').val();
    jQuery('#namecmd').val(t);
    var y = jQuery('#select option:selected').text();
    jQuery('#namecmdos').val(y);
});

jQuery('#select').on('change', function() {
    var t = jQuery('#select option:selected').val();
    jQuery('#namecmd').val(t);
    var y = jQuery('#select option:selected').text();
    jQuery('#namecmdos').val(y);
});

jQuery('#buttoncmd').click(function() {
    groupinfo["namecmd"] = jQuery('#namecmd').val();
    groupinfo["namecmdos"] = jQuery('#namecmdos').val();
    groupinfo["user"] = jQuery('#user').val();
    groupinfo["actionqa"] = jQuery('#action').val();
    groupinfo["groupname"] = jQuery('#groupname').val();
    groupinfo["type"] = jQuery('#type').val();
    jQuery.get("modules/xmppmaster/xmppmaster/actioncustomquickactiongrp.php", groupinfo)
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
        alert("All machines are running");
    } else {
        text = "";
        for (var i = 0; i < machine_not_present.length; i++) {
            text = text + machine_not_present[i] + ", ";
        }
        alert("Wakeonlan on the following machines in progress\n" + text, "", "alert-info");
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
        alert("No machines are running\nReboot possible only on running machine");
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_not_present[i] + ", ";
        }
        alert("Reboot on the following machines in progress\n" + text, "", "alert-info");
    }
}

function shutdownfunction(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_already_present.length == 0) {
        alert("All machines are off\nShutdown possible only on running machines");
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_already_present[i] + ", ";
        }
        alert("shutdown on the following machines in progress\n" + text, "", "alert-info");
    }
}

function vncchangepermsfunction(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_already_present.length == 0) {
        alert("All machines are off\nVNC settings change available only on running machines");
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_already_present[i] + ", ";
        }
        alert("VNC settings change on the following machines in progress\n" + text, "", "alert-info");
    }
}

function installkey(data) {
    uuid = data[0];
    cn = data[1];
    presence = data[2];
    machine_already_present = data[3];
    machine_not_present = data[4];
    if (machine_already_present.length == 0) {
        alert("No machines are running\nARS key installation possible only on running machine");
    } else {
        text = "";
        for (var i = 0; i < machine_already_present.length; i++) {
            text = text + machine_already_present[i] + ", ";
        }
        alert("ARS key installation on the following machines in progress\n" + text, "", "alert-info");
    }
}

jQuery('#wol,#wol0').unbind().on('click', function() {
    groupinfo['wol'] = jQuery('#checkboxwol').is(':checked');
    jQuery.get("modules/xmppmaster/xmppmaster/actionwakeonlan.php", groupinfo)
        .done(function(data) {
            wol(data);
        });
});

jQuery('#inventory,#inventory0').on('click', function() {
    jQuery.get("modules/xmppmaster/xmppmaster/actioninventory.php", groupinfo)
        .done(function(data) {
            inventory(data);
        });
});

jQuery('#reboot,#reboot0').on('click', function() {
    jQuery.get("modules/xmppmaster/xmppmaster/actionrestart.php", groupinfo)
        .done(function(data) {
            reboot(data);
        });
});

jQuery('#installkey,#installkey0').on('click', function() {
    jQuery.get("modules/xmppmaster/xmppmaster/actionkeyinstall.php", groupinfo)
        .done(function(data) {
            installkey(data);
        });
});

jQuery('#shutdown,#shutdown0').on('click', function() {
    groupinfo['time'] = jQuery('#mytimeshutdown').val();
    groupinfo['msg'] = jQuery('#msgshutdown').val();
    jQuery.get("modules/xmppmaster/xmppmaster/actionshutdown.php", groupinfo)
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
    jQuery.get("modules/xmppmaster/xmppmaster/actionvncchangeperms.php", groupinfo)
        .done(function(data) {
            vncchangepermsfunction(data);
        });
});
</script>
