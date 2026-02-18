<?php
/**
 * (c) 2015 siveo, http://www.siveo.net/
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
$url = array();
if(isset($_GET['agenttype']) && $_GET['agenttype'] == 'relayserver' or isset($_GET['uninventoried'])) {
    $_GET['cn'] = $_GET['hostname'];
}

$hostname = !empty($_GET['hostname']) ? htmlentities($_GET['hostname']) : "";
$_GET['cn'] = !empty($_GET['cn']) ? htmlentities($_GET['cn']) : $hostname;

if(isset($_GET['cn'])) {
    $zz = xmlrpc_getGuacamoleRelayServerMachineHostnameProto($_GET['cn']);
    $dd = $zz['machine'];
    $ee = $zz['proto'];
    foreach ($ee as $k) {
        $cux[$k[0]] = $k[1];
        $cux_id_hex = bin2hex($k[1]).'00'.bin2hex('c').'00'.bin2hex('mysql');
        $cux_id = base64_encode(hex2bin($cux_id_hex));
        $url[$k[0]] = str_replace('@@CUX_ID@@', $cux_id, $dd['urlguacamole']);
    }
}

$isServer = ($dd['agenttype'] == "relayserver");
?>
<div class="remote-popup">
    <h1><?php echo _T("Remote", "msc"); ?></h1>

    <!-- Connection methods -->
    <div class="remote-actions">
        <?php foreach ($url as $clef => $val): ?>
            <?php if ($clef == "VNC"): ?>
                <div class="remote-item" id="vnc">
                    <img src="img/actions/vnc.svg" alt="VNC">
                    <span>VNC</span>
                </div>
            <?php endif; ?>
            <?php if ($clef == "SSH"): ?>
                <?php
                $os_up_case = strtoupper($dd["platform"]);
                $isWindows = (strpos($os_up_case, "WINDOW") !== false);
                ?>
                <div class="remote-item" id="ssh">
                    <img src="<?php echo $isWindows ? 'img/actions/cmd.svg' : 'img/actions/ssh.svg'; ?>" alt="<?php echo $isWindows ? 'CMD' : 'SSH'; ?>">
                    <span><?php echo $isWindows ? 'CMD' : 'SSH'; ?></span>
                </div>
            <?php endif; ?>
            <?php if ($clef == "RDP"): ?>
                <div class="remote-item" id="rdp">
                    <img src="img/actions/rdp.svg" alt="RDP">
                    <span>RDP</span>
                </div>
            <?php endif; ?>
        <?php endforeach; ?>
    </div>

    <!-- Machine info -->
    <div class="remote-machine-info">
        <div class="info-header">
            <?php echo $isServer ? _T("Server", "msc") : _T("Computer", "msc"); ?>
        </div>
        <div class="info-grid">
            <div class="info-row">
                <span class="info-label"><?php echo _T("Hostname", "msc"); ?></span>
                <span class="info-value"><?php echo htmlspecialchars($dd['hostname']); ?></span>
            </div>
            <div class="info-row">
                <span class="info-label"><?php echo _T("Platform", "msc"); ?></span>
                <span class="info-value"><?php echo htmlspecialchars($dd['platform']); ?></span>
            </div>
            <div class="info-row">
                <span class="info-label"><?php echo _T("Architecture", "msc"); ?></span>
                <span class="info-value"><?php echo htmlspecialchars($dd['archi']); ?></span>
            </div>
            <div class="info-row">
                <span class="info-label"><?php echo _T("IP", "msc"); ?></span>
                <span class="info-value"><?php echo htmlspecialchars($dd['ip_xmpp'] . '/' . $dd['subnetxmpp']); ?></span>
            </div>
            <div class="info-row">
                <span class="info-label"><?php echo _T("MAC Address", "msc"); ?></span>
                <span class="info-value"><?php echo htmlspecialchars($dd['macaddress']); ?></span>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
var uuid = '<?php echo $_GET['objectUUID']; ?>';
var cn = '<?php echo $_GET['cn']; ?>';

<?php if (isset($url['SSH'])): ?>
jQuery('#ssh').on('click', function(){
    var ssh_url = '<?php echo $url['SSH']; ?>';
    var ssh_cux = '<?php echo $cux['SSH']; ?>';
    jQuery.get("modules/xmppmaster/xmppmaster/actionreversesshguacamole.php", { uuid: uuid, cn: cn, cux_id: ssh_cux, cux_type: "SSH" })
    .done(function(data) {
        window.open(ssh_url);
        alert("The SSH control session opens in a new window");
    });
});
<?php endif; ?>

<?php if (isset($url['RDP'])): ?>
jQuery('#rdp').on('click', function(){
    var rdp_url = '<?php echo $url['RDP']; ?>';
    var rdp_cux = '<?php echo $cux['RDP']; ?>';
    jQuery.get("modules/xmppmaster/xmppmaster/actionreversesshguacamole.php", { uuid: uuid, cn: cn, cux_id: rdp_cux, cux_type: "RDP" })
    .done(function(data) {
        window.open(rdp_url);
        alert("The RDP control session opens in a new window");
    });
});
<?php endif; ?>

<?php if (isset($url['VNC'])): ?>
jQuery('#vnc').on('click', function(){
    var vnc_url = '<?php echo $url['VNC']; ?>';
    var vnc_cux = '<?php echo $cux['VNC']; ?>';
    jQuery.get("modules/xmppmaster/xmppmaster/actionreversesshguacamole.php", { uuid: uuid, cn: cn, cux_id: vnc_cux, cux_type: "VNC" })
    .done(function(data) {
        window.open(vnc_url);
        alert("The VNC control session opens in a new window");
    });
});
<?php endif; ?>
</script>
