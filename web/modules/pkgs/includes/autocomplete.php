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
class Autocomplete extends InputTpl {
    function Autocomplete($name, $ajaxfile, $module, $criterion, $value = '', $limit, $extracriterion, $edition = false) {
        parent::InputTpl ( $name );
        $this->ajaxfile = $ajaxfile;
        $this->module = $module;
        $this->criterion = $criterion;
        $this->val = $value;
        $this->limit = $limit;
        $this->extracriterion = $extracriterion;
    }

    function display($arrParam = array()) {
        if (in_array ( $_GET ['add_param'], array (
                "Entity" 
        ) )) {
            $frequency = 1.0;
        } else {
            $frequency = 2.0;
        }
        

        parent::display ( array (
                "value" => $this->val 
        ) );

        ?>
<script src="jsframework/lib/jquery.jqEasySuggest.min.js"
    type="text/javascript">
</script>

<script type="text/javascript">
    var extravalue = jQuery('#<?php echo  $this->extracriterion ?>').val();
    jQuery(function(){
        jQuery('#<?php echo $this->name?>').jqEasySuggest({
            //ajax_file_path       : '<?php echo $this->ajaxfile?>&modulename=<?php echo  $this->module ?>&criterion=<?php echo  $this->criterion ?>&extracriterion=value',
            ajax_file_path       : '<?php echo $this->ajaxfile?>&modulename=<?php echo  $this->module ?>&criterion=<?php echo  $this->criterion ?>&extracriterion='+extravalue,
            min_keyword_length	: <?php echo $this->limit?>,
            showLoadingImage     : false,
            //focus_color		: "red",
            keyupDelay           : 100,
            sql_match_type       : "starts",
            es_width             : "215",
            es_opacity           : 0.95,
            es_max_results       : 10,
            es_offset_left       : 0,
            es_offset_top        : 0
        });
    });
</script>

<style type="text/css">
.easy_suggest {
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

.easy_list {
    list-style-type: none;
    margin: 0px;
    padding: 0px;
    width: 100%;
}

.easy_list li {
    border: 1px solid #ccc;
    border-width: 0px 1px 1px 0px;
    font-size: 12px;
    list-style: none;
    text-align: left;
    width: 100%;
}

.easy_list li a {
    color: #000;
    display: block;
    padding: 5px;
    text-decoration: none;
}

.easy_list li.selected {
    background-color: #678FD6;
    color: #fff;
}

.easy_list li.selected a {
    color: #fff;
}
</style>
<?php
    }
}

?>
