// function that writes the list order to a cookie
function saveOrder() {
    jQuery(".column script").remove();
    jQuery(".column").each(function(index, value){
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
    jQuery(".column").each(function(index, value) {
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
            var portlet = jQuery(".column")
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

    // Make columns sortable
    jQuery(".column").sortable({
        connectWith: ['.column'],
        stop: function(event,ui) { ui.item.css('opacity',1);saveOrder();},
        sort: function(event,ui) { ui.item.css('opacity',0.7); }
    });

    jQuery(".portlet")
        .addClass("ui-widget")
        .addClass("ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .prepend('<span class="ui-icon ui-icon-minus"></span>')
        .end()
        .find(".portlet-content");

    // Restore order from cookie
    restoreOrder();

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

    setTimeout(function(){
        jQuery('.portlet-content').resizable({handles:'e'}).resize(function(){
            jQuery(this).parents('.column:first').width(jQuery(this).width()+25);
            saveOrder();
        })
    },1000);

});
