<?php
require_once("modules/mobile/includes/xmlrpc.php");

$field = isset($_POST['field']) ? $_POST['field'] : (isset($_GET['field']) ? $_GET['field'] : "all");
$param = isset($_POST['param']) ? $_POST['param'] : (isset($_GET['param']) ? $_GET['param'] : "");
$page_num = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$page_size = 50;

$device_number = "";
$message_filter = "";

if ($field === "device") {
    $device_number = $param;
} else {
    // "all", "message", and "payload" map to text filter (backend handles matching)
    $message_filter = $param;
}

$messages = array();
$show_results = true;
$messages = xmlrpc_get_hmdm_push_messages($device_number, $message_filter, "",
                                    null, null, $page_size, $page_num);

?>

<h3><?php echo _T("Push Messages", "mobile"); ?></h3>
<p><?php echo _T("Search push messages and send new push messages to devices", "mobile"); ?></p>

<hr />

<h4><?php echo _T("Search Push Messages", "mobile"); ?></h4>
<div style="display:flex; justify-content:space-between; width:100%;">
    <form method="post" name="searchform" id="searchform" onsubmit="return false;">
        <div id="searchBest" style="width: 800px;">
            <span class="searchfield">
                <select class="searchfieldreal noborder" name="field" id="field" onchange="document.getElementById('searchform').submit();">
                    <option value="all" <?php echo $field === "all" ? "selected" : ""; ?>><?php echo _T("Search all fields", "mobile"); ?></option>
                    <option value="message" <?php echo $field === "message" ? "selected" : ""; ?>><?php echo _T("Type", "mobile"); ?></option>
                    <option value="payload" <?php echo $field === "payload" ? "selected" : ""; ?>><?php echo _T("Payload", "mobile"); ?></option>
                    <option value="device" <?php echo $field === "device" ? "selected" : ""; ?>><?php echo _T("Device", "mobile"); ?></option>
                </select>
            </span>

            <span style="width: 240px;">
                <input type="text" class="searchfieldreal" name="param" id="param" placeholder="<?php echo _T("Search...", "mobile"); ?>" value="<?php echo htmlspecialchars($param); ?>" onkeyup="if(event.keyCode===13){ document.getElementById('searchform').submit(); }" />
                <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'mobile'); ?>" onclick="document.getElementById('param').value=''; document.getElementById('searchform').submit();"></button>
            </span>

            <button type="submit" name="search" value="1" onclick="document.getElementById('searchform').submit(); return false;"><?php echo _T("Search", "mobile"); ?></button>
            <span class="loader" aria-hidden="true"></span>
        </div>
    </form>
    <div style="margin-bottom: 20px;">
        <a href="<?php echo urlStrRedirect("mobile/mobile/newPushMessage"); ?>" style="color: #fff" class="btnPrimary">
            <?php echo _T("New push message", "mobile"); ?>
        </a>
    </div>
</div>

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