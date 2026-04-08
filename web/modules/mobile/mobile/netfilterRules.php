<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Network Filter Rules", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_POST['add_domain']) && !empty($_POST['domain'])) {
    $domain = trim($_POST['domain']);
    $rule_type = in_array($_POST['rule_type'] ?? '', ['BLOCK', 'ALLOW']) ? $_POST['rule_type'] : 'BLOCK';
    $result = xmlrpc_add_netfilter_rule($domain, $rule_type);
    if ($result) {
        new NotifyWidgetSuccess(_T("Rule added", "mobile"));
    } else {
        new NotifyWidgetFailure(_T("Failed to add rule", "mobile"));
    }
}
?>

<p>
    <?php echo _T("Manage domain filter rules. Use", "mobile"); ?>
    <code>*.domain.com</code>
    <?php echo _T("to match all subdomains.", "mobile"); ?>
    &nbsp;&nbsp;<a href="<?php echo urlStrRedirect("mobile/mobile/netfilterSettings"); ?>">&larr; <?php echo _T("Settings", "mobile"); ?></a>
</p>

<form method="post" style="margin: 10px 0 20px 0;">
    <table>
        <tr>
            <td><input type="text" name="domain" placeholder="<?php echo _T("e.g. youtube.com or *.tiktok.com", "mobile"); ?>" style="width: 280px;"></td>
            <td style="padding-left: 8px;">
                <select name="rule_type">
                    <option value="BLOCK"><?php echo _T("BLOCK", "mobile"); ?></option>
                    <option value="ALLOW"><?php echo _T("ALLOW", "mobile"); ?></option>
                </select>
            </td>
            <td style="padding-left: 8px;">
                <input type="submit" name="add_domain" class="btn btn-small btn-primary" value="<?php echo _T("Add rule", "mobile"); ?>">
            </td>
        </tr>
    </table>
</form>

<?php
$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxNetfilterRules"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
