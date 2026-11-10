<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Affichage formulaire
$p = new PageGenerator(_T("Configurations", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}

// Display notification if redirected from save
if (isset($_GET['saved']) && $_GET['saved'] == '1') {
    new NotifyWidgetSuccess(_T("Configuration saved successfully", "mobile"));
}
if (isset($_GET['error']) && $_GET['error'] == '1') {
    new NotifyWidgetFailure(_T("Failed to save configuration", "mobile"));
}

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxConfigurationsList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
var _cfgBaseUrl = '<?php echo rtrim(urlStrRedirect("mobile/mobile/ajaxConfigurationsList"), "&"); ?>';

function _cfgBuildUrl(filter, start, end, max) {
    var field = jQuery('#cfg_field').val() || 'all';
    var url = _cfgBaseUrl
        + '&filter=' + encodeURIComponent(filter)
        + '&field='  + encodeURIComponent(field)
        + '&maxperpage=' + (max || maxperpage);
    if (start !== undefined) url += '&start=' + start + '&end=' + end;
    return url;
}

updateSearch = function() {
    clearTimers();
    jQuery.ajax({ url: _cfgBuildUrl(document.Form.param.value), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};
updateSearchParam = function(filter, start, end, max) {
    clearTimers();
    jQuery.ajax({ url: _cfgBuildUrl(filter, start, end, max), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};

jQuery(function() {
    var fieldSel = '<select id="cfg_field">'
        + '<option value="all"><?php echo addslashes(_T("All fields", "mobile")); ?></option>'
        + '<option value="name"><?php echo addslashes(_T("Name", "mobile")); ?></option>'
        + '<option value="description"><?php echo addslashes(_T("Description", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(fieldSel);
    jQuery('#cfg_field').on('change', function() { pushSearch(); });

    var $h2 = jQuery('h2').first();
    $h2.wrap('<div style="display:flex;align-items:center;justify-content:space-between;"></div>');
    $h2.after(
        '<span style="flex-shrink:0;margin-left:16px;">'
        + '<button class="btnPrimary" type="button" onclick="_openNewCfgModal();">'
        + '<?php echo addslashes(_T("New configuration", "mobile")); ?>'
        + '</button></span>'
    );
});
</script>

<div id="newCfgModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;align-items:center;justify-content:center;">
    <div style="background:#fff;border-radius:10px;width:520px;max-width:95%;box-shadow:0 8px 32px rgba(0,0,0,0.25);overflow:hidden;display:flex;flex-direction:column;max-height:80vh;">
        <div style="background:#25607d;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;">
            <span style="color:#fff;font-size:1.1em;font-weight:600;"><?php echo _T("New configuration", "mobile"); ?></span>
            <button type="button" onclick="document.getElementById('newCfgModal').style.display='none';" style="background:none;border:none;color:#fff;font-size:1.3em;cursor:pointer;padding:0;">&times;</button>
        </div>
        <div style="padding:16px 24px 8px;flex-shrink:0;">
            <p style="margin:0;color:#6b7280;font-size:13px;"><?php echo _T("Choose a configuration to use as a starting point. You will be able to rename it and adjust settings.", "mobile"); ?></p>
        </div>
        <div id="newCfgList" style="overflow-y:auto;flex:1;padding:8px 24px 16px;">
            <?php
            $allConfigs = xmlrpc_get_hmdm_configurations();
            if (!is_array($allConfigs)) $allConfigs = [];
            $dupBase = urlStrRedirect('mobile/mobile/duplicateConfiguration');
            foreach ($allConfigs as $cfg) {
                $cfgId   = $cfg['id'] ?? '';
                $cfgName = htmlspecialchars($cfg['name'] ?? 'Unnamed', ENT_QUOTES);
                $dupUrl  = $dupBase . '&id=' . urlencode($cfgId);
                echo '<a href="' . htmlspecialchars($dupUrl, ENT_QUOTES) . '" '
                   . 'style="display:block;padding:10px 12px;border-radius:6px;margin-bottom:6px;background:#f9fafb;border:1px solid #e5e7eb;color:#1e3a4f;text-decoration:none;font-size:14px;" '
                   . 'onmouseover="this.style.background=\'#e0eef5\'" onmouseout="this.style.background=\'#f9fafb\'">'
                   . $cfgName
                   . ' <span style="float:right;font-size:12px;color:#6b7280;">' . _T("Duplicate →", "mobile") . '</span>'
                   . '</a>';
            }
            if (empty($allConfigs)) {
                echo '<p style="color:#6b7280;font-size:13px;">' . _T("No configurations found.", "mobile") . '</p>';
            }
            ?>
        </div>
        <div style="padding:12px 24px;border-top:1px solid #e5e7eb;text-align:right;flex-shrink:0;">
            <button class="btn btnSecondary" type="button" onclick="document.getElementById('newCfgModal').style.display='none';"><?php echo _T("Cancel", "mobile"); ?></button>
        </div>
    </div>
</div>

<script type="text/javascript">
document.getElementById('newCfgModal').addEventListener('click', function(e) {
    if (e.target === this) this.style.display = 'none';
});
window._openNewCfgModal = function() {
    document.getElementById('newCfgModal').style.display = 'flex';
};
</script>
