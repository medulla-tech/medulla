// function that writes the list order to a cookie
function saveOrder() {
    jQuery(".dashboard-column script").remove();
    jQuery(".dashboard-column").each(function(index, value){
        var colid = value.id;
        var cookieName = "cookie-" + colid;
        // Get the order for this column.
        var order = jQuery('#' + colid).sortable("toArray");
        // For each portlet in the column
        for ( var i = 0, n = order.length; i < n; i++ ) {
            // Determine if it is 'opened' or 'closed'
            var v = jQuery('#' + order[i] ).find('.portlet-content').is(':visible');
            // Modify the array we're saving to indicate what's open and
            //  what's not.
            order[i] = order[i] + ":" + v;
        }
        jQuery.cookie(cookieName, order, { path: "/", expiry: new Date(2012, 1, 1)});
        jQuery.cookie(cookieName+'-width',jQuery(this).width());
    });
}

// function that restores the list order from a cookie
function restoreOrder() {
    jQuery(".dashboard-column").each(function(index, value) {
        var colid = value.id;
        var cookieName = "cookie-" + colid
        var cookie = jQuery.cookie(cookieName);
        if ( cookie == null ) { return; }
        var IDs = cookie.split(",");
        for (var i = 0, n = IDs.length; i < n; i++ ) {
            var toks = IDs[i].split(":");
            if ( toks.length != 2 ) {
                continue;
            }
            var portletID = toks[0];
            var visible = toks[1]
            var portlet = jQuery(".dashboard-column")
                .find('#' + portletID)
                .appendTo(jQuery('#' + colid));
            if (visible === 'false') {
                portlet.find(".ui-icon").toggleClass("ui-icon-minus");
                portlet.find(".ui-icon").toggleClass("ui-icon-plus");
                portlet.find(".portlet-content").hide();
            }
        }
        jQuery(this).width(jQuery.cookie(cookieName+'-width'));
    });
}

jQuery(document).ready( function () {

    // Drag-and-drop on dashboard grid (only for active widgets)
    jQuery("#dashboard-grid").sortable({
        items: "> .dashboard-column:not(.collapsed-column):not(#collapsed-widgets-section)",
        handle: ".portlet-header",
        placeholder: "column-placeholder",
        tolerance: "pointer",
        start: function(event, ui) {
            ui.item.css('opacity', 0.7);
            ui.placeholder.height(ui.item.height());
        },
        stop: function(event, ui) {
            ui.item.css('opacity', 1);
            saveOrder();
        }
    });

    jQuery(".portlet")
        .addClass("ui-widget")
        .addClass("ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .prepend('<span class="ui-icon ui-icon-minus"></span>')
        .end()
        .find(".portlet-content");

    // Order is now fixed in PHP - no longer restored from cookies
    // restoreOrder();

    jQuery(".portlet-header .ui-icon").click(function() {
        jQuery(this).toggleClass("ui-icon-minus");
        jQuery(this).toggleClass("ui-icon-plus");
        jQuery(this).parents(".portlet:first").find(".portlet-content").toggle();
        saveOrder(); // This is important
    });
    jQuery(".portlet-header .ui-icon").hover(
        function() {jQuery(this).addClass("ui-icon-hover"); },
        function() {jQuery(this).removeClass('ui-icon-hover'); }
    );

    // Resize disabled - layout is fixed
    // setTimeout(function(){
    //     jQuery('.portlet-content').resizable({handles:'e'}).resize(function(){
    //         jQuery(this).parents('.dashboard-column:first').width(jQuery(this).width()+25);
    //         saveOrder();
    //     })
    // },1000);

});
