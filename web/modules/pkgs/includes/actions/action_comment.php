<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");
extract($_POST);
$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1><?php echo _T("Add info in deployment log","pkgs"); ?></h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="action_comment" />
        <?php

        $lab =  (isset($actionlabel))? $actionlabel : uniqid();
        ?>
        <table id="tableToggle">
        <?php
        echo'
           <tr class="toggleable">
                <th width="16%">'._T("Step label :","pkgs").'</th>
                <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>
                <th></th>
                <th></th>
            </tr>
            <tr>
             ';
            echo '<td width="16%">
                   '._T("Information","pkgs").'
                </td>
                <td width="25%">
                <textarea name="comment" cols="5" rows="2">';

                echo (isset($comment)) ? $comment : _T("Your log comments !","pkgs");

    /*
                echo (isset($comment)) ? $comment : "JID AMR : @@@JID_MASTER@@@[@@@IP_MASTER@@@]
JID ARS : @@@JID_RELAYSERVER@@@[@@@IP_RELAYSERVER@@@]
JID AM  : @@@JID_MACHINE@@@[@@@IP_MACHINE@@@]
Package name : @@@PACKAGE_NAME@@@
Deployement session id : @@@SESSION_ID@@@
Hostname : @@@HOSTNAME@@@
Python implentation : @@@PYTHON_IMPLEMENTATION@@@
Machine architecture : @@@ARCHI_MACHINE@@@
OS family : @@@OS_FAMILY@@@
OS complete name :   @@@OS_COMPLET_NAME@@@
Package UUID : @@@UUID_PACKAGE@@@
Package folder : @@@PACKAGE_DIRECTORY_ABS_MACHINE@@@
List of network interfaces :@@@LIST_INTERFACE_NET@@@
List of MAC addresses : @@@LIST_MAC_ADRESS@@@
list of IP addresses : @@@LIST_IP_ADRESS@@@
Machine IP address connected to XMPP : @@@IP_MACHINE_XMPP@@@
Machine tmp folder : @@@TMP_DIR@@@
" ;*/
                echo '</textarea>';
                echo'
                </td>';
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
