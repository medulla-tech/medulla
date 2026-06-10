<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$profile_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$is_create  = ($profile_id === 0);

if (isset($_POST['bsave'])) {
    $name        = trim($_POST['profile_name'] ?? '');
    $filter_mode = in_array($_POST['filter_mode'] ?? '', ['BLOCKLIST', 'ALLOWLIST'])
                   ? $_POST['filter_mode'] : 'BLOCKLIST';
    $enabled     = ($_POST['profile_enabled'] ?? '1') === '1';

    $ok = false;
    if ($name === '') {
        new NotifyWidgetFailure(_T("Profile name is required", "mobile"));
    } elseif ($is_create) {
        $result = xmlrpc_create_netfilter_profile($name, $filter_mode);
        if ($result && isset($result['id'])) {
            $profile_id = intval($result['id']);
            // apply enabled state if different from default
            if (!$enabled) {
                xmlrpc_update_netfilter_profile($profile_id, $name, $filter_mode, $enabled);
            }
            $ok = true;
        } else {
            new NotifyWidgetFailure(_T("Failed to create profile", "mobile"));
        }
    } else {
        $ok = xmlrpc_update_netfilter_profile($profile_id, $name, $filter_mode, $enabled);
        if (!$ok) {
            new NotifyWidgetFailure(_T("Failed to save profile", "mobile"));
        }
    }

    if ($ok) {
        $config_ids = isset($_POST['selected_configs']) ? array_map('intval', (array)$_POST['selected_configs']) : [];
        xmlrpc_set_netfilter_profile_configs($profile_id, $config_ids);
        new NotifyWidgetSuccess($is_create ? _T("Profile created", "mobile") : _T("Profile saved", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/netfilterProfiles"));
        exit;
    }
}

$profile = [];
if (!$is_create) {
    $profiles = xmlrpc_get_netfilter_profiles();
    if (is_array($profiles)) {
        foreach ($profiles as $pr) {
            if ((int)($pr['id'] ?? 0) === $profile_id) {
                $profile = $pr;
                break;
            }
        }
    }
    if (!$profile) {
        new NotifyWidgetFailure(_T("Profile not found", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/netfilterProfiles"));
        exit;
    }

    $assigned_ids = xmlrpc_get_netfilter_profile_configs($profile_id);
    if (!is_array($assigned_ids)) $assigned_ids = [];
    $assigned_ids = array_map('intval', $assigned_ids);
} else {
    $assigned_ids = [];
}

$all_configs = xmlrpc_get_hmdm_configurations();
if (!is_array($all_configs)) $all_configs = [];

$assigned_set = array_flip($assigned_ids);

$page_title = $is_create
    ? _T("Create Filter Profile", "mobile")
    : sprintf(_T("Edit Profile: %s", "mobile"), htmlspecialchars($profile['name'] ?? ''));

$p = new PageGenerator($page_title);
$p->setSideMenu($sidemenu);
$p->display();

$availableOptions = '';
$assignedOptions  = '';
foreach ($all_configs as $cfg) {
    $cid   = (int)($cfg['id'] ?? 0);
    $cname = htmlspecialchars($cfg['name'] ?? '');
    $opt   = '<option value="' . $cid . '">' . $cname . '</option>';
    if (isset($assigned_set[$cid])) {
        $assignedOptions .= $opt;
    } else {
        $availableOptions .= $opt;
    }
}

$f = new ValidatingForm();
$f->push(new Table());

// Section: Profile settings
$f->add(new TrFormElement("", new SpanElement(_T("Profile settings", "mobile"), "pkgs-title")));

// Name
$nameInput = new InputTpl("profile_name");
$f->add(
    new TrFormElement(_T("Name", "mobile"), $nameInput),
    ["value" => $profile['name'] ?? '', "required" => true]
);

// Filter mode
$filterSelect = new SelectItem("filter_mode");
$filterSelect->setElements([
    _T("Blocklist (block listed domains)", "mobile"),
    _T("Allowlist (only allow listed domains)", "mobile"),
]);
$filterSelect->setElementsVal(["BLOCKLIST", "ALLOWLIST"]);
$f->add(
    new TrFormElement(_T("Filter mode", "mobile"), $filterSelect),
    ["value" => $profile['filterMode'] ?? 'BLOCKLIST']
);

// Status (radio)
$enabledRadio = new RadioTpl("profile_enabled");
$enabledRadio->setChoices([_T("Activated", "mobile"), _T("Deactivated", "mobile")]);
$enabledRadio->setvalues(['1', '0']);
$enabledRadio->setSelected(isset($profile['enabled']) && !$profile['enabled'] ? '0' : '1');
$f->add(new TrFormElement(_T("Status", "mobile"), $enabledRadio, ['class' => 'radio-inline']));

// Section: Configurations
$f->add(new TrFormElement("", new SpanElement(_T("Assigned configurations", "mobile"), "pkgs-title")));

// Deps widget
$depsHtml = '
<div id="nfp-grouplist" class="deps-widget">
    <div class="deps-col deps-available">
        <h3>' . _T('Available configurations', 'mobile') . '</h3>
        <input type="text" id="nfpConfigFilter" class="deps-search" value=""
               placeholder="' . _T('Search by name...', 'mobile') . '">
        <select multiple class="deps-list" id="nfp_available">
            ' . $availableOptions . '
        </select>
    </div>
    <div class="deps-actions">
        <span class="deps-arrow-right" onclick="nfpMoveRight()"></span>
        <span class="deps-arrow-left"  onclick="nfpMoveLeft()"></span>
    </div>
    <div class="deps-col deps-added">
        <h3>' . _T('Assigned configurations', 'mobile') . '</h3>
        <select multiple class="deps-list" name="selected_configs[]" id="nfp_selected">
            ' . $assignedOptions . '
        </select>
    </div>
</div>';

$f->add(new TrFormElement("", new SpanElement($depsHtml, "mobile")));

$f->pop();
$btn_label = $is_create ? _T("Create profile", "mobile") : _T("Save", "mobile");
$f->addValidateButton("bsave", $btn_label);
$f->display();
?>
<input type="button" class="btnSecondary" style="margin-left:8px;" value="<?php echo _T("Cancel", "mobile"); ?>" onclick="location.href='<?php echo urlStrRedirect("mobile/mobile/netfilterProfiles"); ?>';" />
<?php
?>

<script type="text/javascript">
function nfpMoveRight() {
    jQuery('#nfp_available option:selected').each(function() {
        jQuery('#nfp_selected').append(jQuery(this).clone());
        jQuery(this).remove();
    });
}
function nfpMoveLeft() {
    jQuery('#nfp_selected option:selected').each(function() {
        jQuery('#nfp_available').append(jQuery(this).clone());
        jQuery(this).remove();
    });
}

jQuery(function() {
    var filterInput = jQuery('#nfpConfigFilter');
    var opts        = jQuery('#nfp_available option');

    filterInput.on('input', function() {
        var q = filterInput.val().toLowerCase();
        opts.each(function() {
            jQuery(this).toggle(!q || jQuery(this).text().toLowerCase().indexOf(q) !== -1);
        });
    });

    // Select all in the assigned list before submit so every option is posted
    jQuery('form').on('submit', function() {
        jQuery('#nfp_selected option').prop('selected', true);
    });
});
</script>
