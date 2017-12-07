<?php
extract($_POST);
//$lab = "PACKAGE_CLEAR";
$lab =  (isset($actionlabel))? $actionlabel : uniqid();

$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1>Remove uploaded files</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="action" value="actioncleaning" />
        <input type="hidden" name="step" />
        <table id="tableToggle">
          <tr class="toggleable">
        <?php
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
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="Options" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
