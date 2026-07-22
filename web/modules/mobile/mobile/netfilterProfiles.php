<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Network Filter Profiles", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}
?>

<?php
$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxNetfilterProfileList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
var _nfpBaseUrl = '<?php echo rtrim(urlStrRedirect("mobile/mobile/ajaxNetfilterProfileList"), "&"); ?>';

function _nfpBuildUrl(filter, start, end, max) {
    var mode    = jQuery('#nfp_mode').val()    || 'all';
    var enabled = jQuery('#nfp_enabled').val() || 'all';
    var url = _nfpBaseUrl
        + '&filter='      + encodeURIComponent(filter)
        + '&filter_mode=' + encodeURIComponent(mode)
        + '&enabled='     + encodeURIComponent(enabled)
        + '&maxperpage='  + (max || maxperpage);
    if (start !== undefined) url += '&start=' + start + '&end=' + end;
    return url;
}

updateSearch = function() {
    clearTimers();
    jQuery.ajax({ url: _nfpBuildUrl(document.Form.param.value), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};
updateSearchParam = function(filter, start, end, max) {
    clearTimers();
    jQuery.ajax({ url: _nfpBuildUrl(filter, start, end, max), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};

jQuery(function() {
    var $h2 = jQuery('h2').first();
    $h2.wrap('<div style="display:flex;align-items:center;justify-content:space-between;"></div>');
    $h2.after(
        '<span style="flex-shrink:0;margin-left:16px;">'
        + '<button class="btnPrimary" type="button" onclick="location.href=\'<?php echo urlStrRedirect("mobile/mobile/netfilterProfileEdit"); ?>\'"><?php echo addslashes(_T("Add profile", "mobile")); ?></button>'
        + '</span>'
    );

    var modeSel = '<select id="nfp_mode">'
        + '<option value="all"><?php echo addslashes(_T("All modes", "mobile")); ?></option>'
        + '<option value="BLOCKLIST"><?php echo addslashes(_T("Blocklist", "mobile")); ?></option>'
        + '<option value="ALLOWLIST"><?php echo addslashes(_T("Allowlist", "mobile")); ?></option>'
        + '</select>';
    var enabledSel = '<select id="nfp_enabled">'
        + '<option value="all"><?php echo addslashes(_T("All status", "mobile")); ?></option>'
        + '<option value="1"><?php echo addslashes(_T("Enabled", "mobile")); ?></option>'
        + '<option value="0"><?php echo addslashes(_T("Disabled", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(enabledSel + modeSel);
    jQuery('#nfp_mode, #nfp_enabled').on('change', function() { pushSearch(); });
});
</script>
