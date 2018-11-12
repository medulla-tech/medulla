<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
extract($_POST);
$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1>Set config file parameter</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="action_set_config_file" />
        <?php
            $lab =  (isset($actionlabel))? $actionlabel : uniqid();
        ?>
        <table id="tableToggle">
        <?php

        $dataval = (isset($set)) ? $set : "add@__@agentconf.ini@__@global@__@log_level@__@INFO";

        echo'
           <tr class="toggleable">
                <th width="16%">Step label : </th>
                <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>
                <th></th>
                <th></th>
            </tr>
            <tr>
             ';
            echo '<td width="16%">
                   Config action description
                </td>
                <td width="25%">
                <input title="eg:
    add@__@agentconf.ini@__@global@__@log_level@__@INFO
    or
    del@__@agentconf.ini@__@global@__@log_level"
                type="text" name="set" value="'.$dataval.'"/>'
                ;
                echo'
                </td>';
        echo '
        <td></td><td></td>
            </tr>
      </table>';
        ?>

    </div>

    <input class="btn btn-primary"
           type="button"
           onclick="jQuery(this).parent().parent('li').detach()"
           value="Delete" />
    <input class="btn btn-primary"
           id="property"
           onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});'
           type="button"
           value="Options" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
