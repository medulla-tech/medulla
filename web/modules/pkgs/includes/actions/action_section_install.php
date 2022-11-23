<?php
// file modules/pkgs/includes/actions/action_section_install.php
require_once("../../../../includes/i18n.inc.php");
extract($_POST);
/*
    descriptor type
        {
            "step" : 8,
            "action": "action_section_install"
        }

    echo "<pre>";
        print_r( $_POST );
    echo "</pre>";
*/

?>
<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">inst_</div>
    <h1><?php echo _T('Install Section', 'pkgs'); ?></h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_section_install" />
        <input type="hidden" name="step" />
        <input id="laction" type="hidden" name="actionlabel" value="label_section_install"/>
    </div>
    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
