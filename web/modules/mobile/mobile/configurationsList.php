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
});
</script>
