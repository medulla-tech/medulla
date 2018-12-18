<?php
extract($_POST);
$lab = "END_SUCCESS";
// $lab =  (isset($actionlabel))? $actionlabel : uniqid();
?>
<div class="header">
    <h1>End Success</h1>
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
                <th width="16%">Step label : </th>
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
                             }" />Delete package
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
                             }" />Inventory
             </td>';

             if(isset($inventory) && $inventory == "True")
             {
               echo '<td width="25%">
                   <select name="inventory">
                       <option  value="False">False</option>
                       <option selected value="True">True</option>
                   <select>
               </td>';
            }
            else{
              echo '<td width="25%">
                  <select name="inventory">
                      <option selected value="False">False</option>
                      <option  value="True">True</option>
                  <select>
              </td>';
            }
        echo '
        <td></td><td></td>
            </tr>
        </table>';
        ?>
    </div>
    <input  class="btn btn-primary" id="property" onclick='jQuery("#tableToggleSuccess tr.toggleable").toggle();' type="button" value="Options" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggleSuccess tr.toggleable" ).hide();
    });
</script>
