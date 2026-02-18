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

require_once("modules/xmppmaster/includes/xmlrpc.php");

// Get machine info
if(!isset($_GET['os']) && isset($_GET["objectUUID"])) {
    $machine = xmlrpc_getMachinefromuuid($_GET["objectUUID"]);
    $_GET["os"] = $machine["platform"];
}

$cn = htmlspecialchars($_GET['cn'] ?? '');
$os = htmlspecialchars($_GET['os'] ?? '');
$entity = htmlspecialchars($_GET['entity'] ?? '');
$presencemachinexmpp = $_GET['presencemachinexmpp'] ?? false;

$objectUUID = $_GET['objectUUID'] ?? '';
$type = $_GET['type'] ?? '';
$owner_realname = $_GET['owner_realname'] ?? '';
$owner = $_GET['owner'] ?? '';
$owner_firstname = $_GET['owner_firstname'] ?? '';
$vnctype = $_GET['vnctype'] ?? '';
$mod = $_GET['mod'] ?? '';
$user = $_GET['user'] ?? '';
$jid = $_GET['jid'] ?? '';
?>

<div class="quick-actions-popup">
    <!-- Header with machine info -->
    <h1><?php echo _T("Quick Actions", "xmppmaster"); ?></h1>

    <div class="machine-info">
        <div class="info-item">
            <span class="info-label"><?php echo _T("Machine", "xmppmaster"); ?></span>
            <span class="info-value"><?php echo $cn; ?></span>
        </div>
        <div class="info-item">
            <span class="info-label"><?php echo _T("OS", "xmppmaster"); ?></span>
            <span class="info-value"><?php echo $os; ?></span>
        </div>
        <div class="info-item">
            <span class="info-label"><?php echo _T("Entity", "xmppmaster"); ?></span>
            <span class="info-value"><?php echo $entity; ?></span>
        </div>
    </div>

    <!-- Main Actions -->
    <div class="actions-section">
        <div class="actions-grid">
            <?php if ($presencemachinexmpp): ?>
                <div class="action-item" id="shutdown0" title="<?php echo _T("Click here to shut down the remote machine:", "xmppmaster") . " " . $cn; ?>">
                    <img src="img/actions/power.svg" alt="Shutdown">
                    <span id="shutdown"><?php echo _T("Shutdown", "xmppmaster"); ?></span>
                    <label class="action-option" onclick="event.stopPropagation();">
                        <input type="checkbox" id="checkboxshutdown"> <?php echo _T("options", "xmppmaster"); ?>
                    </label>
                </div>
                <div class="action-item" id="reboot0" title="<?php echo _T("Click here to reboot the remote machine:", "xmppmaster") . " " . $cn; ?>">
                    <img src="img/actions/restart.svg" alt="Reboot">
                    <span id="reboot"><?php echo _T("Reboot", "xmppmaster"); ?></span>
                </div>
                <div class="action-item" id="inventory0" title="<?php echo _T("Click here to refresh the inventory for the remote machine:", "xmppmaster") . " " . $cn; ?>">
                    <img src="img/actions/inventory.svg" alt="Inventory">
                    <span id="inventory"><?php echo _T("Run inventory", "xmppmaster"); ?></span>
                </div>
                <div class="action-item" id="vncchangeperms0" title="<?php echo _T("Click here to change the settings for the VNC connection to the remote machine:", "xmppmaster") . " " . $cn; ?>">
                    <img src="img/actions/control.svg" alt="VNC">
                    <span id="vncchangeperms"><?php echo _T("Change VNC settings", "xmppmaster"); ?></span>
                    <label class="action-option" onclick="event.stopPropagation();">
                        <input type="checkbox" id="checkboxvncchangeperms" checked> <?php echo _T("Ask user approval", "xmppmaster"); ?>
                    </label>
                </div>
                <div class="action-item" id="installkey0" title="<?php echo _T("Click here to install an SSH key on the remote machine:", "xmppmaster") . " " . $cn; ?>">
                    <img src="img/actions/key.svg" alt="Key">
                    <span id="installkey"><?php echo _T("Install ARS key", "xmppmaster"); ?></span>
                </div>
            <?php else: ?>
                <div class="action-item" id="wol0" title="<?php echo _T("Click here to start the remote machine if it is not already running:", "xmppmaster") . " " . $cn; ?>">
                    <img src="img/actions/power.svg" alt="WOL">
                    <span id="wol"><?php echo _T("Wake on LAN", "xmppmaster"); ?></span>
                    <label class="action-option" onclick="event.stopPropagation();">
                        <input type="checkbox" id="checkboxwol"> <?php echo _T("Imaging", "xmppmaster"); ?>
                    </label>
                </div>
            <?php endif; ?>
        </div>
    </div>

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

    <?php if ($presencemachinexmpp): ?>
    <!-- Custom Command Section -->
    <?php
    $qacomand = array();
    $mm = array();
    $os_up_case = strtoupper($os);

    if (strpos($os_up_case, "WINDOW") !== false) {
        $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "windows");
    } elseif (strpos($os_up_case, "LINUX") !== false || strpos($os_up_case, "UBUNTU") !== false) {
        $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "linux");
    } elseif (strpos($os_up_case, "MACOS") !== false) {
        $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "macos");
    }
    ?>

    <div class="custom-command-section">
        <h3><?php echo _T("Custom command", "xmppmaster"); ?></h3>
        <div class="command-row">
            <select id="select">
                <?php
                foreach($qacomand['command'] as $tabblecommand) {
                    if($tabblecommand['namecmd'] != "Restart machine agent") {
                        $tabblecommand['customcmd'] = preg_replace('/\r?\n|\r/',' ', $tabblecommand['customcmd']);
                        $tabblecommand['customcmd'] = trim($tabblecommand['customcmd'], " \t\n\r");
                        echo '<option value="'.htmlspecialchars($tabblecommand['customcmd']).'">'.htmlspecialchars($tabblecommand['namecmd']).'</option>';
                        $mm[] = "'".addslashes($tabblecommand['namecmd'])."': {
                            'description' : '".addslashes($tabblecommand['description'])."',
                            'customcmd' : '".addslashes($tabblecommand['customcmd'])."',
                            'os' : '".addslashes($tabblecommand['os'])."',
                            'user' : '".addslashes($tabblecommand['user'])."'}";
                    }
                }
                ?>
            </select>
            <button id="buttoncmd" class="btn btn-primary"><?php echo _T("Send custom command", "xmppmaster"); ?></button>
        </div>
    </div>

    <!-- Monitoring Section -->
    <div class="monitoring-section">
        <h3><?php echo _T("Monitoring", "xmppmaster"); ?></h3>
        <div class="monitoring-grid">
            <div class="monitoring-item" id="clone_ps_aux">
                <img src="img/actions/process.svg" alt="Process">
                <span id="clone_ps_aux0"><?php echo _T("Process list", "xmppmaster"); ?></span>
            </div>
            <div class="monitoring-item" id="disk_usage">
                <img src="img/actions/disk.svg" alt="Disk">
                <span id="disk_usage0"><?php echo _T("Disk usage", "xmppmaster"); ?></span>
            </div>
            <div class="monitoring-item" id="agentinfo">
                <img src="img/actions/info.svg" alt="Info">
                <span id="agentinfo0"><?php echo _T("Agent details", "xmppmaster"); ?></span>
            </div>
        </div>
    </div>
    <?php endif; ?>
