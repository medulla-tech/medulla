<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Device Export/Import", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}
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
                        <label><input type="checkbox" name="columns[]" value="custom1" checked> <?php echo _T("Email", "mobile"); ?></label>
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

    <form id="importForm" method="post" action="<?php echo urlStrRedirect("mobile/mobile/deviceImportAction"); ?>" enctype="multipart/form-data">
        <table class="listinfos">
            <tr>
                <td style="width: 200px;"><?php echo _T("CSV file", "mobile"); ?></td>
                <td>
                    <input type="file" name="csv_file" accept=".csv" required />
                </td>
            </tr>
        </table>

        <div class="help-text">
            <?php echo _T("Upload a CSV file exported from this page. The file must have a header row with column names. Writable columns: number, description, configuration, imei, phone, groups, custom1 (email). Existing devices (matched by number) will be updated. New devices require a 'configuration' value.", "mobile"); ?>
        </div>

        <input type="submit" class="btnPrimary" value="<?php echo _T("Import from CSV", "mobile"); ?>" />
    </form>
</div>

<div id="enrollModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9999;align-items:center;justify-content:center;">
    <div style="background:#fff;border-radius:10px;padding:30px;width:560px;max-width:95%;box-shadow:0 10px 40px rgba(0,0,0,0.3);">
        <h3 style="margin:0 0 8px;color:#25607D;"><?php echo _T("Sending enrollment emails", "mobile"); ?></h3>
        <p id="enrollSummary" style="margin:0 0 20px;font-size:13px;color:#666;"></p>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <div style="flex:1;background:#e5e7eb;border-radius:4px;height:10px;">
                <div id="enrollBar" style="background:#25607D;height:10px;border-radius:4px;width:0%;transition:width 0.2s;"></div>
            </div>
            <span style="font-size:13px;white-space:nowrap;"><span id="enrollCurrent">0</span> / <span id="enrollTotal">0</span></span>
        </div>
        <div id="enrollLog" style="height:200px;overflow-y:auto;border:1px solid #e5e7eb;border-radius:4px;padding:8px;font-size:12px;background:#f9fafb;"></div>
        <div style="margin-top:20px;text-align:right;">
            <button id="enrollCloseBtn" class="btnPrimary" disabled><?php echo _T("Close", "mobile"); ?></button>
        </div>
    </div>
</div>

<script type="text/javascript">
var importActionUrl = <?php echo json_encode(urlStrRedirect('mobile/mobile/deviceImportAction')); ?>;
var enrollDoneUrl = <?php echo json_encode(urlStrRedirect('mobile/mobile/index')); ?>;
var sendEmailUrl = <?php echo json_encode(urlStrRedirect('mobile/mobile/sendEnrollmentEmailAjax')); ?>;

function escHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function sendEnrollmentEmail(list, i) {
    var total = list.length;
    if (i >= total) {
        jQuery('#enrollBar').css('width', '100%');
        jQuery('#enrollCurrent').text(total);
        jQuery('#enrollCloseBtn').prop('disabled', false).on('click', function() {
            window.location.href = enrollDoneUrl;
        });
        return;
    }
    jQuery('#enrollCurrent').text(i + 1);
    jQuery('#enrollBar').css('width', Math.round(((i + 1) / total) * 100) + '%');
    var item = list[i];
    jQuery.post(sendEmailUrl, { email: item.email, name: item.name }, function(resp) {
        var color = resp.ok ? '#16a34a' : '#dc2626';
        var label = resp.ok ? 'Sent' : 'Failed';
        var msg   = '[' + label + '] ' + escHtml(item.name) + ' - ' + escHtml(item.email) + (resp.ok ? '' : ' (' + escHtml(resp.error || 'failed') + ')');
        jQuery('#enrollLog').prepend('<div style="color:' + color + ';padding:2px 0;">' + msg + '</div>');
        sendEnrollmentEmail(list, i + 1);
    }, 'json').fail(function() {
        var msg = '[Failed] ' + escHtml(item.name) + ' - ' + escHtml(item.email) + ' (network error)';
        jQuery('#enrollLog').prepend('<div style="color:#dc2626;padding:2px 0;">' + msg + '</div>');
        sendEnrollmentEmail(list, i + 1);
    });
}

function openEnrollModal(emailList, summary) {
    jQuery('#enrollSummary').text(summary);
    jQuery('#enrollTotal').text(emailList.length);
    jQuery('#enrollCurrent').text(0);
    jQuery('#enrollBar').css('width', '0%');
    jQuery('#enrollLog').empty();
    jQuery('#enrollCloseBtn').prop('disabled', true);
    jQuery('#enrollModal').css('display', 'flex');
    sendEnrollmentEmail(emailList, 0);
}

function showImportError(msg) {
    var banner = jQuery('<div style="background:#fee2e2;border:1px solid #fca5a5;color:#991b1b;padding:12px 16px;border-radius:6px;margin-bottom:16px;"></div>').text(msg);
    jQuery('#importForm').before(banner);
}

jQuery(document).ready(function() {
    jQuery('#importForm').on('submit', function(e) {
        e.preventDefault();
        var btn = jQuery(this).find('input[type=submit]');
        btn.prop('disabled', true).val('<?php echo _T("Importing...", "mobile"); ?>');
        jQuery.ajax({
            url: importActionUrl,
            method: 'POST',
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function(resp) {
                btn.prop('disabled', false).val('<?php echo _T("Import from CSV", "mobile"); ?>');
                if (resp.status === 'error') {
                    showImportError(resp.message || 'Import failed');
                    return;
                }
                var summary = 'Import: ' + resp.created + ' created, ' + resp.updated + ' updated, ' + resp.skipped + ' skipped';
                if (resp.errors && resp.errors.length) {
                    summary += '. Errors: ' + resp.errors.slice(0, 3).join('; ');
                }
                if (resp.email_list && resp.email_list.length > 0) {
                    openEnrollModal(resp.email_list, summary);
                } else {
                    window.location.href = <?php echo json_encode(urlStrRedirect('mobile/mobile/index')); ?>;
                }
            },
            error: function() {
                btn.prop('disabled', false).val('<?php echo _T("Import from CSV", "mobile"); ?>');
                showImportError('Request failed. Please try again.');
            }
        });
    });
});
</script>
