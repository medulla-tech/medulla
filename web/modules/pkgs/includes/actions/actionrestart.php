<?php

// {
//     "action": "actionrestart",
//     "step": 0,
//     "actionlabel": "bec6f486",
//     "targetrestart": "AM"
// }
extract($_POST);
$lab =  (isset($actionlabel))? $actionlabel : uniqid();
$tableToggle =  "tableToggle".uniqid();
$toggleable  =  "toggleable".uniqid();
$idclass     =  "#".$tableToggle.' tr.'.$toggleable;


$TargetstartList = array(
                        array(  "Labelselect"=>"Restart Machine",
                                "val" => "MA"),
                        array(  "Labelselect"=>"Restart Agent Machine",
                                "val" => "AM")
);
$targetrestart = (isset($targetrestart))?$targetrestart : "machine";
$options = "";
    foreach($TargetstartList as $obj)
        {
            if(isset($targetrestart) && $targetrestart == $obj['val'])
            {
                $options .= "<option value='".$obj['val']."' selected>".$obj['Labelselect']."</option>";
            }
            else{
                $options .= "<option value='".$obj['val']."'>".$obj['Labelselect']."</option>";
            }
        }
?>
<div class="header">
    <h1>Restart</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="action" value="actionrestart" />
        <input type="hidden" name="step" />
        <table id="tableToggle">
        <?php
        //---------------------label-----------------------------------
        echo '<tr class="toggleable">';
            echo'
                    <th width="16%">Step label : </th>
                    <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>';
                    echo'
                    </th>
                    <th></th>
                    <th></th>
                </tr>';

            echo '<tr class="toggleable">';

                echo '<td width="16%">Target Restart</td>
                    <td width="25%">
                        <select title="" name="targetrestart">'.$options.'</select>
                    </td>';
        echo '
             </tr>
            </table>
                ';
        //-------------------------------------------------------------

        ?>
        <!-- All extra options are added here-->
    </div>
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
<input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="Options" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
