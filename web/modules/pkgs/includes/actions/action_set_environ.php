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

$environstr="key1 :: value1,\nkey2 :: value2";
if(isset($environ))
{
    $environstr = "";
    foreach($environ as $key=>$value)
    {
        $environstr .= $key.' :: '.$value.",\n";
    }
}

$environstr = trim($environstr,",\n\r");
?>

<div class="header">
    <h1>Set Environment variables</h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_set_environ" />
        <input type="hidden" name="step" />
            <table id="tableToggle">
                <tr class="toggleable">
                    <th width="16%">Step label : </th>
                    <th width="25%">
                        <?php echo'  <input type="text" name="actionlabel" value="'.$lab.'"/>'; ?>
                    </th>
                    <th></th>
                    <th></th>
                </tr>
                <tr>
                    <th width="16%">Environment variable</th>
                    <th width="25%">
                        <?php
                        echo'<textarea title="eg : key1 :: value1,'."\n".'key1 :: value1" style="width:206px;height: 50px;" name="environ" cols="5" rows="5">'.$environstr.'</textarea>';
                        ?>
                    </th>
                    <th></th>
                    <th></th>
                </tr>
            </table>
        <!-- All extra options are added here-->
    </div>
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="Options" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
