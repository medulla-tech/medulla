<?php
extract($_POST);
$lab = "END_ERROR";
?>
<div class="header">
    <h1>End Error</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="action" value="actionerrorcompletedend" />
        <input type="hidden" name="step" />
        <?php
            echo '<input type="hidden" name="actionlabel" value="'.$lab.'"/>';
        ?>

        <?php
        echo'
            <table id="tableToggleend">
                 <tr class="toggleable">
                    <th width="16%">Step label : </th>
                    <th width="25%">'.$lab.'
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
  <input  class="btn btn-primary" id="property" onclick='jQuery("#tableToggleend tr.toggleable").toggle();' type="button" value="Options" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggleend tr.toggleable" ).hide();
    });
</script>
