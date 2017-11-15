<?php
// descriptor
// {
//                 "action": "action_set_environ",
//                 "step": 0,
//                 "environ" : {"PLIP22" : "plop"  }
// }
?>
<?php
extract($_POST);
$lab =  (isset($actionlabel))? $actionlabel : uniqid();

$environstr="key1 :: value1,\nkey2 :: value2,";
if(isset($environ))
{
    $environstr = "";
    foreach($environ as $key=>$value)
    {
        $environstr .= $key.' :: '.$value.",\n";
    }
}
?>
<div class="header">
    <h1>Set Environ</h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_set_environ" />
        <input type="hidden" name="step" />
            <table>
                <tr>
                    <th width="16%">step label : </th>
                    <th width="25%">
                        <?php echo'  <input type="text" name="actionlabel" value="'.$lab.'"/>'; ?>
                    </th>
                    <th></th>
                    <th></th>
                </tr>
                <tr>
                    <th width="16%">json environ varaible</th>
                    <th width="25%">
                        <?php 
                        echo'<textarea title="eg : {\'PLIP22\' : \'plop\'}" style="width:206px;height: 50px;" name="environ" cols="5" rows="5">'.$environ.'</textarea>';
                        ?>
                    </th>
                    <th></th>
                    <th></th>
                </tr>
            </table>
        <!-- All extra options are added here-->
    </div>
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>
