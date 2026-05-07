<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Device Contacts Sync", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
	return;
}

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxContactsList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
var _ctcBaseUrl = '<?php echo rtrim(urlStrRedirect("mobile/mobile/ajaxContactsList"), "&"); ?>';

function _ctcBuildUrl(filter, start, end, max) {
    var field = jQuery('#ctc_field').val() || 'all';
    var url = _ctcBaseUrl
        + '&filter=' + encodeURIComponent(filter)
        + '&field='  + encodeURIComponent(field)
        + '&maxperpage=' + (max || maxperpage);
    if (start !== undefined) url += '&start=' + start + '&end=' + end;
    return url;
}

updateSearch = function() {
    clearTimers();
    jQuery.ajax({ url: _ctcBuildUrl(document.Form.param.value), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};
updateSearchParam = function(filter, start, end, max) {
    clearTimers();
    jQuery.ajax({ url: _ctcBuildUrl(filter, start, end, max), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};

jQuery(function() {
    var fieldSel = '<select id="ctc_field">'
        + '<option value="all"><?php echo addslashes(_T("All fields", "mobile")); ?></option>'
        + '<option value="name"><?php echo addslashes(_T("Name", "mobile")); ?></option>'
        + '<option value="description"><?php echo addslashes(_T("Description", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(fieldSel);
    jQuery('#ctc_field').on('change', function() { pushSearch(); });
});
</script>
