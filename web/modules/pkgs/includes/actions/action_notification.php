<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");

extract($_POST);
//     if( base64_decode($message, true) != false){
//                         $message = base64_decode($message);
//     }
    $message = (isset($message)) ? base64_decode($message) : "" ;
    $titlemessage= (isset($message)) ? base64_decode($message) : "" ;
        $packageList = xmpp_packages_list();
        $options = "";

        foreach($packageList as $id=>$package)
        {
            if(isset($packageuuid) && $packageuuid == $package['uuid'])
            {
                $options .= "<option value='".$package['uuid']."' selected>".$package['name']."</option>";
            }
            else
                $options .= "<option value='".$package['uuid']."'>".$package['name']."</option>";
        }
$lab =  (isset($actionlabel))? $actionlabel : uniqid();
?>
<div class="header">
    <h1 data-title="<?php echo _T('Send a notification to the connected user', 'pkgs'); ?>"><?php echo _T('User Notification', 'pkgs'); ?></h1>
</div>
<div class="content">

    <div>
        <input type="hidden" name="action" value="action_notification" />
        <input type="hidden" name="step" />
        <input type="hidden" name="codereturn" value=""/>
    <table id="tableToggle">
        <tr class="toggleable">
            <th><?php echo _T('Step label: ', 'pkgs'); ?></th>
            <th><input id="laction" type="text" name="actionlabel" value="<?php echo $lab; ?>"/>
            </th>
        </tr>




         <?php
            $sizeheader = (isset($sizeheader)) ? $sizeheader : 15;
            $sizemessage = (isset($sizemessage)) ? $sizemessage : 10;
        ?>
        <tr>
            <th>
                    <?php echo _T('Message box title', 'pkgs'); ?>
            </th>
            <th>
                <span  data-title="<?php echo _T('Insert title of message box', 'pkgs'); ?>">
                    <textarea class="special_textarea" name="titlemessage" ><?php echo $titlemessage; ?></textarea>
                </span>
                <span  data-title="<?php echo _T('Define text size for message box title', 'pkgs'); ?>">
                    <?php echo _T('Text size', 'pkgs'); ?>
                    <?php echo'<input style="width:35px;" type="number"  value="'.$sizeheader.'" name="sizeheader" min=10 max=20 />'; ?>
                </span>
            </th>
        </tr>
        <tr>
            <th>
                    <?php echo _T('Message', 'pkgs'); ?>
            </th>
            <th>
                <span  data-title="<?php echo _T('Insert message for user', 'pkgs'); ?>">
                    <textarea class="special_textarea" name="message" ><?php echo $message; ?></textarea>
                </span>
                 <span  data-title="<?php echo _T('Define text size for message', 'pkgs'); ?>">
                    <?php echo _T('Text size', 'pkgs'); ?>
                    <?php echo'<input style="width:35px;" type="number"  value="'.$sizemessage.'" name="sizemessage" min=7 max=15 />'; ?>
                </span>
            </th>
        </tr>

        <tr>
          <?php
            $textbuttonyes = (isset($textbuttonyes)) ? $textbuttonyes : "OK";

            echo '<th>';
            echo _T("True button text","pkgs").'</th>';
            echo '<th>';
           ?>
             <span  data-title="<?php echo _T('Define text to be shown on button returning True', 'pkgs'); ?>">
            <?php echo'<input  type="text"  value="'.$textbuttonyes.'" name="textbuttonyes"  />'; ?>
            </span>
            <?php
            echo '</th>';
            ?>
        </tr>


        <tr class="toggleable">
            <?php
            $textinputcasecoche=_T("Set maximum time waiting for a response","pkgs");
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
                    }" />'._T("Set timeout (in seconds)","pkgs").'
                </td>
                <td><span data-title="'.$textinputcasecoche.'">'.
                    '<input " type="number" min="0" value="'.$timeout.'" name="timeout"  />
                </span></td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />'._T("Set timeout (in seconds)","pkgs").'
                </td>
                <td><span data-title="'.$textinputcasecoche.'">'.
                    '<input type="number" min="0" value="800"  name="timeout"  />
                </td>';
            }
            ?>
        </tr>
        <tr>

        </tr>


    </table>
        <!-- Option timeout -->
    </div>

    <span  data-title="<?php echo _T('Delete this step', 'pkgs'); ?>">
    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
    </span>
    <span  data-title="<?php echo _T('Show additional options for this step', 'pkgs'); ?>">
    <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
    </span>
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
