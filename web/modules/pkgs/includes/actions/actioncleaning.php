<?php
extract($_POST);
//$lab = "PACKAGE_CLEAR";
$lab =  (isset($actionlabel))? $actionlabel : uniqid();
?>
<div class="header">
    <h1 style ="color:#FE642E">Remove uploaded files</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="action" value="actioncleaning" />
        <input type="hidden" name="step" />
        <?php
        echo'
            <table>
                <tr>
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
</div>
