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

require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");
require_once("../../../../includes/utils.inc.php");

extract($_POST);
$gotoreturncode = [];

// Get centralize all the goto-return codes into $gotoreturncode variable
$boperators = ["==", "=", "!=",  "!", "<>", "<", "<=", ">", ">=", "IN", "OUT", "in", "out"];

// hydratation : utilisation des données de $_POST pour l'hydratation.
foreach($_POST as $key => $value){
    if(preg_match("#^gotoreturncode#", $key)){
        // $rawCode = "@5" or "@<=6" (extracted from gotoreturncode@5 or gotoreturncode@<=5)
        $rawCode = explode('@', $key)[1];
        $found=[];
        $code = NULL;

        // check on all operators
        foreach($boperators as $op){
            $found = [];
            preg_match("#^".$op."#", $rawCode, $found);
            $code = $rawCode;
        }

        // Here if $code is NULL, it means the operator has not been found, we parse the $code as usual.
        if($code == NULL){
            // Cette récupération marche pour des codes de type int, mais comme on inclus l'opérateur, ça ne fonctionnait pas
            $code = intval(explode('@', $key)[1]);
        }

        $gotoreturncode[] = ["code"=>htmlentities($code), "label"=>htmlentities($value)];
    }
}
    $command = (isset($command)) ? base64_decode($command) : "" ;

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
    <!-- definie prefixe label -->
    <div style="display:none;">script_</div>
    <h1 class="action"><?php echo _T('Run command', 'pkgs'); ?></h1>
</div>
<div class="content">

    <div>
        <input type="hidden" name="action" value="actionprocessscript" />
        <input type="hidden" name="step" />
        <input type="hidden" name="codereturn" value=""/>
    <table id="tableToggle">
        <tr class="toggleable">
            <th><?php echo _T('Step label: ', 'pkgs'); ?></th>
            <th><input id="laction" type="text" name="actionlabel" value="<?php echo $lab; ?>"/></th>
        </tr>
        <tr>
            <th><?php echo _T('Command', 'pkgs'); ?></th>
            <th>
                <textarea class="special_textarea" name="command" ><?php echo $command; ?></textarea>
            </th>
        </tr>

        <?php
          echo '<tr class="toggleable">';
            if(isset($packageuuid))
            {
                echo '<td width="16%">
                    <input type="checkbox" checked
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                }" />'._T("Alternate package","pkgs").'
                </td>
                <td width="25%">
                    <select name="packageuuid">'.$options.'</select>
                </td>';
            }
            else{
                echo '<td width="16%">
                    <input type="checkbox"
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                }" />'._T("Alternate package","pkgs").'
                    </td>
                    <td width="25%">
                        <select disabled name="packageuuid">'.$options.'</select>
                    </td>';
            }
        echo '
        <td></td><td></td>
            </tr>';
        ?>


        <tr class="toggleable">
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
                    }" />'._T("Set timeout (in seconds)","pkgs").'
                </td>
                <td>
                    <input " type="number" min="0" value="'.$timeout.'" name="timeout"  />
                </td>';
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
        <tr>
            <?php
        $resultlist = array(
                            array('label' => _T('10 first lines of result','pkgs'),'value' => "10@firstlines"),
                            array('label' => _T('20 first lines of result','pkgs'),'value' => "20@firstlines"),
                            array('label' => _T('30 first lines of result','pkgs'),'value' => "30@firstlines"),
                            array('label' => _T('Complete results (limited to 10000 last characters)','pkgs'),'value' => "@resultcommand"),
                            array('label' => _T('10 last lines of result','pkgs'),'value' => "10@lastlines"),
                            array('label' => _T('20 last lines of result','pkgs'),'value' => "20@lastlines"),
                            array('label' => _T('30 last lines of result','pkgs'),'value' => "30@lastlines"),
                            array('label' => _T('20 last lines of result','pkgs'),'value' => "2@lastlines"),
                            array('label' => _T('The last line of result','pkgs'),'value' => "1@lastlines"),
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
        if($_POST['os']){
            $boolselected = true;
        }
        // search in $Post if input result
        foreach($_POST as $key=>$val){
            if (in_array($key, $posibleresultname)){
                $selectresult = $key;
                $boolselected = true;
                break;
            }
        }
        if (!isset($selectresult)){
            $selectresult = "10@lastlines";
        }

        foreach($resultlist as $selectedbyuser)
        {
            if(isset($selectresult) && $selectedbyuser['value'] == $selectresult)
            {
                $options .= "<option value='".$selectedbyuser['value']."' selected>".$selectedbyuser['label']."</option>";
            }
            else
                $options .= "<option value='".$selectedbyuser['value']."'>".$selectedbyuser['label']."</option>";
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
                                                        }" />'._T("Return result","pkgs").'
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
                                                }" />'._T("Return result","pkgs").'
            </td>
            <td>
            <select disabled onchange="jQuery(this).attr(\'name\',jQuery(this).val());"
                name="10@lastlines">'.$options.'</select>
            </td>';
        }
        ?>
        </tr>
        <tr class="toggleable">
           <?php
            /*
            // DO NOT REMOVE : if we want to remove the gotoreturn system and rollback to the end success/error system

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
                    }" />'._T("On success go to step","pkgs").'
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
                    }" />'._T("On success go to step","pkgs").'
                </td>
                <td>
                    <input type="text" value="END_SUCCESS" disabled name="success"  />
                </td>';
            }
            */
            ?>
        </tr>
        <tr class="toggleable">
            <?php
            /*
            // DO NOT REMOVE : if we want to remove the gotoreturn system and rollback to the end success/error system

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
                    }" />'._T("On error go to step","pkgs").'
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
                    }" />'._T("On error go to step","pkgs").'
                </td>
                <td>
                    <input type="text" value="END_ERROR" enabled name="error"  />
                </td>';
            }
            */
            ?>

             <?php
           $gotoTitle = _T(
"Branch if true.\n" .
"Comparison operators:\n" .
"n1 → branch if return code equals n1 (equivalent to ==n1 by default);\n" .
"==n1, =n1 → branch if return code equals n1;\n" .
"!=n1, !n1, <>n1 → branch if return code is different from n1;\n" .
"<n1 → branch if return code is less than n1;\n" .
">n1 → branch if return code is greater than n1;\n" .
"<=n1 → branch if return code is less than or equal to n1;\n" .
">=n1 → branch if return code is greater than or equal to n1;\n" .
"\n" .
"Interval operators:\n" .
"INn1,n2 → branch if return code is inside the interval from n1 to n2 (inclusive);\n" .
"OUTn1,n2 → branch if return code is outside the interval from n1 to n2;\n" .
"\n" .
"Notes:\n" .
"- Interval values are separated by a comma (,).\n" .
"- n1 and n2 can be negative numbers.\n" .
"- IN and OUT are case-insensitive (e.g., in1,5 or out-5,5 are valid).\n" .
"- The order of conditions is important: the first matching condition triggers the branch.\n" .
"- If no condition matches and the return code equals 0 → branch to END_SUCCESS.\n" .
"- If no condition matches and no automatic success applies, the sequence proceeds to the next step.\n",
"pkgs");

