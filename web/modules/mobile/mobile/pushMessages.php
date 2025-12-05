<?php
require_once("modules/mobile/includes/xmlrpc.php");

$device_number = isset($_POST['device']) ? $_POST['device'] : (isset($_GET['device']) ? $_GET['device'] : "");
$message_filter = isset($_POST['message']) ? $_POST['message'] : (isset($_GET['message']) ? $_GET['message'] : "");
$status_filter = isset($_POST['status']) ? $_POST['status'] : (isset($_GET['status']) ? $_GET['status'] : "all messages");
$date_from = isset($_POST['date_from']) ? $_POST['date_from'] : (isset($_GET['date_from']) ? $_GET['date_from'] : "");
$date_to = isset($_POST['date_to']) ? $_POST['date_to'] : (isset($_GET['date_to']) ? $_GET['date_to'] : "");
$page_num = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$page_size = 50;

$messages = array();
$show_results = false;

if (true) {
    $show_results = true;
    
    // Convert dates to milliseconds
    $date_from_millis = null;
    $date_to_millis = null;
    
    if ($date_from) {
        $date_from_millis = strtotime($date_from) * 1000;
    }
    if ($date_to) {
        $date_to_millis = strtotime($date_to) * 1000;
    }
    
    $messages = xmlrpc_get_hmdm_push_messages($device_number, $message_filter, $status_filter,
                                        $date_from_millis, $date_to_millis, $page_size, $page_num);
}

?>

<h3><?php echo _T("Push Messages", "mobile"); ?></h3>
<p><?php echo _T("Search push messages and send new push messages to devices", "mobile"); ?></p>

<!-- <div style="margin-bottom: 20px;">
    <button onclick="toggleNewMessage()" class="btn"><?php echo _T("New message", "mobile"); ?></button>
</div>

<div id="new-message-form" style="display: none; margin-bottom: 20px; border: 1px solid #ccc; padding: 10px;">
    <h4><?php echo _T("Send New Message", "mobile"); ?></h4>
    <form method="post" action="">
        <table>
            <tr>
                <td><?php echo _T("Device", "mobile"); ?></td>
                <td>
                    <input type="text" name="new_device" required />
                </td>
            </tr>
            <tr>
                <td><?php echo _T("Message", "mobile"); ?></td>
                <td>
                    <textarea name="new_message" rows="4" cols="40" required></textarea>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <button type="submit" name="send_message" value="1"><?php echo _T("Send", "mobile"); ?></button>
                    <button type="button" onclick="toggleNewMessage()"><?php echo _T("Cancel", "mobile"); ?></button>
                </td>
            </tr>
        </table>
    </form>
</div>

<hr />

<h4><?php echo _T("Search Messages", "mobile"); ?></h4>

<form method="post" name="searchform">
    <table>
        <tr>
            <td><?php echo _T("Device", "mobile"); ?></td>
            <td>
                <input type="text" name="device" id="device" value="<?php echo htmlspecialchars($device_number); ?>" />
            </td>
        </tr>
        <tr>
            <td><?php echo _T("Message", "mobile"); ?></td>
            <td>
                <input type="text" name="message" id="message" value="<?php echo htmlspecialchars($message_filter); ?>" />
            </td>
        </tr>
        <tr>
            <td><?php echo _T("From", "mobile"); ?></td>
            <td>
                <input type="datetime-local" name="date_from" id="date_from" value="<?php echo htmlspecialchars($date_from); ?>" />
            </td>
        </tr>
        <tr>
            <td><?php echo _T("To", "mobile"); ?></td>
            <td>
                <input type="datetime-local" name="date_to" id="date_to" value="<?php echo htmlspecialchars($date_to); ?>" />
            </td>
        </tr>
        <tr>
            <td><?php echo _T("Status", "mobile"); ?></td>
            <td>
                <select name="status" id="status">
                    <option value="all messages" <?php echo $status_filter == "all messages" ? "selected" : ""; ?>><?php echo _T("All messages", "mobile"); ?></option>
                    <option value="sent" <?php echo $status_filter == "sent" ? "selected" : ""; ?>><?php echo _T("Sent", "mobile"); ?></option>
                    <option value="delivered" <?php echo $status_filter == "delivered" ? "selected" : ""; ?>><?php echo _T("Delivered", "mobile"); ?></option>
                    <option value="read" <?php echo $status_filter == "read" ? "selected" : ""; ?>><?php echo _T("Read", "mobile"); ?></option>
                </select>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <button type="submit" name="search" value="1"><?php echo _T("Search", "mobile"); ?></button>
            </td>
        </tr>
    </table>
</form> -->

<?php if ($show_results): ?>
    <?php if (is_array($messages) && count($messages) > 0): ?>
        <div id='messages-container' style="margin-top: 20px;">
            <table cellpadding="6" cellspacing="0" style="border: 1px solid; border-collapse: collapse; width: 100%;">
                <tr style="background-color: #dadadaff; ">
                    <th style="text-align:start;"><?php echo _T("Time", "mobile"); ?></th>
                    <th style="text-align:start;"><?php echo _T("Device", "mobile"); ?></th>
                    <th style="text-align:start;"><?php echo _T("Type", "mobile"); ?></th>
                    <th style="text-align:start;"><?php echo _T("Payload", "mobile"); ?></th>
                </tr>
                <?php foreach ($messages as $msg): ?>
                <tr>
                    <td><?php echo date("Y-m-d H:i:s", $msg['time']); ?></td>
                    <td><?php echo htmlspecialchars($msg['name']); ?></td>
                    <td><?php echo htmlspecialchars($msg['type']); ?></td>
                    <td><?php echo htmlspecialchars($msg['payload']); ?></td>
                </tr>
                <?php endforeach; ?>
            </table>
        </div>
    <?php else: ?>
        <div class="info-box" style="margin-top: 20px;">
            <?php echo _T("No messages found matching the criteria", "mobile"); ?>
        </div>
    <?php endif; ?>
<?php endif; ?>

<script type="text/javascript">
function toggleNewMessage() {
    var form = document.getElementById('new-message-form');
    if (form.style.display === 'none') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}
</script>

<?php
