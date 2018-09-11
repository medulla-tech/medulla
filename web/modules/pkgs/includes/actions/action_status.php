<?php
extract($_POST);

$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1>Deployment status</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="status" />
        <?php

        $lab =  (isset($actionlabel))? $actionlabel : uniqid();
        ?>
        <table id="tableToggle">
        <?php
        $stat = (isset($stat)) ? $stat : 0;
        echo'
           <tr class="toggleable">
                <th width="16%">Step label : </th>
                <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>
                <th></th>
                <th></th>
            </tr>
            <tr>
             ';
            echo '<td width="16%">
                   Stat
                </td>
                <td width="25%">
                  <input type="number" name="stat" min=0 max=100 value="'.$stat.'"/>';

                echo'
                </td>';
        echo '
        <td></td><td></td>
            </tr>
        </table>';
        ?>

    </div>

    <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="Options" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
