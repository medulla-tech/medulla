<?php
/**
 * (c) 2016-2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net/
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */
require_once("../../../../includes/i18n.inc.php");
extract($_POST);
if (!isset($clear)) {
    $clear = "True";
}
if (!isset($inventory)) {
    $inventory = "noforced";
}

$lab = "END_SUCCESS";
// $lab =  (isset($actionlabel))? $actionlabel : uniqid();
?>
<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">END_SUCCESS</div>
    <h1><?php echo _T("End Success", "pkgs"); ?></h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="actionsuccescompletedend" />
        <?php
            echo '<input type="hidden" name="actionlabel" value="'.$lab.'"/>';
        ?>
        <?php
        echo'
        <table id="tableToggleSuccess">
            <tr class="toggleable">
                <th width="16%">'._T('Step label :','pkgs').'</th>
                <th width="25%">'.$lab.'
                <th></th>
                <th></th>
            </tr>
            <tr class="toggleable">
             ';



             $optChecked = "";
             if ($clear == "True") {
                 $optChecked = "checked";
             }
             echo '<td width="16%">
                 <input type="checkbox" '.$optChecked.'
                     onclick="if(jQuery(this).is(\':checked\')){
                                 jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                             }
                             else{
                                 jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
			     }" />'._T("Delete package","pkgs").'
             </td>';

            if(isset($clear) && $clear == "True")
            {

               echo '<td width="25%">
                   <select name="clear">
                       <option selected value="True">True</option>
                       <option value="False">False</option>
                   <select>
               </td>';
            }
             else{
               echo '<td width="25%">
                   <select name="clear">
                       <option value="True">True</option>
                       <option selected value="False">False</option>
                   <select>
               </td>';
             }

        echo '
        <td></td><td></td>
            </tr>
             <tr class="toggleable">
             ';

             $optChecked = "";
             if ($inventory != "False") {
                 $optChecked = "checked";
             }

             echo '<td width="16%">
                 <input type="checkbox" '.$optChecked.'
                     onclick="if(jQuery(this).is(\':checked\')){
                                 jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                             }
                             else{
                                 jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                             }" />'._T("Inventory","pkgs").'
             </td>';

            if(!isset($inventory)){ $inventory = "False"; }
                echo '<td width="25%">
                  <select name="inventory">';
                switch($inventory){
                    case "True":
                        echo'<option selected value="True">'._T('Forced inventory','pkgs').'</option>
                             <option value="False">'._T('No inventory','pkgs').'</option>
                             <option value="noforced">'._T('Inventory on change','pkgs').'</option>';
                    break;
                    case "False":
                        echo'<option value="True">'._T('Forced inventory','pkgs').'</option>
                             <option selected value="False">'._T('No inventory','pkgs').'</option>
                             <option value="noforced">'._T('Inventory on change','pkgs').'</option>';
                    break;
                    case "noforced":
                        echo'<option value="True">'._T('Forced inventory','pkgs').'</option>
                             <option value="False">'._T('No inventory','pkgs').'</option>
                             <option  selected value="noforced">'._T('Inventory on change','pkgs').'</option>';
                    break;
                }
                echo '<select>
                        </td>';

        echo '
        <td></td><td></td>
            </tr>
        </table>';
        ?>
    </div>
    <input  class="btn btn-primary" id="property" onclick='jQuery("#tableToggleSuccess tr.toggleable").toggle();' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggleSuccess tr.toggleable" ).hide();
    });
</script>
