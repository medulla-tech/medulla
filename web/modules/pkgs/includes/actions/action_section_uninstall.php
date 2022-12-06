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
            "action": "action_section_uninstall"
        }

    echo "<pre>";
        print_r( $_POST );
    echo "</pre>";
*/

?>
<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">Uninst_</div>
    <h1><?php echo _T('Uninstall Section', 'pkgs'); ?></h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_section_uninstall" />
        <input type="hidden" name="step" />
        <input id="laction" type="hidden" name="actionlabel" value="label_section_uninstall"/>
    </div>
    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
