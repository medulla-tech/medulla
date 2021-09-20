<?php
require_once("../../../../includes/i18n.inc.php");
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
    <h1><?php echo _T('Set Environment variables', 'pkgs'); ?></h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_set_environ" />
        <input type="hidden" name="step" />
            <table id="tableToggle">
                <tr class="toggleable">
                    <th width="16%"><?php echo _T('Step label : ', 'pkgs'); ?></th>
                    <th width="25%">
                        <?php echo'  <input type="text" name="actionlabel" value="'.$lab.'"/>'; ?>
                    </th>
                    <th></th>
                    <th></th>
                </tr>
                <tr>
                    <th width="16%"><?php echo _T('Environment variable', 'pkgs') ?></th>
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
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
