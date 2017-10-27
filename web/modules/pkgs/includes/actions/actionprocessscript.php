<?php 
extract($_POST);

// echo "<pre>";
// print_r($_POST );
// echo "</pre>";
?>
<div class="header">
    <h1>Run command</h1>
</div>
<div class="content">

    <div>
        <input type="hidden" name="action" value="actionprocessscript" />
        <input type="hidden" name="step" />
    <table>
        <tr>
            <th>step label:</th>
            <th><input id="laction" type="text" name="actionlabel" value="<?php echo (isset($actionlabel))? $actionlabel : uniqid(); ?>"/></th>
            <th rowspan="6">
                Command<br>
                <textarea name="command" cols="5" rows="5"><?php echo (isset($command)) ? $command : "" ;?></textarea></th>
        </tr>
        <tr>
            <?php
            if(isset($timeout))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />Timeout
                </td>
                <td>
                    <input " type="number" min="0" value="'.$timeout.'" name="timeout"  />
                </td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox" onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />Timeout
                </td>
                <td>
                    <input type="number" min="0" value="10" disabled name="timeout"  />
                </td>';
            }
            ?>
        </tr>
        <tr>
            <td>
            <input type="checkbox" <?php echo (isset($codereturn)) ? " checked " : " "; ?> onclick="if(jQuery(this).is(':checked')){
                    jQuery(this).next().prop('disabled',false);
                }
                else{
                    jQuery(this).next().prop('disabled',true);
                }" />codereturn
            <input type="hidden" value="" disabled name="codereturn" />
            </td>
            <td>

            </td>
        </tr>
        <tr>
            
            <?php
        $resultlist = array(array('label' => 'pas de result','value' => "noneresult"),
                            array('label' => 'the 10 first lines result','value' => "10@firstlines"),
                            array('label' => 'the 20 first lines','value' => "20@firstlines"),
                            array('label' => 'the 30 first lines','value' => "30@firstlines"),
                            array('label' => 'conplet result ','value' => "@resultcommand"),
                            array('label' => 'the 10 last lines result','value' => "10@lastlines"),
                            array('label' => 'the 20 last lines result','value' => "20@lastlines"),
                            array('label' => 'the 30 last lines result','value' => "30@lastlines"),
                            array('label' => 'the 2 last lines result','value' => "2@lastlines"),
                            array('label' => 'the last line result','value' => "1@lastlines"),
        );
        $posibleresultname = array( "noneresult",
                                    "10@firstlines",
                                    "20@firstlines",
                                    "30@firstlines",
                                    "@resultcommand",
                                    "10@lastlines",
                                    "20@lastlines",
                                    "30@lastlines",
                                    "2@lastlines",
                                    "1@lastlines"
        );
        $options = "";
        // search in $Post if input result
        foreach($_POST as $key=>$val){
            if (in_array($key, $posibleresultname)){
                $selectresult = $key;
                break;
            }
        }
//         if (!isset($selectresult)){
//             $selectresult = "noneresult";
//         }
        foreach($resultlist as $selectedbyuser)
        {
            if(isset($selectresult) && $selectedbyuser['value'] == $selectresult)
            {
                $options .= "<option value='".$selectedbyuser['value']."' selected>".$selectedbyuser['label']."</option>";
            }
            else
                $options .= "<option value='".$selectedbyuser['value']."'>".$selectedbyuser['label']."</option>";
        }

        if(isset($selectresult))// and $selectresult != "noneresult"
        {
            echo '
            <td>
                <input type="checkbox" checked onclick="if(jQuery(this).is(\':checked\')){
                                                            jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                                        }
                                                        else{
                                                            jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                                        }" />Result
            </td>
            <td> 
                <select id = "gggg" onchange="jQuery(this).attr(\'name\',jQuery(this).val());" name="'.$selectresult.'">'.$options.'</select>
            </td>';

        }
        else{
            echo '
            <td>
                <input type="checkbox" onclick="if(jQuery(this).is(\':checked\')){
                                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                                }
                                                else{
                                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                                }" />Result
            </td>
            <td>
            <select id = "gggg" onchange="jQuery(this).attr(\'name\',jQuery(this).val());"
                disabled name="'.$selectresult.'">'.$options.'</select>
            </td>';
        }
        ?>
        </tr>
        <tr>
            <td></td>
            <td></td>
        </tr>
        <tr>
            <td></td>
            <td></td>
        </tr>
    </table>
        <!-- Option timeout -->
    </div>

    <input type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>
