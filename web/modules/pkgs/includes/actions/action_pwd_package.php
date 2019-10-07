<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");
extract($_POST);
$tableToggle =  "tableToggle".uniqid();
$toggleable  =  "toggleable".uniqid();
$idclass     =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1><?php echo _T('Go to package folder', 'pkgs'); ?></h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="action_pwd_package" />
        <?php
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
        <table id="tableToggle">
        <?php

        echo '<tr class="toggleable">';
        echo'
                <th width="16%">'._T("Step label :","pkgs").'</th>
                <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>
                <th></th>
                <th></th>
            </tr>
             ';
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
            </tr>
        </table>';
        ?>

    </div>

    <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
    <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
