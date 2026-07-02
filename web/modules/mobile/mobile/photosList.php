<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Device Photos", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
	return;
}

if (isset($_GET['saved']) && $_GET['saved'] == '1') {
    new NotifyWidgetSuccess(_T("Photos settings saved successfully", "mobile"));
}
?>

<?php
$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxPhotosList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
var _photosBaseUrl = '<?php echo rtrim(urlStrRedirect("mobile/mobile/ajaxPhotosList"), "&"); ?>';

function _photosBuildUrl(filter, start, end, max) {
    var field = jQuery('#photos_field').val() || 'all';
    var url = _photosBaseUrl
        + '&filter=' + encodeURIComponent(filter)
        + '&field='  + encodeURIComponent(field)
        + '&maxperpage=' + (max || maxperpage);
    if (start !== undefined) url += '&start=' + start + '&end=' + end;
    return url;
}

updateSearch = function() {
    clearTimers();
    jQuery.ajax({
        url: _photosBuildUrl(document.Form.param.value),
        type: 'get',
        success: function(data) { jQuery('#container').html(data); }
    });
};

updateSearchParam = function(filter, start, end, max) {
    clearTimers();
    jQuery.ajax({
        url: _photosBuildUrl(filter, start, end, max),
        type: 'get',
        success: function(data) { jQuery('#container').html(data); }
    });
};

jQuery(function() {
    var fieldSel = '<select id="photos_field">'
        + '<option value="all"><?php echo addslashes(_T("All fields", "mobile")); ?></option>'
        + '<option value="device"><?php echo addslashes(_T("Device", "mobile")); ?></option>'
        + '<option value="filename"><?php echo addslashes(_T("File name", "mobile")); ?></option>'
        + '<option value="location"><?php echo addslashes(_T("Location", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(fieldSel);

    jQuery('#photos_field').on('change', function() { pushSearch(); });

    var $h2 = jQuery('h2').first();
    $h2.wrap('<div style="display:flex;align-items:center;justify-content:space-between;"></div>');
    $h2.after(
        '<span style="flex-shrink:0;margin-left:16px;">'
        + '<a href="<?php echo addslashes(urlStrRedirect('mobile/mobile/photosSettings')); ?>" class="btnSecondary">'
        + '<?php echo addslashes(_T('Settings', 'mobile')); ?>'
        + '</a></span>'
    );
});
</script>
