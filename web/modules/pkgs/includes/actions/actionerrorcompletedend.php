<?php
require_once("../../../../includes/i18n.inc.php");
extract($_POST);
$lab = "END_ERROR";
?>
<div class="header">
    <h1><?php echo _T('End Error', 'pkgs'); ?></h1>
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
                    <th width="16%">'._T("Step label :","pkgs").'</th>
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
  <input  class="btn btn-primary" id="property" onclick='jQuery("#tableToggleend tr.toggleable").toggle();' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggleend tr.toggleable" ).hide();
    });
</script>
