<?php
/*
 * (c) 2024-2025 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse.
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

require_once("modules/urbackup/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$filter = (!empty($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$jidmachine = (!empty($_GET['jidmachine'])) ? htmlentities($_GET['jidmachine']) : "";
echo '<h1>'._T("Basket", "urbackup").'</h1>';

$machines = xmlrpc_get_machines_summary_list();?>
<form id="basket-sender" method="POST" action="#">
    <div class="field">
        <label for="machinedest-search">Select dest machine</label>
        <input type="text" id="machinedest-search" value="">
        <select name="machinedest" id="machinedest">
            <option class="option-header" disabled selected>Select machine</option>
<?php foreach($machines as $machine){
    echo '<option class="option-machine" value="'.$machine["jid"].'">'.$machine['hostname'].'</option>';
}?>
        </select>
    </div>

    <div class="field">
        <input type="submit" name="basket" value="<?php echo _T("Validate Basket", "urbackup");?>" >
    </div>
    <?php
// Display only the list on
if(isset($_SESSION["urbackup"]["files"]) && count($_SESSION["urbackup"]["files"]) > 0){?>
<div class="field">
    <h2>List of Selected Files</h2>
    <table class="listinfos" border="1" cellspacing="0" cellspanning="5">
    <thead><tr>
    <th>Selection</th>
    <th>Files</th>
    </tr></thead><tbody>
    <?php foreach($_SESSION["urbackup"]["files"] as $file){
        echo "<tr>";
        echo '<td><input type="checkbox" checked name="files[]" value="'.$file.'"></td>';
        echo '<td>'.$file.'</td>';
        echo '</tr>';

    }?>
    </tbody></table>
</div>
<?php
}
else{
    echo '<input type="hidden" name="files[]" value="">';
}

if(isset($_SESSION["urbackup"]["folders"]) && count($_SESSION["urbackup"]["folders"]) > 0){?>
<div class="field">
    <h2>List of Selected Folders</h2>
    <table class="listinfos" border="1" cellspacing="0" cellspanning="5">
    <thead><tr>
    <th>Selection</th>
    <th>Folders</th>
    </tr></thead><tbody>
    <?php foreach($_SESSION["urbackup"]["folders"] as $folder){
        echo "<tr>";
        echo '<td><input type="checkbox" checked name="folders[]" value="'.$folder.'"></td>';
        echo '<td>'.$folder.'</td>';
        echo '</tr>';

    }?>
    </tbody></table>
</div>
<?php }
else{
    echo '<input type="hidden" name="folders[]" value="">';
}
?>
<input type="hidden" name="machinesource" value="<?php echo $jidmachine;?>" >
<input type="hidden" name="base_path" value="<?php echo $_GET["base_path"];?>" >
<input type="hidden" name="basename" value="<?php echo $_GET["basename"];?>" >
</form>


<style>
    .field{
        margin-top:28px;
    }
</style>

<script>
/**
 * Disable the validate button on basket popup
 */
function disableValidate(){
    jQuery("input[name='basket']").prop("disabled", true);
    jQuery("input[name='basket']").attr("title", "<?php echo _T("You must choose a destination machine", "urbackup");?>");
}

/**
 * enable the validate button on basket popup
 */
function enableValidate(){
    jQuery("input[name='basket']").prop("disabled", false);
    jQuery("input[name='basket']").attr("title", "");
}

jQuery(document).ready(function(){
    // By default when the popup opens:
    jQuery("#popup").css("overflow", "scroll");
    jQuery("#popup").css("max-height", "650px");
    disableValidate();

    // search machines by name corresponding to the input value
    jQuery("#machinedest-search").on("keyup", function(){
        let name = jQuery(this).val()

        if(name==""){
            jQuery("#machinedest .option-machine").show();
            jQuery("#machinedest .option-header").prop("selected", true)

        }
        else{
            jQuery("#machinedest .option-machine").hide();
            jQuery("#machinedest .option-machine[value*='"+name+"']").show()
            let count = jQuery("#machinedest .option-machine[value*='"+name+"']").length

            if(count == 0){
                // No match: disable the validate button, the user must select manually the machine
                jQuery("#machinedest .option-machine").show();
                jQuery("#machinedest .option-header").prop("selected", true)
                disableValidate();
            }
            else{
                // A valid machine name has been matched. Use it as selected name
                jQuery(".option-machine[value*='"+name+"']").first().prop("selected", true);
                enableValidate();
            }
        }
    })

    jQuery("#machinedest").on("change", function(){
        if(jQuery(this).val() == "undefined"){
            disableValidate();
        }
        else{
            enableValidate();
        }
    })
});
</script>
