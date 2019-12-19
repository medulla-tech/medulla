<?php
require_once("../../../../includes/i18n.inc.php");
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
                        array(  "Labelselect"=>_T("Restart Machine","pkgs"),
                                "val" => "MA"),
                        array(  "Labelselect"=>_T("Restart Agent Machine","pkgs"),
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
    <h1><?php echo _T('Restart', 'pkgs'); ?></h1>
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
                    <th width="16%">'._T("Step label :","pkgs").'</th>
                    <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>';
                    echo'
                    </th>
                    <th></th>
                    <th></th>
                </tr>';

            echo '<tr class="toggleable">';

                echo '<td width="16%">'._T("Target Restart","pkgs").'</td>
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
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
<input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
