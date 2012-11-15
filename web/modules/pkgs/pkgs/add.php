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

$p = new PageGenerator(_T("Add package", "pkgs"));
$p->setSideMenu($sidemenu);
$p->display();


if (isset($_POST['bconfirm'])) {
    $p_api_id = $_POST['p_api'];
    $random_dir = $_SESSION['random_dir'];
    $need_assign = True;
    $mode = $_POST['mode'];
    $level = 0;
    if ($mode == "creation") { $level = 1; }

    foreach (array('id', 'label', 'version', 'description', 'mode') as $post) {
        $package[$post] = $_POST[$post];
    }
    foreach (array('reboot') as $post) {
        $package[$post] = ($_POST[$post] == 'on' ? 1 : 0);
    }
    foreach (array('command') as $post) {
        $package[$post] = array('name'=>$_POST[$post.'name'], 'command'=>stripslashes($_POST[$post.'cmd']));
    }
    // Send Package Infos via XMLRPC
    $ret = putPackageDetail($p_api_id, $package, $need_assign);
    $pid = $ret[3]['id'];
    $plabel = $ret[3]['label'];
    $pversion = $ret[3]['version'];

    if (!isXMLRPCError() and $ret and $ret != -1) {
        if ($_POST['package-method'] == "upload") {
            $cbx = array($random_dir);
        }
        else if ($_POST['package-method'] == "package") {
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
                header("Location: " . urlStrRedirect("pkgs/pkgs/pending", array('location'=>base64_encode($p_api_id))));
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
}
else {
    // Get number of PackageApi
    $res = getUserPackageApi();

    // set first Package Api found as default Package API
    $p_api_id = $res[0]['uuid'];

    $list_val = $list = array();
    if (!isset($_SESSION['PACKAGEAPI'])) { $_SESSION['PACKAGEAPI'] = array(); }
    foreach ($res as $mirror) {
        $list_val[$mirror['uuid']] = $mirror['uuid'];
        $list[$mirror['uuid']] = $mirror['mountpoint'];
        $_SESSION['PACKAGEAPI'][$mirror['uuid']] = $mirror;
    }

    $selectpapi = new SelectItem('p_api');
    $selectpapi->setElements($list);
    $selectpapi->setElementsVal($list_val);

    $f = new ValidatingForm();
    $f->push(new Table());

    $r = new RadioTpl("package-method");
    $keys = $vals = array("package", "upload");
    $r->setValues($vals);
    $r->setChoices($keys);

    $f->add(new TrFormElement(_T("Select how you want to create packages", "pkgs"), $r), array());
    // Package API

    $f->add(
        new TrFormElement(_T("Package API", "pkgs"), $selectpapi),
        array("value" => $p_api_id, "required" => True)
    );

    $f->add(new TrFormElement(_T("Select the directory you want for this package", "pkgs"), new Div(array("id" => "package-temp-directory"))), array());
    $f->add(new HiddenTpl("mode"), array("value" => "creation", "hide" => True));

    // fields

    $fields = array(
        array("label", _T("Package label", "pkgs"), array("required" => True)),
        array("version", _T("Package version", "pkgs"), array("required" => True)),
        array('description', _T("Description", "pkgs"), array()),
    );

    $cmds = array(
        array('command', _T('Command\'s name : ', 'pkgs'), _T('Command : ', 'pkgs')),/*
        array('installInit', _T('installInit', 'pkgs'), _T('Install Init', 'pkgs')),
        array('preCommand', _T('preCommand', 'pkgs'), _T('Pre Command', 'pkgs')),
        array('postCommandFailure', _T('postCommandFailure', 'pkgs'), _T('postCommandFailure', 'pkgs')),
        array('postCommandSuccess', _T('postCommandSuccess', 'pkgs'), _T('postCommandSuccess', 'pkgs')) //*/
    );

    $options = array(
        array('reboot', _T('Need a reboot ?', 'pkgs'))
    );

    foreach ($fields as $p) {
        $f->add(
            new TrFormElement($p[1], new InputTpl($p[0])),
            array_merge(array("value" => $package[$p[0]]), $p[2])
        );
    }

    foreach ($options as $p) {
        $op = ($package[$p[0]] == 1 || $package[$p[0]] == '1' || $package[$p[0]] === 'enable');
        $f->add(
            new TrFormElement($p[1], new CheckboxTpl($p[0])),
            array("value" => ($op ? 'checked' : ''))
        );
    }

    foreach ($cmds as $p) {
        $f->add(
            new HiddenTpl($p[0].'name'),
            array("value" => $package[$p[0]]['name'], "hide" => True)
        );
        $f->add(
            new TrFormElement($p[2], new TextareaTpl($p[0].'cmd')),
            array("value" => htmlspecialchars($package[$p[0]]['command']))
        );
    }

    $f->pop();

    $f->addValidateButton("bconfirm", _T("Add", "pkgs"));
    $f->display();
}
?>

<script src="jsframework/lib/fileuploader.js" type="text/javascript"></script> <!-- js for file upload -->
<link href="jsframework/lib/fileuploader.css" rel="stylesheet" type="text/css"> <!-- css for file upload -->

<script type="text/javascript">
Event.observe(window, 'load', function() { // load this piece of code when page is loaded
    /*
     * Auto fill fields of form
     * if tempdir is empty (when changing packageAPI)
     * default tempdir will be chosen in ajaxGetSuggestedCommand
     * php file.
     */
    function fillForm(selectedPapi, tempdir) {
        url = '<?php echo urlStrRedirect("pkgs/pkgs/ajaxGetSuggestedCommand")?>&papiid=' + selectedPapi;
        if (tempdir != undefined) {
            url += '&tempdir=' + tempdir;
        }
        new Ajax.Request(url, {
            onSuccess: function(response) {
                $('label').value = response.headerJSON.label;
                $('version').value = response.headerJSON.version;
                $('commandcmd').value = response.headerJSON.commandcmd;
            }
        });
    }
    /*
     * Refresh Package API tempdir content
     * When called, display available packages
     * in package API tempdir
     */
    function refreshTempPapi() {
        var packageMethodValue= $$('input:checked[type="radio"][name="package-method"]').pluck('value');
        var box = $('p_api');
        var selectedIndex = box.selectedIndex;
        var selectedPapi = box.options[selectedIndex].value;
        if (packageMethodValue == "package") {
            new Ajax.Updater('package-temp-directory', '<?php echo urlStrRedirect("pkgs/pkgs/ajaxRefreshPackageTempDir") ?>&papi=' + selectedPapi, { 
                method: "get", 
                    evalScripts: true,
                    onComplete: fillForm(selectedPapi)
            });
        }
        else {
            new Ajax.Updater('package-temp-directory', '<?php echo urlStrRedirect("pkgs/pkgs/ajaxDisplayUploadForm") ?>&papi=' + selectedPapi, { 
                method: "get", 
                evalScripts: true
            });
            // reset form fields
            $('label').value = "";
            $('version').value = "";
            $('commandcmd').value = "";
        }
        
        return selectedPapi;
    }

    // on page load, display available temp packages
    var selectedPapi = refreshTempPapi();

    // When change Package API, update available temp packages
    $('p_api').observe('change', function() {
        selectedPapi = refreshTempPapi();
    });

    document.observe('click', function(event) {
        var elem = event.element();
        
        // display temp package or upload form
        // according to package-method chosen ("package" or "upload")
        if (elem.match('input[name="package-method"]')) {
            var selectedValue= $$('input:checked[type="radio"][name="package-method"]').pluck('value');
            if (selectedValue == "package") {
                selectedPapi = refreshTempPapi();
            }
            else if (selectedValue == "upload"){
                new Ajax.Updater('package-temp-directory', '<?php echo urlStrRedirect("pkgs/pkgs/ajaxDisplayUploadForm") ?>&papi=' + selectedPapi, { 
                    method: "get", 
                    evalScripts: true
                });
                // reset form fields
                $('label').value = "";
                $('version').value = "";
                $('commandcmd').value = "";
            }
        }
    });
});
</script>
