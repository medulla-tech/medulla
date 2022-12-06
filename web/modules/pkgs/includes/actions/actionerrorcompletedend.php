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
$lab = "END_ERROR";
?>
<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">END_ERROR</div>
    <h1><?php echo _T('End Error', 'pkgs'); ?></h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="action" value="actionerrorcompletedend" />
        <input type="hidden" name="step" />
        <?php
            echo '<input type="hidden" name="actionlabel" value="'.$lab.'"/>';
        ?>

        <?php
        echo'
            <table id="tableToggleend">
                 <tr class="toggleable">
                    <th width="16%">'._T("Step label :","pkgs").'</th>
                    <th width="25%">'.$lab.'
                    </th>
                    <th></th>
                    <th></th>
                </tr>
                <tr>
            </table>
                ';
        ?>
        <!-- All extra options are added here-->
    </div>
  <input  class="btn btn-primary" id="property" onclick='jQuery("#tableToggleend tr.toggleable").toggle();' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggleend tr.toggleable" ).hide();
    });
</script>
