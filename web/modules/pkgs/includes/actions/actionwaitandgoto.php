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
/*
descriptor type
         {
                       "step" : 8,
                       "action": "actionwaitandgoto",
                       "waiting" : 60,
                       "goto" : 7
        }

echo "<pre>";
    print_r( $_POST );
echo "</pre>";*/
$waiting =  (isset($waiting))? $waiting : 10;
$goto =  (isset($goto))? $goto : "END_SUCCESS";

?>
<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">wait_</div>
    <h1><?php echo _T('Wait and go to step', 'pkgs'); ?></h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="actionwaitandgoto" />
        <input type="hidden" name="step" />
        <input type="hidden" name="codereturn" value=""/>
    <table id="tableToggle">
       <tr class="toggleable">
            <th width="16%"><?php echo _T('Step label :', 'pkgs'); ?></th>
            <th width="25%">
                <input id="laction" type="text" name="actionlabel" value="<?php echo (isset($actionlabel))? $actionlabel : uniqid(); ?>"/>
            </th>
            <th></th>
            <th></th>
        </tr>
        <tr>
            <?php
                echo '
                <td>'
                    ._T("Wait for (seconds)","pkgs").
                '</td>
                <td>
                    <input " type="number" min="1" value="'.$waiting.'" name="waiting"  />
                </td>';
            ?>
        </tr>

        <?php echo '<tr class="toggleable">';?>
        <?php
           if(isset($goto))
            {
                echo '<td width="16%">
                    <input type="checkbox" checked
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                                }" />goto
                </td>
                <td width="25%">
                    <input type="text" min="0" value="'.$goto.'" name="goto"  />
                </td>';
            }
            else{
                echo '<td width="16%">
                    <input type="checkbox"
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                                }" />Go to step
                    </td>
                    <td width="25%">
                         <input type="text" min="0" value="END_SUCCESS" name="goto"  />
                    </td>';
            }
            ?><td></td>
            <td></td>
        </tr>

    </table>
        <!-- Option timeout -->
    </div>
    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
   <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