?>



        </tr>
        <tr class="toggleable">
          <td  width="100%">
            <input type="checkbox" checked onclick="if(jQuery(this).is(':checked')){
              jQuery(this).next('.add-goto').attr('disabled', false);
              jQuery(this).parent().find('.goto-on-return-section').show();
              jQuery(this).parent().find('.goto-on-return-section input[name=\'gotoreturncode\']').not('.ignore').attr('disabled', false);
            }
            else{
              jQuery(this).next('.add-goto').attr('disabled', true);
              jQuery(this).parent().find('.goto-on-return-section').hide();
              jQuery(this).parent().find('.goto-on-return-section input[name=\'gotoreturncode\']').not('.ignore').attr('disabled', true);
            }"/><?php echo _T("On return code, goto ","pkgs");?>
            <input type="button" class="add-goto btn btn-primary" class="add-goto" value="<?php echo _T("Add goto","pkgs");?>"
            onclick="jQuery(this).parent().find('.goto-on-return-section').append('<div class=\'goto-on-return\'>Return Code <input type=\'text\' name=\'gotoreturncode\'/> Goto Label <input type=\'text\' name=\'gotolabel\'/><input type=\'button\' value=\'Delete\' onclick=\'jQuery(this).parent().remove()\'/></div>')"/>
            <div class="goto-on-return-section">
              <?php
              if(safeCount($gotoreturncode) > 0){
                foreach($gotoreturncode as $row){?>
                  <div class='goto-on-return'>Return Code <input type='text' title='<?php echo htmlspecialchars($gotoTitle); ?>' name='gotoreturncode' value='<?php echo $row['code'];?>'/> Goto Label <input type='text' name='gotolabel' value="<?php echo $row['label'];?>"/><input type='button' value='Delete' onclick='jQuery(this).parent().remove()'/></div>
                <?php }
              }
              else{
                ?>
                <div class='goto-on-return'>Return Code <input type='text' title='<?php echo htmlspecialchars($gotoTitle); ?>' name='gotoreturncode' value='!=0'/> Goto Label <input type='text' name='gotolabel' value="END_ERROR"/><input type='button' value='Delete' onclick='jQuery(this).parent().remove()'/></div>
                <?php
              }
              ?>
            </div>
          </td>
        </tr>
    </table>
        <!-- Option timeout -->
    </div>

    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
    <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
