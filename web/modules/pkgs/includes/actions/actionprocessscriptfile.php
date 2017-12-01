<?php

/*
    creation action actionprocessscriptfile
                "step": intnb,
                "action": "actionprocessscriptfile",
                "typescript": "",
                "script" :  "",
                "suffix" : "",
                "bang" : "",
                "codereturn": "",
                "timeout": 900,
                "error": 5,
                "success": 3,
                "@resultcommand": ""
*/
extract($_POST);
// echo "<pre>";
//     print_r( $os );
// echo "</pre>";
?>
<div class="header">
    <h1>Execute script</h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="actionprocessscriptfile" />
        <input type="hidden" name="step" />
        <input type="hidden" name="codereturn" value=""/>
    <table id="tableToggleactionprocessscriptfile">
        <tr class="toggleableactionprocessscriptfile">
            <th>Step label:</th>
            <th><input id="laction" type="text" name="actionlabel" value="<?php echo (isset($actionlabel))? $actionlabel : uniqid(); ?>"/></th>
        </tr>

    <?php
        echo '<tr class="toggleableactionprocessscriptfile">';
        $options = "";
        $boolselected = false;
        $selectedbyscript = array(
                                    array(
                                        "label" => 'Batch',
                                        "value" => "Batch"),
                                    array(
                                        "label" => 'Visual Basic Script (Windows)',
                                        "value" => "visualbasicscript"),
                                    array(
                                        "label" => 'Power Shell (Windows)',
                                        "value" => "powershell"),
                                    array(
                                        "label" => 'Korn Shell (Linux & macOS)',
                                        "value" => "unixKornshell"),
                                    array(
                                        "label" => 'C Shell (Linux & macOS)',
                                            "value" => "unixCshell")
        );

        foreach($selectedbyscript as $val)
        {
            if(isset($typescript) && $typescript == $val['value'])
            {
                $options .= "<option value='".$typescript."' selected>".$val['label']."</option>";
            }
            else
                $options .= "<option value='".$val['value']."'>".$val['label']."</option>";
        }


                echo '<th width="16%">
                    Script language
                </th>
                <th width="25%">
                    <select name="typescript">'.$options.'</select>
                </th>';
        echo "</tr>";
    ?>

        <tr>
            <th>Script</th>
            <th>
              <textarea name="script" cols="5" rows="5"><?php echo (isset($script)) ? $script : "" ;?></textarea>
            </th>
        </tr>

    <tr class="toggleableactionprocessscriptfile">
           <?php
            if(isset($suffix))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />Force suffix
                </td>
                <td>
                    <input  type="text"
                           title=\'The "Script language" property above applies a suffix to the script by default.
However, if the "Force suffix" property is set, the imposed suffix will be this one\'
                            value="'.$suffix.'"
                            name="suffix"  />
                </td><td></td><td></td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox"  onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />Force suffix
                </td>
                <td>
                    <input  type="text"
                            title=\'The "Script language" property above applies a suffix to the script by default.
 However, if the "Force suffix" property is set, the imposed suffix will be this one\'
                            value="" disabled
                            name="suffix"  />
                </td><td></td><td></td>';
            }
            ?>
        </tr>

      <tr class="toggleableactionprocessscriptfile">
           <?php
            if(isset($bang))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />Force hash-bang
                </td>
                <td>
                    <input  type="text"
                            title=\'The "Script language" property above applies a hash-bang to the script by default.
 However, if the "Force hash-bang" property is set, the imposed hash-bang will be this one\'
                            value="'.$bang.'"
                            name="bang"  />
                </td><td></td><td></td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox"  onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />Force hash-bang
                </td>
                <td>
                    <input  type="text"
                            title=\'The "Script language" property above applies a hash-bang to the script by default.
 However, if the "Force hash-bang" property is set, the imposed hash-bang will be this one\'
                            value="" disabled
                            name="bang"  />
                </td><td></td><td></td>';
            }
            ?>
        </tr>

    <?php
            echo "<tr class='toggleableactionprocessscriptfile'>";

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
                    }" />Set timeout
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
                    }" />Set timeout
                </td>
                <td>
                    <input type="number" min="0" value="10" disabled name="timeout"  />
                </td>';
            }
    ?>
        </tr>

    <tr>
    <?php
        $resultlist = array(
                            array('label' => '10 first lines of result','value' => "10@firstlines"),
                            array('label' => '20 first lines of result','value' => "20@firstlines"),
                            array('label' => '30 first lines of result','value' => "30@firstlines"),
                            array('label' => 'Complete results','value' => "@resultcommand"),
                            array('label' => '10 last lines of result','value' => "10@lastlines"),
                            array('label' => '20 last lines of result','value' => "20@lastlines"),
                            array('label' => '30 last lines of result','value' => "30@lastlines"),
                            array('label' => '20 last lines of result','value' => "2@lastlines"),
                            array('label' => 'The last line of result','value' => "1@lastlines"),
        );
        $posibleresultname = array(
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
        $boolselected = false;
        // search in $Post if input result
        foreach($_POST as $key=>$val){
            if (in_array($key, $posibleresultname)){
                $selectresult = $key;
                $boolselected = true;
                break;
            }
        }
        if (!isset($selectresult)){
            $selectresult = "1@lastlines";
        }

        foreach($resultlist as $selectedbyscript)
        {
            if(isset($selectresult) && $selectedbyscript['value'] == $selectresult)
            {
                $options .= "<option value='".$selectedbyscript['value']."' selected>".$selectedbyscript['label']."</option>";
            }
            else
                $options .= "<option value='".$selectedbyscript['value']."'>".$selectedbyscript['label']."</option>";
        }

        if($boolselected)// and $selectresult != "noneresult"
        {
            echo '
            <td>
                <input type="checkbox" checked onclick="if(jQuery(this).is(\':checked\')){
                                                            jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                                        }
                                                        else{
                                                            jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                                        }" />Return result
            </td>
            <td>
                <select  onchange="jQuery(this).attr(\'name\',jQuery(this).val());" name="'.$selectresult.'">'.$options.'</select>
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
                                                }" />Return result
            </td>
            <td>
            <select disabled onchange="jQuery(this).attr(\'name\',jQuery(this).val());"
                name="1@lastlines">'.$options.'</select>
            </td>';
        }
    ?>

        </tr>
        <tr class="toggleableactionprocessscriptfile">
           <?php
            if(isset($success))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />On success go to step
                </td>
                <td>
                    <input " type="text"  value="'.$success.'" name="success"  />
                </td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox"  onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />On success go to step
                </td>
                <td>
                    <input type="text" value="END_SUCCESS" disabled name="success"  />
                </td>';
            }
            ?>
        </tr>
        <tr class="toggleableactionprocessscriptfile">
            <?php
            if(isset($error))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />On error go to step
                </td>
                <td>
                    <input " type="text"  value="'.$error.'" name="error"  />
                </td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox"  onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />On error go to step
                </td>
                <td>
                    <input type="text" value="END_ERROR" disabled name="error"  />
                </td>';
            }
            ?>
        </tr>
    </table>
        <!-- Option timeout -->
    </div>

    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
    <input  class="btn btn-primary" id="property" onclick='jQuery("#tableToggleactionprocessscriptfile tr.toggleableactionprocessscriptfile").toggle();' type="button" value="Options" />
</div>
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggleactionprocessscriptfile tr.toggleableactionprocessscriptfile" ).hide();
    });
</script>
