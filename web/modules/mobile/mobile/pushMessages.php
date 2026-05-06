<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Push Messages", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxPushMessagesList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
var _pmBaseUrl = '<?php echo rtrim(urlStrRedirect("mobile/mobile/ajaxPushMessagesList"), "&"); ?>';

function _pmBuildUrl(filter, start, end, max) {
    var field = jQuery('#pm_field').val() || 'all';
    var url = _pmBaseUrl
        + '&filter=' + encodeURIComponent(filter)
        + '&field='  + encodeURIComponent(field)
        + '&maxperpage=' + (max || maxperpage);
    if (start !== undefined) url += '&start=' + start + '&end=' + end;
    return url;
}

updateSearch = function() {
    clearTimers();
    jQuery.ajax({
        url: _pmBuildUrl(document.Form.param.value),
        type: 'get',
        success: function(data) { jQuery('#container').html(data); }
    });
};

updateSearchParam = function(filter, start, end, max) {
    clearTimers();
    jQuery.ajax({
        url: _pmBuildUrl(filter, start, end, max),
        type: 'get',
        success: function(data) { jQuery('#container').html(data); }
    });
};

jQuery(function() {
    var newBtn = '<button type="button" class="btn btn-small btn-primary" style="flex-shrink:0;margin-right:auto;" onclick="location.href=\'<?php echo urlStrRedirect("mobile/mobile/newPushMessage"); ?>\'"><?php echo addslashes(_T("New push message", "mobile")); ?></button>';
    jQuery('.searchbox').prepend(newBtn);

    var fieldSel = '<select id="pm_field">'
        + '<option value="all"><?php echo addslashes(_T("All fields", "mobile")); ?></option>'
        + '<option value="device"><?php echo addslashes(_T("Device", "mobile")); ?></option>'
        + '<option value="type"><?php echo addslashes(_T("Type", "mobile")); ?></option>'
        + '<option value="payload"><?php echo addslashes(_T("Payload", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(fieldSel);

    jQuery('#pm_field').on('change', function() { pushSearch(); });
});
</script>
</script>