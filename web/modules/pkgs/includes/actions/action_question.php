<?php
// file modules/pkgs/includes/actions/action_question.php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");

extract($_POST);

$message = (isset($message)) ? base64_decode($message) : "" ;
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
<!-- Style a modifier pour le title des boites de dialog -->
<style>
  [data-title]:hover:after {
    opacity: 1;
    transition: all 0.1s ease 0.5s;
    visibility: visible;
}
[data-title]:after {
    content: attr(data-title);
    background-color: #00FF00;
    color: #111;
    font-size: 100%;
    position: absolute;
    padding: 1px 5px 2px 5px;
    bottom: -1.6em;
    left: 10%;
    white-space: nowrap;
    box-shadow: 1px 1px 3px #222222;
    opacity: 0;
    border: 1px solid #111111;
    z-index: 99999;
    visibility: hidden;
}
[data-title] {
    position: relative;
}
.showText {text-decoration: none;}

      .showText:hover {position: relative;}

      .showText span {display: none;}

      .showText:hover span {
        border: #666 2px solid;
        padding: 5px 20px 5px 5px;
        display: block;
        z-index: 1000;
        background: #e3e3e3;
        left: 0px;
        margin: 15px;
        width: 200px;
        position: absolute;
        top: 15px;
        text-decoration: none;
		border-radius:100% 50%;
		text-align:center;
		box-shadow: 10px 10px 5px 0px rgba(0,0,0,0.75);}

</style>
<?php
$namestep=_T("Update Question","pkgs");
?>
<div class="header">
    <h1 data-title="<?php echo _T('This step allows you to submit 1 question to the user', 'pkgs'); ?>" ><?php echo $namestep; ?></h1>
</div>

<div class="content">


    <div>
        <input type="hidden" name="action" value="action_question" />
        <input type="hidden" name="step" />
        <input type="hidden" name="codereturn" value=""/>
    <table id="tableToggle">
        <tr class="toggleable">
            <th <?php echo 'data-title="'._T('define Step Label', 'pkgs').'"'; ?> ><?php echo _T('Step label: ', 'pkgs'); ?></th>
            <th <?php echo 'data-title="'._T('Cutomize or not step label', 'pkgs').'"'; ?> >
                <input id="laction" type="text" name="actionlabel" value="<?php echo $lab; ?>"/>
            </th>
        </tr>

        <tr>
            <th <?php echo 'data-title="'._T('Question Message for user', 'pkgs').'"'; ?> >
                    <?php echo _T('Message', 'pkgs'); ?>
            </th>
            <th>
                <span  data-title="<?php echo _T('input Message for user', 'pkgs'); ?>">
                    <textarea class="special_textarea" name="message" ><?php echo $message; ?></textarea>
                </span>
            </th>
        </tr>
        <!--input Positive reponse-->
        <tr>
           <?php
            $gotoyes = (isset($gotoyes)) ? $gotoyes : "";

            echo '<th data-title="'._T("On 1 positive answer jump to the step label","pkgs").'">';
            echo _T("If 'yes' go to step","pkgs").'</th>';
            echo '<td>';
           ?>
            <span  data-title="<?php echo _T('input step label', 'pkgs'); ?>">
            <?php echo'<input  type="text"  value="'.$gotoyes.'" name="gotoyes"  />'; ?>
            </span>

            <?php
            echo '</td>';
            ?>
        </tr>
        <!--input Negative reponse-->
        <tr>
           <?php
            $gotono = (isset($gotono)) ? $gotono : "";

            echo '<th data-title="'._T("On 1 negative answer jump to the step label","pkgs").'">';
            echo _T("If 'no' go to step","pkgs").'</th>';
            echo '<td>';
           ?>
            <span  data-title="<?php echo _T('input step label', 'pkgs'); ?>">
            <?php echo'<input  type="text"  value="'.$gotono.'" name="gotoyes"  />'; ?>
            </span>

            <?php
            echo '</td>';
            ?>
        </tr>
        <!--input no  user-->
        <tr>
           <?php
            $gotonouser = (isset($gotonouser)) ? $gotonouser : "";

            echo '<th data-title="'._T("direct jump to the step label if no user session exist on machine","pkgs").'">';
            echo _T("If 'no user' go to step","pkgs").'</th>';
            echo '<td>';
           ?>
            <span  data-title="<?php echo _T('input step label', 'pkgs'); ?>">
            <?php echo'<input  type="text"  value="'.$gotonouser.'" name="gotoyes"  />'; ?>
            </span>

            <?php
            echo '</td>';
            ?>
        </tr>
        <!--input timeout-->
        <tr>
           <?php
            $gototimeout = (isset($gototimeout)) ? $gototimeout : "";

            echo '<th data-title="'._T("direct jump to the step label if timeout","pkgs").'">';
            echo _T("If 'timeout' go to step","pkgs").'</th>';
            echo '<td>';
           ?>
            <span  data-title="<?php echo _T('input step label', 'pkgs'); ?>">
            <?php echo'<input  type="text"  value="'.$gototimeout.'" name="gotoyes"  />'; ?>
            </span>

            <?php
            echo '</td>';
            ?>
        </tr>
        <tr>
            <?php
            $textcasecoche=_T("customize time for timeout","pkgs");
            $textinputcasecoche=_T("chang time in secondes","pkgs");
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
                    }" />'.'<span data-title="'.$textcasecoche.'">'._T("Set timeout (in seconds)","pkgs").'
                </span></td>
                <td>'.'<span data-title="'.$textinputcasecoche.'">'.
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
                <td>
                    <input type="number" min="0" value="800"  name="timeout"  />
                </td>';
            }
            ?>
        </tr>
    </table>
        <!-- Option timeout -->
    </div>
    <span  data-title="<?php echo _T('Delete this step label', 'pkgs').' '.$namestep ; ?>">
    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
    </span>
     <span  data-title="<?php echo _T('Paraneter this step label', 'pkgs').' '.$namestep ; ?>">
    <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
    </span>
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
