<?php
require_once("../../../../includes/i18n.inc.php");
extract($_POST);
$lab = "END_SUCCESS";
// $lab =  (isset($actionlabel))? $actionlabel : uniqid();
?>
<div class="header">
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
             if(isset($clear))
                 $optChecked = "checked";
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
             if(isset($inventory))
                $optChecked = "checked";

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
