<?php
extract($_POST);
$lab = "END_ERROR";
// $lab =  (isset($actionlabel))? $actionlabel : uniqid();
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
            <table>
                <tr>
                    <th width="16%">step label : </th>
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

</div>
