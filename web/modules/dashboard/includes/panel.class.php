<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

class Panel {
    public $id;
    public $title;

    function __construct($id, $title, $toggled = true) {
        $this->id = $id;
        $this->title = $title;
        $this->data = getPanelInfos($id);

        //$toggled is used to show/hide the widget content
        if (isset($_SESSION['user']['widgets'][$this->id]))
        {
          if($_SESSION['user']['widgets'][$this->id] == true || $_SESSION['user']['widgets'][$this->id] == 1)
            $this->toggled = 'checked';
          else
            $this->toggled = '';
        }
        else
        {
          if($toggled)
          {
            $this->toggled = 'checked';
            $_SESSION['user']['widgets'][$this->id] = $toggled;
          }

          else
          {
            $_SESSION['user']['widgets'][$this->id] = 0;
            $this->toggled = '';
          }
        }
    }

    function display() {
        //echo '<h3 class="handle">' . $this->title . '</h3>';
        echo '<div class="portlet-header"><div class="header-title">' . $this->title . '</div><div class="header-switch">
        <label class="switch">
          <input type="checkbox" '.$this->toggled.' data-widget="'.$this->id.'">
          <span class="slider round"></span>
        </label>
        </div></div>';
        echo '<div class="portlet-content">';
echo <<< JSSCRIPT
<script>
jQuery(function(){
  var selector = "#$this->id .switch input";
  var portlet = jQuery(selector).closest('.portlet');
  var column = portlet.closest('.dashboard-column');

  // Initialize visibility and position
  var collapsedSection = jQuery('#collapsed-widgets-section');

  if(jQuery(selector).is(":checked")) {
    portlet.find('.portlet-content').show();
    portlet.removeClass('collapsed');
    column.removeClass('collapsed-column');
  } else {
    portlet.find('.portlet-content').hide();
    portlet.addClass('collapsed');
    column.addClass('collapsed-column');
    // Move to drawer
    column.appendTo(collapsedSection);
    // Update button
    var btn = jQuery('#disabled-widgets-btn');
    btn.removeClass('hidden');
    btn.find('.btn-count').text(collapsedSection.find('.dashboard-column').length);
  }

  // Bind change event
  jQuery(selector).off('change').on('change', function() {
    var input = jQuery(this);
    var portlet = input.closest('.portlet');
    var column = portlet.closest('.dashboard-column');
    var widgetId = input.data('widget');
    var collapsedSection = jQuery('#collapsed-widgets-section');

    if(input.is(":checked")) {
      // Widget enabled - move back to grid
      portlet.find('.portlet-content').show();
      portlet.removeClass('collapsed');
      column.removeClass('collapsed-column');
      // Move to grid
      column.appendTo(jQuery('#dashboard-grid'));
    } else {
      // Widget disabled - move to collapsed section
      portlet.find('.portlet-content').hide();
      portlet.addClass('collapsed');
      column.addClass('collapsed-column');
      // Move to collapsed section
      column.appendTo(collapsedSection);
    }

    // Update drawer button
    var btn = jQuery('#disabled-widgets-btn');
    var count = collapsedSection.find('.dashboard-column').length;
    if (count > 0) {
      btn.removeClass('hidden');
      btn.find('.btn-count').text(count);
    } else {
      btn.addClass('hidden');
      jQuery('#disabled-widgets-drawer').removeClass('open');
      jQuery('#drawer-overlay').removeClass('visible');
    }

    jQuery.ajax({
      url: "main.php?module=dashboard&submod=main&action=ajaxSessionPanels",
      type: 'get',
      data: {"widget": widgetId, "toggled": input.is(":checked") ? 1 : 0}
    });
  });
});
</script>
JSSCRIPT;
        echo $this->display_content();
        echo '</div>';
    }

    function display_content() {
        throw Error("Must be implemented by subclass");
    }
}
