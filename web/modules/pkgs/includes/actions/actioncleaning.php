<div class="header">
    <h1>Clean</h1>
</div>

<form class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="actioncleaning" />
    </div>
    <div>
        <!-- All extra options are added here-->
    </div>

    <input type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</form>