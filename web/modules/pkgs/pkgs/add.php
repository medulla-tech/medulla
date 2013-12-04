<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/pkgs/includes/functions.php");
require_once("modules/pkgs/includes/query.php");

$p = new PageGenerator(_T("Add package", "pkgs"));
$p->setSideMenu($sidemenu);
$p->display();

// This session variable is used for auto-check upload button
// @see ajaxrefreshPackageTempdir.php
$_SESSION['pkgs-add-reloaded'] = array();

if (isset($_POST['bconfirm'])) {
    $p_api_id = $_POST['p_api'];
    $random_dir = $_SESSION['random_dir'];
    $need_assign = True;
    $mode = $_POST['mode'];
    $level = 0;
    if ($mode == "creation") {
        $level = 1;
    }

    foreach (array('id', 'label', 'version', 'description', 'mode', 'Qvendor', 'Qsoftware', 
            'Qversion', 'boolcnd', 'licenses') as $post) {
        $package[$post] = $_POST[$post];
    }
    foreach (array('reboot', 'associateinventory') as $post) {
        $package[$post] = ($_POST[$post] == 'on' ? 1 : 0);
    }
    // Package command
    $package['command'] = array('name' => $_POST['commandname'], 'command' => $_POST['commandcmd']);

    // Send Package Infos via XMLRPC
    $ret = putPackageDetail($p_api_id, $package, $need_assign);
    $pid = $ret[3]['id'];
    $plabel = $ret[3]['label'];
    $pversion = $ret[3]['version'];

    if (!isXMLRPCError() and $ret and $ret != -1) {
        if ($_POST['package-method'] == "upload") {
            $cbx = array($random_dir);
        } else if ($_POST['package-method'] == "package") {
            $cbx = array();
            foreach ($_POST as $post => $v) {
                if (preg_match("/cbx_/", $post) > 0) {
                    $cbx[] = preg_replace("/cbx_/", "", $post);
                }
            }
            if (isset($_POST['rdo_files'])) {
                $cbx[] = $_POST['rdo_files'];
            }
        }
        $ret = associatePackages($p_api_id, $pid, $cbx, $level);
        if (!isXMLRPCError() and is_array($ret)) {
            if ($ret[0]) {
                $explain = '';
                if (count($ret) > 1) {
                    $explain = sprintf(" : <br/>%s", implode("<br/>", $ret[1]));
                }
                new NotifyWidgetSuccess(sprintf(_T("Files successfully associated with package <b>%s (%s)</b>%s", "pkgs"), $plabel, $pversion, $explain));
                header("Location: " . urlStrRedirect("pkgs/pkgs/pending", array('location' => base64_encode($p_api_id))));
                exit;
            } else {
                $reason = '';
                if (count($ret) > 1) {
                    $reason = sprintf(" : <br/>%s", $ret[1]);
                }
                new NotifyWidgetFailure(sprintf(_T("Failed to associate files%s", "pkgs"), $reason));
            }
        } else {
            new NotifyWidgetFailure(_T("Failed to associate files", "pkgs"));
        }
    }
} else {
    // Get number of PackageApi
    $res = getUserPackageApi();

    // set first Package Api found as default Package API
    $p_api_id = $res[0]['uuid'];

    $list_val = $list = array();
    if (!isset($_SESSION['PACKAGEAPI'])) {
        $_SESSION['PACKAGEAPI'] = array();
    }
    foreach ($res as $mirror) {
        $list_val[$mirror['uuid']] = $mirror['uuid'];
        $list[$mirror['uuid']] = $mirror['mountpoint'];
        $_SESSION['PACKAGEAPI'][$mirror['uuid']] = $mirror;
    }

    $span = new SpanElement(_T("Choose package source", "pkgs"), "pkgs-title");

    $selectpapi = new SelectItem('p_api');
    $selectpapi->setElements($list);
    $selectpapi->setElementsVal($list_val);

    $f = new ValidatingForm();
    $f->push(new Table());

    // Step title
    $f->add(new TrFormElement("", $span), array());

    $r = new RadioTpl("package-method");
    $vals = array("package", "upload", "empty");
    $keys = array(_T("Already uploaded on the server", "pkgs"), _T("Upload from this web page", "pkgs"), _T("Make an empty package", "pkgs"));
    $r->setValues($vals);
    $r->setChoices($keys);

    // Package API
    $f->add(
            new TrFormElement("<div id=\"p_api_label\">" . _T("Package API", "pkgs") . "</div>", $selectpapi), array("value" => $p_api_id, "required" => True)
    );

    $f->add(new TrFormElement(_T("Package source", "pkgs"), $r), array());
    $f->add(new TrFormElement("<div id='directory-label'>" . _T("Files directory", "pkgs") . "</div>", new Div(array("id" => "package-temp-directory"))), array());
    $f->add(new HiddenTpl("mode"), array("value" => "creation", "hide" => True));

    $span = new SpanElement(_T("Package Creation", "pkgs"), "pkgs-title");
    $f->add(new TrFormElement("", $span), array());

    // fields

    $fields = array(
        array("label", _T("Name", "pkgs"), array("required" => True, 'placeholder' => _T('<fill_package_name>', 'pkgs'))),
        array("version", _T("Version", "pkgs"), array("required" => True)),
        array('description', _T("Description", "pkgs"), array()),
    );

    $command = _T('Command:', 'pkgs') . '<br /><br />';
    $commandHelper = '<span>' . _T('Pulse will try to figure out how to install the uploaded files.\n\n
If the detection fails, it doesn\'t mean that the application cannot be installed using Pulse but that you\'ll have to figure out the proper command.\n\n
Many vendors (Acrobat, Flash, Skype) provide a MSI version of their applications which can be processed automatically by Pulse.\n
You may also ask Google for the silent installation switches. If you\'re feeling lucky, here is a Google search that may help:\n\n
<a href="@@GOOGLE_SEARCH_URL@@">Google search</a>', 'pkgs') . '</span>';
    $command = $command . str_replace('\n', '<br />', $commandHelper);
    $cmds = array(
        array('command', _T('Command\'s name : ', 'pkgs'), $command), /*
              array('installInit', _T('installInit', 'pkgs'), _T('Install Init', 'pkgs')),
              array('preCommand', _T('preCommand', 'pkgs'), _T('Pre Command', 'pkgs')),
              array('postCommandFailure', _T('postCommandFailure', 'pkgs'), _T('postCommandFailure', 'pkgs')),
              array('postCommandSuccess', _T('postCommandSuccess', 'pkgs'), _T('postCommandSuccess', 'pkgs')) // */
    );

    $options = array(
        array('reboot', _T('Need a reboot ?', 'pkgs'))
    );

    foreach ($fields as $p) {
        $f->add(
                new TrFormElement($p[1], new InputTpl($p[0])), array_merge(array("value" => ''), $p[2])
        );
    }

    foreach ($options as $p) {
        $f->add(
                new TrFormElement($p[1], new CheckboxTpl($p[0])), array("value" => '')
        );
    }
    foreach ($cmds as $p) {
        $f->add(
                new HiddenTpl($p[0] . 'name'), array("value" => '', "hide" => True)
        );
        $f->add(
                new TrFormElement($p[2], new TextareaTpl($p[0] . 'cmd')), array("value" => '')
        );
    }

    foreach (array('Qvendor', 'Qsoftware', 'Qversion') as $k) {
        if (!isset($package[$k])) {
            $package[$k] = '';
        }
    }
    addQuerySection($f, $package);
    /* =================   BEGIN LICENSE   ===================== */
    $f->add(new TrFormElement(_T('Number of licenses', 'pkgs'), new InputTpl('licenses')),
            array("value" => '')
    );
    /* ==================   END LICENSE   ====================== */
    
    $f->pop();

    $f->addValidateButton("bconfirm", _T("Add", "pkgs"));
    $f->display();
}
?>

<script src="modules/pkgs/lib/fileuploader/fileuploader.js"
    type="text/javascript"></script>
<!-- js for file upload -->
<link href="modules/pkgs/lib/fileuploader/fileuploader.css"
    rel="stylesheet" type="text/css">
<!-- css for file upload -->

<script type="text/javascript">
    jQuery(function() { // load this piece of code when page is loaded
        jQuery('.label span a').each(function() {
            jQuery(this).attr('href', 'http://www.google.com/#q=file.exe+silent+install');
            jQuery(this).attr('target', '_blank');
            return false; // break the loop
        });
        /*
         * Auto fill fields of form
         * if tempdir is empty (when changing packageAPI)
         * default tempdir will be chosen in ajaxGetSuggestedCommand
         * php file.
         */
        function fillForm(selectedPapi, tempdir) {
            url = '<?php echo urlStrRedirect("pkgs/pkgs/ajaxGetSuggestedCommand") ?>&papiid=' + selectedPapi;
            if (tempdir != undefined) {
                url += '&tempdir=' + tempdir;
            }

            jQuery.ajax({
                'url': url,
                type: 'get',
                success: function(data) {
                    jQuery('#version').val(data.version);
                    jQuery('#commandcmd').val(data.commandcmd);
                }
            });
        }
        /*
         * Refresh Package API tempdir content
         * When called, display available packages
         * in package API tempdir
         */
        function refreshTempPapi() {
            var packageMethodValue = jQuery('input:checked[type="radio"][name="package-method"]').val();
            var selectedPapi = jQuery("#p_api").val();
            if (packageMethodValue == "package") {
                /*new Ajax.Updater('package-temp-directory', '<?php echo urlStrRedirect("pkgs/pkgs/ajaxRefreshPackageTempDir") ?>&papi=' + selectedPapi, {
                 method: "get",
                 evalScripts: true,
                 onComplete: fillForm(selectedPapi)
                 });*/

                jQuery('#package-temp-directory').load('<?php echo urlStrRedirect("pkgs/pkgs/ajaxRefreshPackageTempDir") ?>&papi=' + selectedPapi, function() {
                    fillForm(selectedPapi);
                });

            }
            else {
                /*new Ajax.Updater('package-temp-directory', '<?php echo urlStrRedirect("pkgs/pkgs/ajaxDisplayUploadForm") ?>&papi=' + selectedPapi, {
                 method: "get",
                 evalScripts: true
                 });*/

                jQuery('#package-temp-directory').load('<?php echo urlStrRedirect("pkgs/pkgs/ajaxDisplayUploadForm") ?>&papi=' + selectedPapi);

                // reset form fields
                jQuery('#version').val("");
                jQuery('#commandcmd').val("");
            }

            return selectedPapi;
        }

        // on page load, display available temp packages
        var selectedPapi = refreshTempPapi();

        // When change Package API, update available temp packages
        jQuery('#p_api').change(function() {
            selectedPapi = refreshTempPapi();
        });


        jQuery('input[name="package-method"]').click(function() {

            // display temp package or upload form
            // according to package-method chosen ("package" or "upload")
            var selectedValue = jQuery('input:checked[type="radio"][name="package-method"]').val();
            if (selectedValue == "package") {
                selectedPapi = refreshTempPapi();
                jQuery('#directory-label').html("<?php echo _T("Files directory", "pkgs") ?>");
                jQuery('#directory-label').parent().parent().fadeIn();
            }
            else if (selectedValue == "empty") {
                var jcArray = new Array('label', 'version', 'description', 'commandcmd');
                for (var dummy in jcArray) {
                    try {
                        jQuery('#' + jcArray[dummy]).css("background", "#FFF");
                        jQuery('#' + jcArray[dummy]).removeAttr('disabled'); // TODO: Check if no error here
                    }
                    catch (err) {
                        // this php file is prototype ajax request with evalscript
                        // enabled.
                    }
                }
                jQuery('#directory-label').parent().parent().fadeOut();
            }
            else if (selectedValue == "upload") {
                jQuery('#package-temp-directory').load('<?php echo urlStrRedirect("pkgs/pkgs/ajaxDisplayUploadForm") ?>&papi=' + selectedPapi);
                // reset form fields
                jQuery('#version').val("");
                jQuery('#commandcmd').val("");
                jQuery('#directory-label').html("<?php echo sprintf(_T("Files upload (<b><u title='%s'>%sM max</u></b>)", "pkgs"), _T("Change post_max_size and upload_max_filesize directives in php.ini file to increase upload size.", "pkgs"), get_php_max_upload_size()) ?>");
                jQuery('#directory-label').parent().parent().fadeIn();
            }

        });

        // Set easySuggest on software field with the new ajax url
        jQuery('#Qvendor').focusout(window.completeQsoftware);

    });
<?php
// if one package API, hide field
if (count($list) < 2) {
    echo <<< EOT
            // Hide package api field
            jQuery('#p_api').parents('tr:first').hide();
EOT;
}
?>
</script>
