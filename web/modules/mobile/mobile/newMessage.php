<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");
require_once("modules/imaging/includes/class_form.php");

$p = new PageGenerator(_T("Send New Message", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$device_keys = isset($_POST['device_keys']) && is_array($_POST['device_keys']) ? $_POST['device_keys'] : [];
$send_to_type = isset($_POST['send_to']) ? $_POST['send_to'] : "device";
$message_text = isset($_POST['message']) ? $_POST['message'] : "";
$device_number = isset($_POST['device_input']) ? $_POST['device_input'] : (isset($_GET['device']) ? $_GET['device'] : "");
$group_id = isset($_POST['group_input']) ? $_POST['group_input'] : (isset($_GET['group_id']) ? $_GET['group_id'] : "");
$configuration_id = isset($_POST['configuration_input']) ? $_POST['configuration_input'] : (isset($_GET['config_id']) ? $_GET['config_id'] : "");

if (isset($_GET['group_id']) && !empty($_GET['group_id']) && !isset($_POST['send_to'])) {
    $send_to_type = "group";
}
if (isset($_GET['config_id']) && !empty($_GET['config_id']) && !isset($_POST['send_to'])) {
    $send_to_type = "configuration";
}

$groups = xmlrpc_get_hmdm_groups();
$configurations = xmlrpc_get_hmdm_configurations();

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    $errors = array();
    
    if (empty($message_text)) {
        $errors[] = _T("Message text is required", "mobile");
    }

    if (!empty($device_keys)) {
        if (empty($errors)) {
            $successCount = 0;
            $failCount = 0;
            foreach ($device_keys as $key) {
                $parts = explode('##', $key, 2);
                $deviceNumber = $parts[0];
                if (empty($deviceNumber)) { $failCount++; continue; }
                $result = xmlrpc_send_hmdm_message('device', $deviceNumber, '', '', $message_text);
                if ($result && isset($result['status']) && $result['status'] === 'OK') {
                    $successCount++;
                } else {
                    $failCount++;
                }
            }
            if ($successCount > 0) {
                new NotifyWidgetSuccess(_T("Message sent successfully", "mobile"));
            } else {
                new NotifyWidgetFailure(_T("Failed to send message. Please try again.", "mobile"));
            }
            header("Location: " . urlStrRedirect("mobile/mobile/messaging"));
            exit;
        }
    } else {
        if ($send_to_type === "device" && empty($device_number)) {
            $errors[] = _T("Device is required", "mobile");
        } elseif ($send_to_type === "group" && empty($group_id)) {
            $errors[] = _T("Group is required", "mobile");
        } elseif ($send_to_type === "configuration" && empty($configuration_id)) {
            $errors[] = _T("Configuration is required", "mobile");
        }

        if (empty($errors)) {
            $dev_num = ($send_to_type === 'device') ? $device_number : '';
            $grp_id = ($send_to_type === 'group') ? $group_id : '';
            $cfg_id = ($send_to_type === 'configuration') ? $configuration_id : '';

            $result = xmlrpc_send_hmdm_message(
                $send_to_type,
                $dev_num,
                $grp_id,
                $cfg_id,
                $message_text
            );

            if ($result && isset($result['status']) && $result['status'] === 'OK') {
                new NotifyWidgetSuccess(_T("Message sent successfully", "mobile"));
                header("Location: " . urlStrRedirect("mobile/mobile/messaging"));
                exit;
            } else {
                $errors[] = _T("Failed to send message. Please try again.", "mobile");
            }
        }
    }
    
    if (!empty($errors)) {
        foreach ($errors as $error) {
            new NotifyWidgetFailure($error);
        }
    }
}

$form = new Form();
$form->push(new Table());

if (empty($device_keys)) {
    $sendToSelect = new SelectItem('send_to');
    $sendToSelect->setElements(array(
        _T('Device', 'mobile'),
        _T('Group', 'mobile'),
        _T('Configuration', 'mobile'),
        _T('All devices', 'mobile')
    ));
    $sendToSelect->setElementsVal(array('device', 'group', 'configuration', 'all_devices'));
    $sendToSelect->setSelected($send_to_type);
    $form->add(new TrFormElement(_T('Send to', 'mobile'), $sendToSelect));

    $deviceInput = new InputTpl('device_input', '/.+/', $device_number);
    $deviceRow = new TrFormElement(_T('Device', 'mobile'), $deviceInput);
    $deviceRow->setClass('row-device');
    $form->add($deviceRow);

    $groupElements = array(_T('Select a group', 'mobile'));
    $groupValues = array('');
    if (is_array($groups)) {
        foreach ($groups as $group) {
            $groupElements[] = htmlspecialchars($group['name']);
            $groupValues[] = (string)$group['id'];
        }
    }
    $groupSelect = new SelectItem('group_input');
    $groupSelect->setElements($groupElements);
    $groupSelect->setElementsVal($groupValues);
    $groupSelect->setSelected($group_id);
    $groupRow = new TrFormElement(_T('Group', 'mobile'), $groupSelect);
    $groupRow->setClass('row-group');
    $form->add($groupRow);

    $configElements = array(_T('Select a configuration', 'mobile'));
    $configValues = array('');
    if (is_array($configurations)) {
        foreach ($configurations as $config) {
            $configElements[] = htmlspecialchars($config['name']);
            $configValues[] = (string)$config['id'];
        }
    }
    $configSelect = new SelectItem('configuration_input');
    $configSelect->setElements($configElements);
    $configSelect->setElementsVal($configValues);
    $configSelect->setSelected($configuration_id);
    $configRow = new TrFormElement(_T('Configuration', 'mobile'), $configSelect);
    $configRow->setClass('row-configuration');
    $form->add($configRow);
} else {
    $indicatorSelect = new SelectItem('send_to_indicator');
    $indicatorSelect->setElements(array(sprintf(_T('Dynamic selection (%d device(s))', 'mobile'), count($device_keys))));
    $indicatorSelect->setElementsVal(array(''));
    $form->add(new TrFormElement(_T('Send to', 'mobile'), $indicatorSelect));
}

$messageArea = new TextareaTpl('message');
$messageArea->setRows(6);
$form->add(new TrFormElement(_T('Message', 'mobile'), $messageArea));

$form->addValidateButton('test', _T('Send', 'mobile'));

$form->pop();
$form->display();

?>

<?php if (!empty($device_keys)): ?>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var indicator = document.querySelector('select[name="send_to_indicator"]');
    if (indicator) {
        indicator.disabled = true;
        indicator.style.cssText += ';opacity:0.85;cursor:default;pointer-events:none;';
    }
    var f = document.querySelector('form');
    if (f) {
        var keys = <?php echo json_encode(array_values($device_keys)); ?>;
        keys.forEach(function(k) {
            var inp = document.createElement('input');
            inp.type = 'hidden';
            inp.name = 'device_keys[]';
            inp.value = k;
            f.appendChild(inp);
        });
    }
});
</script>
<?php endif; ?>

