<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Import Devices", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}
?>

<form class="mmc-form" id="importForm" method="post" action="<?php echo urlStrRedirect("mobile/mobile/deviceImportAction"); ?>" enctype="multipart/form-data">
    <input type="hidden" name="auth_token" value="<?php echo $_SESSION['auth_token']; ?>">
    <table class="mmc-form-table" cellspacing="0">
        <tr class="mmc-form-row">
            <td class="mmc-label"><?php echo _T("CSV file", "mobile"); ?></td>
            <td>
                <input type="file" name="csv_file" accept=".csv" required />
            </td>
        </tr>
        <tr class="mmc-form-row">
            <td class="mmc-label"><?php echo _T("Send enrollment emails", "mobile"); ?></td>
            <td>
                <label><input type="radio" name="send_emails" value="yes" checked /> <?php echo _T("Yes - send QR code email to new devices", "mobile"); ?></label><br>
                <label style="margin-top:4px;display:inline-block;"><input type="radio" name="send_emails" value="no" /> <?php echo _T("No - import only", "mobile"); ?></label>
            </td>
        </tr>
    </table>

    <input type="submit" class="btnPrimary" value="<?php echo _T("Import from CSV", "mobile"); ?>" />
</form>

<div id="enrollModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9999;align-items:center;justify-content:center;">
    <div style="background:#fff;border-radius:10px;padding:30px;width:560px;max-width:95%;box-shadow:0 10px 40px rgba(0,0,0,0.3);">
        <h3 style="margin:0 0 8px;color:#25607D;"><?php echo _T("Sending enrollment emails", "mobile"); ?></h3>
        <p id="enrollSummary" style="margin:0 0 20px;font-size:13px;color:#666;"></p>
        <div id="enrollProgressBar" style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <div style="flex:1;background:#e5e7eb;border-radius:4px;height:10px;">
                <div id="enrollBar" style="background:#25607D;height:10px;border-radius:4px;width:0%;transition:width 0.2s;"></div>
            </div>
            <span style="font-size:13px;white-space:nowrap;"><span id="enrollCurrent">0</span> / <span id="enrollTotal">0</span></span>
        </div>
        <div id="enrollLog" style="height:200px;overflow-y:auto;border:1px solid #e5e7eb;border-radius:4px;padding:8px;font-size:12px;background:#f9fafb;"></div>
        <div style="margin-top:20px;text-align:right;">
            <button id="enrollConfirmOk" class="btnPrimary" style="display:none;"><?php echo _T("Send", "mobile"); ?></button>
            <button id="enrollCancelBtn" class="btn btnSecondary" style="margin-left:8px;display:none;" onclick="jQuery('#enrollModal').hide();"><?php echo _T("Cancel", "mobile"); ?></button>
            <button id="enrollCloseBtn" class="btnPrimary" style="display:none;" disabled><?php echo _T("Close", "mobile"); ?></button>
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

function openEnrollModal(emailList, importSummary) {
    // Show confirm phase: display import summary + device list, wait for user to click Send
    jQuery('#enrollSummary').text(importSummary);
    jQuery('#enrollProgressBar').hide();
    jQuery('#enrollLog').empty();
    for (var i = 0; i < emailList.length; i++) {
        jQuery('#enrollLog').append('<div style="padding:2px 0;color:#374151;">' + escHtml(emailList[i].name) + ' &lt;' + escHtml(emailList[i].email) + '&gt;</div>');
    }
    jQuery('#enrollCloseBtn').hide();
    jQuery('#enrollConfirmOk').show().off('click').on('click', function() {
        // Switch to progress phase
        jQuery('#enrollConfirmOk').hide();
        jQuery('#enrollCancelBtn').hide();
        jQuery('#enrollTotal').text(emailList.length);
        jQuery('#enrollCurrent').text(0);
        jQuery('#enrollBar').css('width', '0%');
        jQuery('#enrollLog').empty();
        jQuery('#enrollProgressBar').show();
        jQuery('#enrollCloseBtn').show().prop('disabled', true);
        sendEnrollmentEmail(emailList, 0);
    });
    jQuery('#enrollCancelBtn').show();
    jQuery('#enrollModal').css('display', 'flex');
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
                var sendEmails = jQuery('input[name="send_emails"]:checked').val() === 'yes';
                var summary = 'Import: ' + resp.created + ' created, ' + resp.updated + ' updated, ' + resp.skipped + ' skipped';
                if (resp.errors && resp.errors.length) {
                    summary += '. Errors: ' + resp.errors.slice(0, 3).join('; ');
                }
                if (sendEmails && resp.email_list && resp.email_list.length > 0) {
                    openEnrollModal(resp.email_list, summary);
                } else {
                    // Show summary modal without sending emails
                    jQuery('#enrollSummary').text(summary);
                    jQuery('#enrollProgressBar').hide();
                    jQuery('#enrollLog').empty();
                    if (!sendEmails && resp.email_list && resp.email_list.length > 0) {
                        jQuery('#enrollLog').append('<div style="padding:4px 0;color:#6b7280;margin-bottom:6px;"><?php echo addslashes(_T("Email sending skipped (disabled by user).", "mobile")); ?></div>');
                        for (var i = 0; i < resp.email_list.length; i++) {
                            jQuery('#enrollLog').append('<div style="padding:2px 0;color:#374151;">' + escHtml(resp.email_list[i].name) + '</div>');
                        }
                    }
                    jQuery('#enrollConfirmOk').hide();
                    jQuery('#enrollCancelBtn').hide();
                    jQuery('#enrollCloseBtn').show().prop('disabled', false).off('click').on('click', function() {
                        window.location.href = enrollDoneUrl;
                    });
                    jQuery('#enrollModal').css('display', 'flex');
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
