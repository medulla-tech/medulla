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
        // Not effective for now 
        $this->toggled = $toggled;
    }

    function display() {
      echo '<style>
.switch {
  position: relative;
  display: inline-block;
  width: 30px;
  height: 15px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: .4s;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 13px;
  width: 13px;
  left: 1px;
  bottom: 1px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:focus + .slider {
  box-shadow: 0 0 1px #2196F3;
}

input:checked + .slider:before {
  -webkit-transform: translateX(14px);
  -ms-transform: translateX(14px);
  transform: translateX(14px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 17px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>
';
        echo '<div class="portlet-header"><div class="header-title" style="display:inline">' . $this->title . '</div><div class="header-switch" style="display:inline;float:right;">
        <label class="switch" onchange="changeSwitch(jQuery(this))">
          <input type="checkbox" checked>
          <span class="slider round"></span>
        </label>
        </div></div>';
        echo '<div class="portlet-content" style="clear:both;">';
echo <<< JSSCRIPT
<script>
function changeSwitch(selector)
{
  jQuery(selector).closest('.portlet').find('.portlet-content').toggle()
}
</script>
JSSCRIPT;
        echo $this->display_content();
        echo '</div>';
    }

    function display_content() {
        throw Error("Must be implemented by subclass");
    }
}
