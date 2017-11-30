<?php
extract($_POST);
$lab =  (isset($actionlabel))? $actionlabel : uniqid();
$tableToggle =  "tableToggle".uniqid();
$toggleable  =  "toggleable".uniqid();
$idclass     =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1>Restart</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="action" value="actionrestart" />
        <input type="hidden" name="step" />
        <table id="<?php echo $tableToggle;?>">
        <?php
        echo '<tr class="'.$toggleable.'">';
            echo'
                    <th width="16%">Step label : </th>
                    <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>';
                    echo'
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
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
 <input  class="btn btn-primary" id="property" onclick='jQuery("<?php echo $idclass;?>").toggle();' type="button" value="propriety" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#<?php echo $tableToggle.' tr.'.$toggleable;?>" ).hide();
    });
</script>

