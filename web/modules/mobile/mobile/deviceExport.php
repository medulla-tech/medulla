<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Device Export/Import", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();
?>

<style>
.export-import-section {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #f9f9f9;
}
.export-import-section h3 {
    margin-top: 0;
    border-bottom: 2px solid #0066cc;
    padding-bottom: 10px;
}
.column-selector {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 15px 0;
}
.column-selector label {
    display: flex;
    align-items: center;
    gap: 5px;
}
.help-text {
    color: #666;
    font-size: 0.9em;
    margin: 10px 0;
    padding: 10px;
    background-color: #fffbe6;
    border-left: 3px solid #ffc107;
}
</style>

<div class="export-import-section">
    <h3><?php echo _T("Export Devices to CSV", "mobile"); ?></h3>

    <form method="post" action="<?php echo urlStrRedirect("mobile/mobile/deviceExportAction"); ?>">
        <table class="listinfos">
            <tr>
                <td style="width: 200px;"><?php echo _T("Filter by group", "mobile"); ?></td>
                <td>
                    <select name="group_id">
                        <option value="">— <?php echo _T("All groups", "mobile"); ?> —</option>
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
            <tr>
                <td><?php echo _T("Filter by configuration", "mobile"); ?></td>
                <td>
                    <select name="configuration_id">
                        <option value="">— <?php echo _T("All configurations", "mobile"); ?> —</option>
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
            <tr>
                <td><?php echo _T("Text filter", "mobile"); ?></td>
                <td>
                    <input type="text" name="filter_text" placeholder="<?php echo _T("Device number or description", "mobile"); ?>" style="width: 300px;" />
                </td>
            </tr>
            <tr>
                <td style="vertical-align: top;"><?php echo _T("Columns to export", "mobile"); ?></td>
                <td>
                    <div class="column-selector">
                        <label><input type="checkbox" name="columns[]" value="description" checked> <?php echo _T("Description", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="configuration" checked> <?php echo _T("Configuration", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="imei" checked> <?php echo _T("IMEI", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="phone" checked> <?php echo _T("Phone", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="groups" checked> <?php echo _T("Groups", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="custom1" checked> <?php echo _T("Custom 1", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="custom2"> <?php echo _T("Custom 2", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="custom3"> <?php echo _T("Custom 3", "mobile"); ?></label>
                        <label><input type="checkbox" name="columns[]" value="serial" checked> <?php echo _T("Serial", "mobile"); ?></label>
                    </div>
                    <div class="help-text">
                        <?php echo _T("Device number is always exported as the first column (required for import). Read-only columns like serial are exported but ignored during import.", "mobile"); ?>
                    </div>
                </td>
            </tr>
        </table>

        <input type="submit" class="btnPrimary" value="<?php echo _T("Export to CSV", "mobile"); ?>" />
    </form>
</div>

<div class="export-import-section">
    <h3><?php echo _T("Import Devices from CSV", "mobile"); ?></h3>

    <form method="post" action="<?php echo urlStrRedirect("mobile/mobile/deviceImportAction"); ?>" enctype="multipart/form-data">
        <table class="listinfos">
            <tr>
                <td style="width: 200px;"><?php echo _T("CSV file", "mobile"); ?></td>
                <td>
                    <input type="file" name="csv_file" accept=".csv" required />
                </td>
            </tr>
        </table>

        <div class="help-text">
            <?php echo _T("Upload a CSV file exported from this page. The file must have a header row with column names. Writable columns: number, description, configuration, imei, phone, groups, custom1, custom2, custom3. Existing devices (matched by number) will be updated. New devices require a 'configuration' value.", "mobile"); ?>
        </div>

        <input type="submit" class="btnPrimary" value="<?php echo _T("Import from CSV", "mobile"); ?>" />
    </form>
</div>
