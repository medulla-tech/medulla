<?php
/**
 * (c) 2016-2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net/
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */
// file : modules/pkgs/includes/actions/action_loop_question.php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");

extract($_POST);
    $titlemessage = (isset($titlemessage)) ? base64_decode($titlemessage) : "" ;
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
$namestep=_T("User Postpone Options","pkgs");
?>

<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">loop_</div>
    <h1 class="action" data-title="<?php echo _T('Allow the connected user to postpone an action', 'pkgs'); ?>"><?php echo $namestep; ?></h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_loop_question" />
        <input type="hidden" name="step" />
        <input type="hidden" name="codereturn" value=""/>
    <table id="tableToggle">
        <tr class="toggleable">
            <th><?php echo _T('Step label: ', 'pkgs'); ?></th>
            <th><input id="laction" type="text" name="actionlabel" value="<?php echo $lab; ?>"/></th>
        </tr>
                <?php
            $sizeheader = (isset($sizeheader)) ? $sizeheader : 15;
            $sizemessage = (isset($sizemessage)) ? $sizemessage : 10;
        ?>
        <tr>
            <th><?php echo _T('Message box title', 'pkgs'); ?></th>
            <th>
                <span data-title="<?php echo _T('Insert title of message box', 'pkgs'); ?>">
                    <textarea class="special_textarea" name="titlemessage"><?php echo $titlemessage; ?></textarea>
                </span>
            </th>
        </tr>
        <tr>
            <th>
                <span data-title="<?php echo _T('Define text size for message box title', 'pkgs'); ?>">
                    <?php echo _T('Text size', 'pkgs'); ?>
                </span>
            </th>
            <th><?php echo'<input type="number" value="'.$sizeheader.'" name="sizeheader" min=10 max=20 />'; ?></th>
        </tr>
        <tr>
            <th><?php echo _T('Question', 'pkgs'); ?></th>
            <th>
                <span data-title="<?php echo _T('Insert question for user', 'pkgs'); ?>">
                    <textarea class="special_textarea" name="message"><?php echo $message; ?></textarea>
                </span>
            </th>
        </tr>
        <tr>
            <th>
                <span data-title="<?php echo _T('Define text size for question', 'pkgs'); ?>">
                    <?php echo _T('Text size', 'pkgs'); ?>
                </span>
            </th>
            <th><?php echo'<input type="number" value="'.$sizemessage.'" name="sizemessage" min=7 max=15 />'; ?></th>
        </tr>
  <tr>
          <?php
            $textbuttonyes = (isset($textbuttonyes)) ? $textbuttonyes : "Yes";

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

        <tr>
          <?php
            $textbuttonno = (isset($textbuttonno)) ? $textbuttonno : "No";
            echo '<th>';
            echo _T("False button text","pkgs").'</th>';
            echo '<th>';
           ?>
             <span  data-title="<?php echo _T('Define text to be shown on button returning False', 'pkgs'); ?>">
            <?php echo'<input  type="text"  value="'.$textbuttonno.'" name="textbuttonno"  />'; ?>
            </span>
            <?php
            echo '</th>';
            ?>
        </tr>
        <tr>
           <?php
            $gotoyes = (isset($gotoyes)) ? $gotoyes : "";
            echo '
            <th>'._T("If 'True' go to step","pkgs").'</th>
            <td>';
            ?>
             <span  data-title="<?php echo _T('Define step label if user response is True', 'pkgs'); ?>">
             <?php echo'<input  style="width:80px;" type="text"  value="'.$gotoyes.'" name="gotoyes"  />'; ?>
             </span>
             </td>
        </tr>

        <tr>
            <?php
            $gotolookterminate = (isset($gotolookterminate)) ? $gotolookterminate : "";

            echo '
            <th>'._T("If 'Max Postponements Reached' go to step","pkgs").'</th>
            <td>';
            ?>
             <span  data-title="<?php echo _T('Define step label if the maximum number of postponements reached', 'pkgs'); ?>">
             <?php echo'<input  style="width:80px;" type="text"  value="'.$gotolookterminate.'" name="gotolookterminate"  />'; ?>
             </span>
             </td>
        </tr>

        <tr>
            <?php
            $gotonouser = (isset($gotonouser)) ? $gotonouser : "";

            echo '<th>';
            echo _T("If 'No User' go to step","pkgs").'</th>';
            echo '<td>';
            ?>
            <span  data-title="<?php echo _T('Define step label if no user is connected', 'pkgs'); ?>">
            <?php echo'<input  style="width:80px;" type="text"  value="'.$gotonouser.'" name="gotonouser"  />'; ?>
            </span>

            <?php
            echo '</td>';
            ?>
        </tr>
        <tr>
            <?php
            $gototimeout = (isset($gototimeout)) ? $gototimeout : "";

            echo '<th>';
            echo _T("If 'Timeout' go to step","pkgs").'</th>';
            echo '<td>';
            ?>
            <span  data-title="<?php echo _T('Define step label if no response is given before the timeout', 'pkgs'); ?>">
            <?php echo'<input  style="width:80px;" type="text"  value="'.$gototimeout.'" name="gototimeout"  />'; ?>
            </span>

            <?php
            echo '</td>';
            ?>
        </tr>
        <tr>
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

       <?php
            $loopnumber = (isset($loopnumber)) ? $loopnumber : 1;
            echo '<tr class="toggleable">';
            echo '<td>'._T("Maximum allowed postponements","pkgs").'</td>';
            echo '<td>';
        ?>
            <span  data-title="<?php echo _T('Define the maximum number of times a user can postpone the question', 'pkgs'); ?>">
         <?php
             echo '<input type="number" min="1" value="'.$loopnumber.'" name="loopnumber"  />
            </span></td>';
            echo '</tr>';
        ?>
        <?php
            $timeloop = (isset($timeloop)) ? $timeloop : 900;
            echo '<tr class="toggleable">';
            echo '<td>'._T("Interval","pkgs").'</td>';
            echo '<td>'; ?>

            <span  data-title="<?php echo _T('Define the interval between two questions to the user', 'pkgs'); ?>">
         <?php
             echo '<input type="number" min="1" value="'.$timeloop.'" name="timeloop"  />
            </span></td>';
            echo '</tr>';
        ?>
    </table>
        <!-- Option timeout -->
    </div>

    <span  data-title="<?php echo _T('Delete this step', 'pkgs').' '.$namestep ; ?>">
     <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs"); ?>" />
    </span>

     <span  data-title="<?php echo _T('Show additional options for this step', 'pkgs').' '.$namestep ; ?>">
     <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
    </span>
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
