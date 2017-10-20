<div class="header">
    <h1>Go to package folder</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="actionlabel" value="<?php echo (isset($_POST['actionlabel']))? $_POST['actionlabel'] : uniqid(); ?>"/>
        <input type="hidden" name="action" value="action_pwd_package" />

        <?php
        if(isset($_POST['packageuuid']))
        {
            echo '<p><input type="checkbox" checked onclick="if(jQuery(this).is(\':checked\')){jQuery(this).next().prop(\'disabled\',false);}else{jQuery(this).next().prop(\'disabled\',true);}" />Package uuid <input type="text" value="'.$_POST['packageuuid'].'" name="packageuuid"  /></p>';
        }
        else{
            echo '<p><input type="checkbox" onclick="if(jQuery(this).is(\':checked\')){jQuery(this).next().prop(\'disabled\',false);}else{jQuery(this).next().prop(\'disabled\',true);}" />Package uuid <input type="text" value="" disabled name="packageuuid"  /></p>';
        }
        ?>

    </div>

    <input type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>
