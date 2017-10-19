<div class="header">
    <h1>Process script</h1>
</div>

<div class="content">

    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="actionlabel" value="<?php echo (isset($_POST['actionlabel']))? $_POST['actionlabel'] : uniqid(); ?>"/>
        <input type="hidden" name="action" value="actionprocessscript" />

        Command <textarea name="command" cols="5" rows="5"><?php echo (isset($_POST['command'])) ? $_POST['command'] : "" ;?></textarea>

        <!-- Option timeout -->
        <?php
        if(isset($_POST['timeout']))
        {
            echo '<p><input type="checkbox" checked onclick="if(jQuery(this).is(\':checked\')){jQuery(this).next().prop(\'disabled\',false);}else{jQuery(this).next().prop(\'disabled\',true);}" />Timeout <input type="number" min="0" value="'.$_POST['timeout'].'" name="timeout"  /></p>';
        }
        else{
            echo '<p><input type="checkbox" onclick="if(jQuery(this).is(\':checked\')){jQuery(this).next().prop(\'disabled\',false);}else{jQuery(this).next().prop(\'disabled\',true);}" />Timeout <input type="number" min="0" value="10" disabled name="timeout"  /></p>';
        }
        ?>

        <p><input type="checkbox" onclick="if(jQuery(this).is(':checked')){jQuery(this).next().prop('disabled',false);}else{jQuery(this).next().prop('disabled',true);}" />codereturn <input type="hidden" value="" disabled name="codereturn" /></p>
    </div>

    <input type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>