<script type="text/javascript">
    function updateSecondInput() {
        var sendTo = document.querySelector('select[name="send_to"]').value;
        var deviceRow = document.querySelector('.row-device');
        var groupRow = document.querySelector('.row-group');
        var configRow = document.querySelector('.row-configuration');
        
        if (deviceRow) deviceRow.style.display = 'none';
        if (groupRow) groupRow.style.display = 'none';
        if (configRow) configRow.style.display = 'none';
        
        if (sendTo === 'device' && deviceRow) {
            deviceRow.style.display = '';
        } else if (sendTo === 'group' && groupRow) {
            groupRow.style.display = '';
        } else if (sendTo === 'configuration' && configRow) {
            configRow.style.display = '';
        }
    }
    
    document.addEventListener('DOMContentLoaded', function() {
        var sendToSelect = document.querySelector('select[name="send_to"]');
        if (sendToSelect) {
            sendToSelect.addEventListener('change', updateSecondInput);
            updateSecondInput();
        }
        
        var deviceInput = document.getElementById('device_input');
        if (deviceInput) {
            var autocompleteTimeout;
            
            deviceInput.addEventListener('input', function(e) {
                clearTimeout(autocompleteTimeout);
                var query = e.target.value;
                var suggestionsList = document.getElementById('device-suggestions');
                
                if (!suggestionsList) {
                    suggestionsList = document.createElement('ul');
                    suggestionsList.id = 'device-suggestions';
                    suggestionsList.style.cssText = 'position: absolute; top: 100%; left: 0; width: 100%; max-height: 200px; overflow-y: auto; background: white; border: 1px solid #ccc; list-style: none; padding: 0; margin: 5px 0 0 0; display: none; z-index: 1000;';
                    var container = deviceInput.parentElement;
                    if (container) {
                        container.style.position = 'relative';
                        container.appendChild(suggestionsList);
                    }
                }
                
                if (query.length < 1) {
                    suggestionsList.style.display = 'none';
                    return;
                }
                
                autocompleteTimeout = setTimeout(function() {
                    fetch('<?php echo urlStrRedirect("mobile/mobile/ajaxDeviceSearch"); ?>&filter=' + encodeURIComponent(query))
                        .then(response => response.json())
                        .then(data => {
                            suggestionsList.innerHTML = '';
                            if (Array.isArray(data) && data.length > 0) {
                                data.forEach(function(device) {
                                    var li = document.createElement('li');
                                    li.style.padding = '8px 12px';
                                    li.style.cursor = 'pointer';
                                    li.style.borderBottom = '1px solid #eee';
                                    
                                    var deviceName = device.name || '';
                                    li.textContent = deviceName;
                                    li.title = deviceName;
                                    
                                    li.onmouseover = function() {
                                        li.style.backgroundColor = '#f0f0f0';
                                    };
                                    li.onmouseout = function() {
                                        li.style.backgroundColor = 'white';
                                    };
                                    
                                    li.onclick = function() {
                                        deviceInput.value = deviceName;
                                        suggestionsList.style.display = 'none';
                                    };
                                    
                                    suggestionsList.appendChild(li);
                                });
                                suggestionsList.style.display = 'block';
                            } else {
                                suggestionsList.style.display = 'none';
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            suggestionsList.style.display = 'none';
                        });
                }, 300);
            });
            
            document.addEventListener('click', function(e) {
                if (e.target !== deviceInput) {
                    var suggestions = document.getElementById('device-suggestions');
                    if (suggestions) {
                        suggestions.style.display = 'none';
                    }
                }
            });
        }

    });
</script>