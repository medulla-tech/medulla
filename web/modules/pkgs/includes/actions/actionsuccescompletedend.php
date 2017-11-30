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
        <table id="tableToggle">
            <tr>
                <th width="16%">Step label : </th>
                <th width="25%">'.$lab.'
                <th></th>
                <th></th>
            </tr>
            <tr class="toggleable">
             ';
            if(isset($clear))
            {
                echo '<td width="16%">
                    <input type="checkbox" checked 
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                }" />Delete package
                </td>
                <td width="25%">
                    <select name="clear">
                        <option selected value="True">True</option>
                        <option value="False">False</option>
                    <select>
                </td>';
            }
            else{
                echo '<td width="16%">
                    <input type="checkbox" 
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                }" />Delete package
                    </td>
                    <td width="25%">
                         <select name="clear" disabled>
                            <option value="True">True</option>
                            <option selected value="False">False</option>
                         <select>
                    </td>';
            }
        echo '
        <td></td><td></td>
            </tr>
        </table>';
        ?>
    </div>
    <input  class="btn btn-primary" id="property" onclick='jQuery("#tableToggle tr.toggleable").toggle();' type="button" value="propriety" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable" ).hide();
    });
</script>

