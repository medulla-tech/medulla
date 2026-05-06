<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Messages", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxMessagingList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
var _msgBaseUrl = '<?php echo rtrim(urlStrRedirect("mobile/mobile/ajaxMessagingList"), "&"); ?>';

function _msgBuildUrl(filter, start, end, max) {
    var field  = jQuery('#msg_field').val()  || 'all';
    var status = jQuery('#msg_status').val() || 'all';
    var url = _msgBaseUrl
        + '&filter=' + encodeURIComponent(filter)
        + '&field='  + encodeURIComponent(field)
        + '&status=' + encodeURIComponent(status)
        + '&maxperpage=' + (max || maxperpage);
    if (start !== undefined) url += '&start=' + start + '&end=' + end;
    return url;
}

updateSearch = function() {
    clearTimers();
    jQuery.ajax({
        url: _msgBuildUrl(document.Form.param.value),
        type: 'get',
        success: function(data) { jQuery('#container').html(data); }
    });
};

updateSearchParam = function(filter, start, end, max) {
    clearTimers();
    jQuery.ajax({
        url: _msgBuildUrl(filter, start, end, max),
        type: 'get',
        success: function(data) { jQuery('#container').html(data); }
    });
};

jQuery(function() {
    var newBtn = '<button type="button" class="btn btn-small btn-primary" style="flex-shrink:0;margin-right:auto;" onclick="location.href=\'<?php echo urlStrRedirect("mobile/mobile/newMessage"); ?>\'"><?php echo addslashes(_T("New message", "mobile")); ?></button>';
    jQuery('.searchbox').prepend(newBtn);

    var statusSel = '<select id="msg_status">'
        + '<option value="all"><?php echo addslashes(_T("All statuses", "mobile")); ?></option>'
        + '<option value="0"><?php echo addslashes(_T("Sent", "mobile")); ?></option>'
        + '<option value="1"><?php echo addslashes(_T("Delivered", "mobile")); ?></option>'
        + '<option value="2"><?php echo addslashes(_T("Read", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(statusSel);

    var fieldSel = '<select id="msg_field">'
        + '<option value="all"><?php echo addslashes(_T("All fields", "mobile")); ?></option>'
        + '<option value="device"><?php echo addslashes(_T("Device", "mobile")); ?></option>'
        + '<option value="message"><?php echo addslashes(_T("Message", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(fieldSel);

    jQuery('#msg_field, #msg_status').on('change', function() { pushSearch(); });
});
</script>
