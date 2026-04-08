<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Network Traffic Filtering", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$settings = xmlrpc_get_netfilter_settings();
if (!is_array($settings)) {
    $settings = ['enabled' => false, 'filterMode' => 'BLOCKLIST'];
}

if (isset($_POST['save'])) {
    $enabled = isset($_POST['enabled']) && $_POST['enabled'] == '1';
    $filter_mode = in_array($_POST['filterMode'] ?? '', ['BLOCKLIST', 'ALLOWLIST']) ? $_POST['filterMode'] : 'BLOCKLIST';
    $result = xmlrpc_save_netfilter_settings($enabled, $filter_mode);
    if ($result) {
        new NotifyWidgetSuccess(_T("Settings saved", "mobile"));
        $settings['enabled'] = $enabled;
        $settings['filterMode'] = $filter_mode;
    } else {
        new NotifyWidgetFailure(_T("Failed to save settings", "mobile"));
    }
}
?>

<h3><?php echo _T("Network Traffic Filtering", "mobile"); ?></h3>
<p><?php echo _T("Configure DNS-based network filtering for all devices.", "mobile"); ?></p>

<form method="post">
    <table cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 500px; margin-top: 20px;">
        <tr>
            <td style="width: 200px;"><?php echo _T("Filtering enabled", "mobile"); ?></td>
            <td>
                <input type="hidden" name="enabled" value="0">
                <input type="checkbox" name="enabled" value="1" <?php echo !empty($settings['enabled']) ? 'checked' : ''; ?>>
            </td>
        </tr>
        <tr>
            <td><?php echo _T("Filter mode", "mobile"); ?></td>
            <td>
                <select name="filterMode">
                    <option value="BLOCKLIST" <?php echo ($settings['filterMode'] ?? '') === 'BLOCKLIST' ? 'selected' : ''; ?>><?php echo _T("Blocklist (block listed domains)", "mobile"); ?></option>
                    <option value="ALLOWLIST" <?php echo ($settings['filterMode'] ?? '') === 'ALLOWLIST' ? 'selected' : ''; ?>><?php echo _T("Allowlist (only allow listed domains)", "mobile"); ?></option>
                </select>
            </td>
        </tr>
        <tr>
            <td></td>
            <td style="display:flex; gap:10px; align-items:center;">
                <input type="submit" name="save" class="btn" value="<?php echo _T("Save", "mobile"); ?>">
                <a href="<?php echo urlStrRedirect("mobile/mobile/netfilterRules"); ?>" class="btn"><?php echo _T("Manage rules", "mobile"); ?></a>
            </td>
        </tr>
    </table>
</form>