</div>

<!-- Hidden forms -->
<form name="formcmdcustom" id="formcmdcustom" action="main.php" method="GET" style="display:none;">
    <input type="hidden" name="module" value="xmppmaster">
    <input type="hidden" name="submod" value="xmppmaster">
    <input type="hidden" name="action" value="ActionQuickconsole">
    <?php foreach ($_GET as $key => $valu): ?>
        <?php if (!in_array($key, ['displayName', 'owner_realname', 'owner_firstname', 'mod', 'action'])): ?>
            <input type="hidden" name="<?php echo htmlspecialchars($key); ?>" value="<?php echo htmlspecialchars($valu); ?>">
        <?php endif; ?>
    <?php endforeach; ?>
    <input id="namecmd" type="hidden" name="namecmd" value="">
    <input id="customcmd" type="hidden" name="customcmd" value="">
    <input id="description" type="hidden" name="description" value="">
    <input id="os" type="hidden" name="os" value="">
    <input id="user" type="hidden" name="user" value="">
</form>

<form name="formmonitoring" id="formmonitoring" action="main.php" method="GET" style="display:none;">
    <input type="hidden" name="module" value="xmppmaster">
    <input type="hidden" name="submod" value="xmppmaster">
    <input type="hidden" name="action" value="xmppMonitoring">
    <input type="hidden" name="UUID" value="<?php echo htmlspecialchars($objectUUID); ?>">
    <input type="hidden" name="cn" value="<?php echo htmlspecialchars($cn); ?>">
    <input type="hidden" name="type" value="<?php echo htmlspecialchars($type); ?>">
    <input type="hidden" name="owner_realname" value="<?php echo htmlspecialchars($owner_realname); ?>">
    <input type="hidden" name="entity" value="<?php echo htmlspecialchars($entity); ?>">
    <input type="hidden" name="owner" value="<?php echo htmlspecialchars($owner); ?>">
    <input type="hidden" name="user" value="<?php echo htmlspecialchars($user); ?>">
    <input type="hidden" name="owner_firstname" value="<?php echo htmlspecialchars($owner_firstname); ?>">
    <input type="hidden" name="os" value="<?php echo htmlspecialchars($os); ?>">
    <input type="hidden" name="presencemachinexmpp" value="<?php echo htmlspecialchars($presencemachinexmpp); ?>">
    <input type="hidden" name="vnctype" value="<?php echo htmlspecialchars($vnctype); ?>">
    <input type="hidden" name="mod" value="<?php echo htmlspecialchars($mod); ?>">
    <input type="hidden" name="jid" value="<?php echo htmlspecialchars($jid); ?>">
    <input id="informationmonitor" type="hidden" name="information" value="">
    <input id="args" type="hidden" name="args" value="">
    <input id="kwargs" type="hidden" name="kwargs" value="">
