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
// descriptor
// {
//                 "action": "action_set_environ",
//                 "step": 0,
//                 "environ" : {"PLIP22" : "plop"  }
// }
?>
<?php
extract($_POST);
$lab =  (isset($actionlabel))? $actionlabel : uniqid();

$environstr="key1 :: value1,\nkey2 :: value2";
if(isset($environ))
{
    $environstr = "";
    foreach($environ as $key=>$value)
    {
        $environstr .= $key.' :: '.$value.",\n";
    }
}

$environstr = trim($environstr,",\n\r");
?>

<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">setenv_</div>
    <h1 class="action"><?php echo _T('Set Environment variables', 'pkgs'); ?></h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_set_environ" />
        <input type="hidden" name="step" />
            <table id="tableToggle">
                <tr class="toggleable">
                    <th width="16%"><?php echo _T('Step label : ', 'pkgs'); ?></th>
                    <th width="25%">
                        <?php echo'  <input type="text" name="actionlabel" value="'.$lab.'"/>'; ?>
                    </th>
                    <th></th>
                    <th></th>
                </tr>
                <tr>
                    <th width="16%"><?php echo _T('Environment variable', 'pkgs') ?></th>
                    <th width="25%">
                        <?php
                        echo'<textarea title="eg : key1 :: value1,'."\n".'key1 :: value1" name="environ">'.$environstr.'</textarea>';
                        ?>
                    </th>
                    <th></th>
                    <th></th>
                </tr>
            </table>
        <!-- All extra options are added here-->
    </div>
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
