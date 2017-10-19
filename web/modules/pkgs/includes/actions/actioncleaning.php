<div class="header">
    <h1>Clean</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="actionlabel" value="<?php echo (isset($_POST['actionlabel']))? $_POST['actionlabel'] : uniqid(); ?>"/>
        <input type="hidden" name="action" value="actioncleaning" />

        <!-- All extra options are added here-->
    </div>

    <input type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>