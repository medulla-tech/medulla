<?php
extract($_POST);
/*
    descriptor type
        {
            "step" : 8,
            "action": "action_section_launch"
        }

    echo "<pre>";
        print_r( $_POST );
    echo "</pre>";
*/

?>
<div class="header">
    <h1>Launch Section</h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_section_launch" />
        <input type="hidden" name="step" />
        <input id="laction" type="hidden" name="actionlabel" value="label_section_launch"/>
    </div>
    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
