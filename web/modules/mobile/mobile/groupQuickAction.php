<?php
require_once("modules/mobile/includes/xmlrpc.php");

$groupId = isset($_GET['group_id']) ? intval($_GET['group_id']) : 0;

if ($groupId <= 0) {
    echo "<p style='color: red; text-align: center;'>" . _T("Invalid group ID", "mobile") . "</p>";
    exit;
}

// group info
$groups = xmlrpc_get_hmdm_groups();
$group = null;
foreach ($groups as $g) {
    if (isset($g['id']) && $g['id'] == $groupId) {
        $group = $g;
        break;
    }
}

if (!$group) {
    echo "<p style='color: red; text-align: center;'>" . _T("Group not found", "mobile") . "</p>";
    exit;
}

$groupName = $group['name'] ?? _T("Unknown", "mobile");
?>
<style type="text/css">
    .popup{
        width : 500px
    }

    td img {
        transition: filter 0.3s ease;
    }

    td img:hover {
        filter: brightness(50%);
        cursor: pointer;
    }
</style>

    <div style="width : 600px;">
        <?
        echo "<h1>"._T("Quick Actions", "mobile")."</h1>";
        echo "<h2>"._T("Group", "mobile")." : ".$groupName."</h2>";
        ?>
        <table style="width : 500px;">
            <tr>
            <?
                    echo sprintf("<td id='sync0' align='center' title='%s'><img src='modules/updates/graph/navbar/updates.svg' height='70' width='70'></td>", _T("Click here to update configuration", "mobile"));
                ?>
            </tr>
                <tr>
                <?
                    echo '<td id="sync" align="center">'._T("Update Config", "mobile")."</td>";
                ?>
            </tr>
            </table>
            <?php
                echo "<table>";
                    echo '<tr>';
                    echo '<td>'._T("Custom command", "mobile").'</td>
                    <td>
                        <select id="select">';
                        echo '<option value="custom">'._T("Custom", "mobile").'</option>';
                        echo'</select>
                    </td>
                    <td><input id="buttoncmd" class="btn btn-primary" type=button value="'._T("Send custom command", "mobile").'"></td>';
                    echo '</tr>';
                    echo '<tr id="custom-type-row">';
                    echo '<td>'._T("Message type", "mobile").'</td>';
                    echo '<td colspan="2"><input type="text" id="custom-type" style="width: 100%;" placeholder="'._T("Enter custom message type", "mobile").'"></td>';
                    echo '</tr>';
                    echo '<tr>';
                    echo '<td>'._T("Payload", "mobile").'</td>';
                    echo '<td colspan="2"><textarea id="payload" rows="4" style="width: 100%; font-family: monospace;" placeholder="'._T("Enter JSON payload (optional)", "mobile").'"></textarea></td>';
                    echo '</tr>';
                echo "</table>";
             ?>
    </div>
<script type="text/javascript">
    
    var groupId = <?php echo $groupId; ?>;
    
    function submitAction(action, messageType, payload) {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '<?php echo urlStrRedirect("mobile/mobile/groupQuickActionExec"); ?>';
        
        var fields = {
            'group_id': groupId,
            'action': action,
            'message_type': messageType,
            'payload': payload
        };
        
        for (var key in fields) {
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = fields[key];
            form.appendChild(input);
        }
        
        document.body.appendChild(form);
        form.submit();
    }
   
    jQuery(function() {
        jQuery('#sync0, #sync').on('click', function(){
            submitAction('configUpdated', 'configUpdated', '');
        });
        
        // custom Command
        jQuery('#buttoncmd').click(function() {
            var customType = jQuery('#custom-type').val().trim();
            var payload = jQuery('#payload').val();
            
            if (customType === '') {
                alert('<?php echo _T("Please enter a custom message type.", "mobile"); ?>');
                return;
            }
            
            submitAction('custom', customType, payload);
        });
    });

</script>
