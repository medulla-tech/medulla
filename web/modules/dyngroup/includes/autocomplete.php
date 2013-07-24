<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id$
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

class Autocomplete {
    function Autocomplete($module, $criterion, $value = '', $edition = false) {
        $this->module = $module;
        $this->criterion = $criterion;
        $this->val = $value;
        $this->b_label = _T("Add", "dyngroup");
        if ($edition) {
            $this->b_label = _T("Modify", "dyngroup");
        }
    }
    
    function display() {
        if (in_array($_GET['add_param'], array("Entity"))) {
            $frequency = 1.0;
        }
        else {
            $frequency = 2.0;
        }
    ?>

    <td style="text-align:right;"><?php echo  _T("Add a value", "dyngroup"); ?></td><td>

    <input type="text" autocomplete="off" id="autocomplete" name="value" size="23" value="<?php echo $this->val ?>" /> 
    
    <input name="buser" type="submit" class="btnPrimary" value="<?php echo  $this->b_label; ?>"/> 
    </td></tr>
    </table>
    
    <script src="jsframework/lib/jquery.jqEasySuggest.min.js" type="text/javascript"></script>
    <script type="text/javascript">

        /*var groups = new Array();
        new Ajax.Autocompleter('autocomplete','autocomplete_choices',
            'main.php?module=base&submod=computers&action=ajaxAutocompleteSearch&modulename=<?php echo  $this->module ?>&criterion=<?php echo  $this->criterion ?>', {paramName: "value", frequency: <?php echo $frequency ?>});
       */
       jQuery(function(){
           jQuery('#autocomplete').jqEasySuggest({
		ajax_file_path 		: 'main.php?module=base&submod=computers&action=ajaxAutocompleteSearch&modulename=<?php echo  $this->module ?>&criterion=<?php echo  $this->criterion ?>',
		min_keyword_length	: 3,
		showLoadingImage	: false,
		focus_color		: "red",
		keyupDelay		: 100,
		//id_element	 	: "autocomplete_old",
		sql_match_type	 	: "starts",
		es_width		: "215",
		es_opacity		: 0.95,
		es_max_results		: 10,
		es_offset_left		: 0,
		es_offset_top		: 0	
            });
       });
        
    </script>
    <style type="text/css">
        .easy_suggest{
                background-color: #e5e5e5;
                border: 1px solid #ccc;
                border-width: 0px 1px;
                -moz-box-shadow: 0 2px 4px #ccc;
                -webkit-box-shadow: 0 2px 4px #ccc;
                box-shadow: 0 2px 4px #ccc;
                -webkit-border-bottom-right-radius: 8px;
                -webkit-border-bottom-left-radius: 8px;
                -moz-border-radius-bottomright: 8px;
                -moz-border-radius-bottomleft: 8px;
                border-bottom-right-radius: 8px;
                border-bottom-left-radius: 8px;
                display: none;
                overflow: hidden;
                position: absolute;
                z-index: 9999;
        }
        .easy_list{
                list-style-type: none;
                margin: 0px;
                padding: 0px;
                width : 100%;
        }
        .easy_list li{
                border: 1px solid #ccc;
                border-width: 0px 1px 1px 0px;
                font-size:12px;
                list-style : none;
                text-align:left;
                width : 100%;
        }
        .easy_list li a{
                color: #000;
                display: block;
                padding: 5px;
                text-decoration: none;
        }
        .easy_list li.selected{
                background-color: #678FD6;
                color: #fff;
        }
        .easy_list li.selected a{
                color : #fff;
        }
    </style>
    <?php
    }
}

?>
