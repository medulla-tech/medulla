<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Export Devices", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}
?>

<h3><?php echo _T("Export Devices to CSV", "mobile"); ?></h3>

<form class="mmc-form" method="post" action="<?php echo urlStrRedirect("mobile/mobile/deviceExportAction"); ?>">
    <input type="hidden" name="auth_token" value="<?php echo $_SESSION['auth_token']; ?>">
    <table class="mmc-form-table" cellspacing="0">
        <tr class="mmc-form-row">
            <td class="mmc-label"><?php echo _T("Filter by group", "mobile"); ?></td>
            <td>
                <select name="group_id">
                    <option value=""><?php echo _T("All groups", "mobile"); ?></option>
                    <?php
                    $groups = xmlrpc_get_hmdm_groups();
                    if (is_array($groups)) {
                        foreach ($groups as $group) {
                            echo '<option value="' . htmlspecialchars($group['id']) . '">' . htmlspecialchars($group['name']) . '</option>';
                        }
                    }
                    ?>
                </select>
            </td>
        </tr>
        <tr class="mmc-form-row">
            <td class="mmc-label"><?php echo _T("Filter by configuration", "mobile"); ?></td>
            <td>
                <select name="configuration_id">
                    <option value=""><?php echo _T("All configurations", "mobile"); ?></option>
                    <?php
                    $configs = xmlrpc_get_hmdm_configurations();
                    if (is_array($configs)) {
                        foreach ($configs as $cfg) {
                            echo '<option value="' . htmlspecialchars($cfg['id']) . '">' . htmlspecialchars($cfg['name']) . '</option>';
                        }
                    }
                    ?>
                </select>
            </td>
        </tr>
        <tr class="mmc-form-row">
            <td class="mmc-label"><?php echo _T("Text filter", "mobile"); ?></td>
            <td>
                <input type="text" name="filter_text" placeholder="<?php echo _T("Device number or description", "mobile"); ?>" />
            </td>
        </tr>
        <tr class="mmc-form-row">
            <td class="mmc-label" style="vertical-align: top;"><?php echo _T("Columns to export", "mobile"); ?></td>
            <td>
                <label><input type="checkbox" name="columns[]" value="description" checked> <?php echo _T("Description", "mobile"); ?></label>&nbsp;&nbsp;
                <label><input type="checkbox" name="columns[]" value="configuration" checked> <?php echo _T("Configuration", "mobile"); ?></label>&nbsp;&nbsp;
                <label><input type="checkbox" name="columns[]" value="imei" checked> <?php echo _T("IMEI", "mobile"); ?></label>&nbsp;&nbsp;
                <label><input type="checkbox" name="columns[]" value="phone" checked> <?php echo _T("Phone", "mobile"); ?></label>&nbsp;&nbsp;
                <label><input type="checkbox" name="columns[]" value="groups" checked> <?php echo _T("Groups", "mobile"); ?></label>&nbsp;&nbsp;
                <label><input type="checkbox" name="columns[]" value="custom1" checked> <?php echo _T("Email", "mobile"); ?></label>&nbsp;&nbsp;
                <label><input type="checkbox" name="columns[]" value="serial" checked> <?php echo _T("Serial", "mobile"); ?></label>
            </td>
        </tr>
    </table>

    <input type="submit" class="btnPrimary" value="<?php echo _T("Export to CSV", "mobile"); ?>" />
</form>