</form>

<script type="text/javascript">
<?php if ($presencemachinexmpp): ?>
var myObject = {<?php echo implode(",", $mm); ?>};

jQuery(function() {
    var t = jQuery('#select option:selected').text();
    jQuery('#namecmd').val(t);
    jQuery('#customcmd').val(myObject[t].customcmd);
    jQuery('#description').val(myObject[t].description);
    jQuery('#os').val(myObject[t].os);
    jQuery('#user').val(myObject[t].user);
});

jQuery('#buttoncmd').click(function() {
    jQuery('#formcmdcustom').submit();
});

jQuery('#select').on('change', function() {
    var t = jQuery('#select option:selected').text();
    jQuery('#namecmd').val(t);
    jQuery('#customcmd').val(myObject[t].customcmd);
    jQuery('#description').val(myObject[t].description);
    jQuery('#os').val(myObject[t].os);
    jQuery('#user').val(myObject[t].user);
});
<?php endif; ?>

var uuid = <?php echo json_encode($_GET); ?>;

<?php if ($presencemachinexmpp): ?>
jQuery('#clone_ps_aux, #clone_ps_aux0').click(function() {
    jQuery('#informationmonitor').val('clone_ps_aux');
    jQuery('#formmonitoring').submit();
});

jQuery('#disk_usage, #disk_usage0').click(function() {
    jQuery('#informationmonitor').val('disk_usage');
    jQuery('#formmonitoring').submit();
});

jQuery('#agentinfo, #agentinfo0').click(function() {
    jQuery('#informationmonitor').val('agentinfos');
    jQuery('#formmonitoring').submit();
});
<?php endif; ?>

jQuery('#checkboxshutdown').click(function() {
    jQuery('#shutdowninfo').toggle();
});

jQuery('#wol, #wol0').on('click', function() {
    uuid['wol'] = jQuery('#checkboxwol').is(':checked');
    jQuery.get("modules/xmppmaster/xmppmaster/actionwakeonlan.php", uuid)
        .done(function(data) {
            alert("Wake on LAN sent to: " + uuid['cn'], "", "alert-info");
        });
});

jQuery('#inventory, #inventory0').on('click', function() {
    jQuery.get("modules/xmppmaster/xmppmaster/actioninventory.php", uuid)
        .done(function(data) {
            window.location.href = window.location.href;
        });
});

jQuery('#reboot, #reboot0').on('click', function() {
    jQuery.get("modules/xmppmaster/xmppmaster/actionrestart.php", uuid)
        .done(function(data) {
            alert("Reboot sent to: " + uuid['cn'], "", "alert-info");
        });
});

jQuery('#shutdown, #shutdown0').on('click', function() {
    uuid['time'] = jQuery('#mytimeshutdown').val();
    uuid['msg'] = jQuery('#msgshutdown').val();
    jQuery.get("modules/xmppmaster/xmppmaster/actionshutdown.php", uuid)
        .done(function(data) {
            alert("Shutdown sent to: " + uuid['cn'], "", "alert-info");
        });
});

jQuery('#vncchangeperms, #vncchangeperms0').on('click', function() {
    uuid['askpermission'] = jQuery('#checkboxvncchangeperms').is(":checked") ? 1 : 0;
    jQuery.get("modules/xmppmaster/xmppmaster/actionvncchangeperms.php", uuid)
        .done(function(data) {
            alert("VNC settings changed for: " + uuid['cn'], "", "alert-info");
        });
});

jQuery('#installkey, #installkey0').on('click', function() {
    jQuery.get("modules/xmppmaster/xmppmaster/actionkeyinstall.php", uuid)
        .done(function(data) {
            var obj = jQuery.parseJSON(data);
            alert("SSH key installed on: " + obj.hostname, "", "alert-info");
        });
});
</script>
