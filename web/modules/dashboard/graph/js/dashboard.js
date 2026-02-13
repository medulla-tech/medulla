/*
 * (c) 2016-2025 Siveo, http://www.siveo.net
 *
 * Dashboard drawer and widget organization
 */

jQuery(function() {
    var drawer = jQuery('#disabled-widgets-drawer');
    var drawerBtn = jQuery('#disabled-widgets-btn');
    var overlay = jQuery('#drawer-overlay');
    var collapsedSection = jQuery('#collapsed-widgets-section');

    // Update button visibility and count
    function updateDrawerButton() {
        var count = collapsedSection.find('.column').length;
        if (count > 0) {
            drawerBtn.removeClass('hidden');
            drawerBtn.find('.btn-count').text(count);
        } else {
            drawerBtn.addClass('hidden');
            closeDrawer();
        }
    }

    // Open drawer
    function openDrawer() {
        drawer.addClass('open');
        overlay.addClass('visible');
    }

    // Close drawer
    function closeDrawer() {
        drawer.removeClass('open');
        overlay.removeClass('visible');
    }

    // Toggle drawer
    drawerBtn.on('click', openDrawer);
    overlay.on('click', closeDrawer);
    jQuery('.drawer-close').on('click', closeDrawer);

    // Close on Escape key
    jQuery(document).on('keydown', function(e) {
        if (e.key === 'Escape') closeDrawer();
    });

    // Move collapsed widgets to drawer
    function organizeCollapsedWidgets() {
        // Move collapsed columns to drawer
        jQuery('#dashboard-grid > .column.collapsed-column').each(function() {
            jQuery(this).appendTo(collapsedSection);
        });

        // Move uncollapsed columns back to grid
        var grid = jQuery('#dashboard-grid');
        collapsedSection.find('.column:not(.collapsed-column)').each(function() {
            jQuery(this).appendTo(grid);
        });

        updateDrawerButton();
    }

    // Initial organization
    setTimeout(organizeCollapsedWidgets, 100);

    // Re-organize when widgets are toggled
    jQuery(document).on('change', '.switch input', function() {
        setTimeout(organizeCollapsedWidgets, 50);
    });
});
