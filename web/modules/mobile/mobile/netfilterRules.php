<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Network Filter Rules", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();
?>

<?php
$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxNetfilterRules"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
var _nfrBaseUrl = '<?php echo rtrim(urlStrRedirect("mobile/mobile/ajaxNetfilterRules"), "&"); ?>';

function _nfrBuildUrl(filter, start, end, max) {
    var field = jQuery('#nfr_field').val() || 'all';
    var url = _nfrBaseUrl
        + '&filter=' + encodeURIComponent(filter)
        + '&field='  + encodeURIComponent(field)
        + '&maxperpage=' + (max || maxperpage);
    if (start !== undefined) url += '&start=' + start + '&end=' + end;
    return url;
}

updateSearch = function() {
    clearTimers();
    jQuery.ajax({ url: _nfrBuildUrl(document.Form.param.value), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};
updateSearchParam = function(filter, start, end, max) {
    clearTimers();
    jQuery.ajax({ url: _nfrBuildUrl(filter, start, end, max), type: 'get',
        success: function(data) { jQuery('#container').html(data); } });
};

jQuery(function() {
    var fieldSel = '<select id="nfr_field">'
        + '<option value="all"><?php echo addslashes(_T("All fields", "mobile")); ?></option>'
        + '<option value="domain"><?php echo addslashes(_T("Domain", "mobile")); ?></option>'
        + '<option value="type"><?php echo addslashes(_T("Type", "mobile")); ?></option>'
        + '</select>';
    jQuery('#searchBest').prepend(fieldSel);
    jQuery('#nfr_field').on('change', function() { pushSearch(); });
});
</script>
