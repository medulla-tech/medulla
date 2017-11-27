<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
extract($_POST);
?>
<div class="header">
    <h1>User Comment</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="action_comment" />
        <?php

        $lab =  (isset($actionlabel))? $actionlabel : uniqid();
        echo'
        <table>
            <tr>
                <th width="16%">step label : </th>
                <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>
                <th></th>
                <th></th>
            </tr>
            <tr>
             ';
            echo '<td width="16%">
                   User Comment
                </td>
                <td width="25%">
                <textarea name="comment" cols="5" rows="2">';
                echo (isset($comment)) ? $comment : "jid AMR : @@@JID_MASTER@@@[@@@IP_MASTER@@@]
jid ARS : @@@JID_RELAYSERVER@@@[@@@IP_RELAYSERVER@@@]
jid AM  : @@@JID_MACHINE@@@[@@@IP_MACHINE@@@]
nom du package : @@@PACKAGE_NAME@@@
session de deployement : @@@SESSION_ID@@@
hostname : @@@HOSTNAME@@@
python implentation : @@@PYTHON_IMPLEMENTATION@@@
architecture machine : @@@ARCHI_MACHINE@@@
os family : @@@OS_FAMILY@@@
os complet name :   @@@OS_COMPLET_NAME@@@
uuid package : @@@UUID_PACKAGE@@@
folder package : @@@PACKAGE_DIRECTORY_ABS_MACHINE@@@
list interface network :@@@LIST_INTERFACE_NET@@@
list adress mac : @@@LIST_MAC_ADRESS@@@
list ip adress : @@@LIST_IP_ADRESS@@@
ip xmpp machine : @@@IP_MACHINE_XMPP@@@
tmp dir machine : @@@TMP_DIR@@@
" ;
                echo '</textarea>';
                echo'
                </td>';
        echo '
        <td></td><td></td>
            </tr>
        </table>';
        ?>

    </div>

    <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>
