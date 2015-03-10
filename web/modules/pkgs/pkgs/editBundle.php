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
require_once("modules/pkgs/includes/html.inc.php");
require_once("modules/pkgs/includes/query.php");
require_once("modules/msc/includes/package_api.php");
require_once("modules/msc/includes/utilities.php");



// ==================================================================================
// Receiving POST DATA
// ==================================================================================


if (isset($_POST['bconfirm'])){
    
    // Adding or editing
    
    $package = array(
        'label' => $_POST['label'],
        'description' => $_POST['description'],
        'version' => $_POST['version'],
        'sub_packages' => array(),
        'boolcnd' => '',
        'Qsoftware' => '',
        'Qversion' => '',
        'Qvendor' => '',
        'command' => array('command' => '', 'name' => ''),
        'licenses' => '',
        'id' => ''
    );
    
    // Edition mode
    if (isset($_POST['pid']))
        $package['id'] = $_POST['pid'];
    else
        // Creation mode
        $package['mode'] = 'creation';
        
    
    $package['reboot'] = empty($_POST['do_reboot']) ? '0' : 1;
    $package['associateinventory'] = empty($_POST['do_associateinventory']) ? '0' : 1;
        
    for ($i = 0 ; $i < count($_POST['sub_packages']['pids']); $i++){
        $pid = $_POST['sub_packages']['pids'][$i];
        $condition = $_POST['sub_packages']['conditions'][$i];
        
        $package['sub_packages'][] = array(
            'pid' => $pid,
            'condition' => $condition
        );
        
    }
    
    putPackageDetail($_POST['p_api'], $package, True);
    if (!isXMLRPCError()) {
        new NotifyWidgetSuccess(_T("Bundle successfully edited", "pkgs"));
    }
}



// ==================================================================================

// Add or Edit
if (!empty($_GET['p_api']))
    $p = new PageGenerator(_T("Edit bundle", "pkgs"));
else 
    $p = new PageGenerator(_T("Add bundle", "pkgs"));
    

$p->setSideMenu($sidemenu);
$p->display();

// display an edit config form 
$f = new ValidatingForm();
$f->push(new Table());

// Package API

$papis = getUserPackageApi();
$papis_by_uuid = array();


$list_val = $list = array();

if (!isset($_SESSION['PACKAGEAPI'])) {
    $_SESSION['PACKAGEAPI'] = array();
}
    
foreach ($papis as $mirror) {
    $list_val[$mirror['uuid']] = $mirror['uuid'];
    $list[$mirror['uuid']] = $mirror['mountpoint'];
    $_SESSION['PACKAGEAPI'][$mirror['uuid']] = $mirror;
    
    $papis_by_uuid[$mirror['uuid']] = $mirror;
}

// Edition mode
if (isset($_GET['p_api'], $_GET['pid'])){
    $p_api = base64_decode($_GET['p_api']);
    $pid = base64_decode($_GET['pid']);
    
    $package = getPackageDetail($p_api, $pid);
    
    $f->add(new HiddenTpl("p_api"), array(
        "value" => $p_api,
        "hide" => True));
    
    $f->add(new HiddenTpl("pid"), array(
        "value" => $pid,
        "hide" => True));
    
    
    $papi = $papis_by_uuid[$p_api];
}
else{
  
  
    $selectpapi = new SelectItem('p_api');
    $selectpapi->setElements($list);
    $selectpapi->setElementsVal($list_val);
    
    $papi = $papis[0];
    
    $f->add(
        new TrFormElement(_T('Package respository','pkgs'), $selectpapi),
        array("value" => "","required" => True)
    );
    
}


$papi_packages = advGetAllPackages(array(
            'filter' => '',
            'bundle' => 0,
            'packageapi' => $papi
        ), 0, -1);

$papi_packages_pids = array();
$papi_packages_labels = array();
        
foreach ($papi_packages[1] as $p){
    $papi_packages_pids[] = $p[0]['id'];
    $papi_packages_labels[] = $p[0]['label'];
}


// Bundle title
$f->add(
    new TrFormElement(_T('Bundle title','pkgs'), new InputTpl('label')),
    array("value" => $package['label'],"required" => True)
);

// Bundle version
$f->add(
    new TrFormElement(_T('Version','pkgs'), new InputTpl('version')),
    array("value" => $package['version'],"required" => True)
);

// Bundle description
$f->add(
    new TrFormElement(_T('Description','pkgs'), new InputTpl('description')),
    array("value" => $package['description'],"required" => True)
);

// Need reboot
$f->add(
    new TrFormElement(_T('Need a reboot','pkgs'), new CheckboxTpl('do_reboot')), array("value" => ($package['reboot'] == 1 ? 'checked' : ''))
);

// Associate inventory
$f->add(
    new TrFormElement(_T('Associate inventory','pkgs'), new CheckboxTpl('do_associateinventory')), array("value" => ($package['associateinventory'] == 1 ? 'checked' : ''))
);


// If sub_packages is empty (new bundle, we init it with the first package)

if (!$package['sub_packages']){
    $package['sub_packages'] = array(array(
        'pid' => $papi_packages_pids[0],
        'condition' => ''
    ));
}

// SubPackages lists

for ($i = 0 ; $i < count($package['sub_packages']) ; $i++) {
    
    $package_select = new SelectItem('sub_packages[pids][]');
    $package_select->setElements($papi_packages_labels);
    $package_select->setElementsVal($papi_packages_pids);
    
    // Fields
    $fields = array(
        $package_select,
        new InputTpl('sub_packages[conditions][]'),
        new buttonTpl('removeShare',_T('Remove'),'removeShare')
        );
    
    $values = array(
        $package['sub_packages'][$i]['pid'],
        $package['sub_packages'][$i]['condition'],
        ''
    );
    
    $f->add(
        new TrFormElement(_T('Folder','pkgs'), new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
}

// Add Share button
$addShareBtn = new buttonTpl('addShare',_T('Add folder','pkgs'));
$addShareBtn->setClass('btnPrimary');
$f->add(
    new TrFormElement('', $addShareBtn),
    array()
);

// If BackupProfile id is transmitten, we write it into the form
if ($ID) {
    $f->add(new HiddenTpl("id"), array("value" => $ID, "hide" => True));
}
elseif (isset($profile['id']))
    $f->add(new HiddenTpl("id"), array("value" => $profile['id'], "hide" => True));


$f->pop();
$f->addValidateButton("bconfirm");
$f->display();

?>

<script type="text/javascript">
jQuery(function(){
    
    var $ = jQuery;
    $('input[name*=sub_packages]').hide();

    // Function to populate select from list
    (function($, window) {
        $.fn.replaceOptions = function(options) {
          var self, $option;
      
          this.empty();
          self = this;
      
          $.each(options, function(index, option) {
            $option = $("<option></option>")
              .attr("value", option.value)
              .text(option.text);
            self.append($option);
          });
        };
    })(jQuery, window);
    
    
    $('form').submit(function(e){
       
        // Check if we have at least 2 packages
        if (jQuery('select[name*=sub_packages]').length < 2){
            alert(<?php print json_encode(_T('Error, at least two packages are required to create a bundle.', 'pkgs')); ?>);
            e.preventDefault();
            return;
        } 
        
        var selected_packages = [];
        jQuery('select[name*=sub_packages]').each(function(){
            // If there is a null package abort here
            if ($(this).val() == null){
                $(this).css('border', '1px solid red');
                e.preventDefault();
                return;
            }
            selected_packages.push($(this).val());
        });
        unique = selected_packages.filter(function(value, index, ctx) {
            return index == selected_packages.indexOf(value);
        });


        // If duplicate packages prevent form from submit
        if (selected_packages.length != unique.length){
            alert(<?php print json_encode(_T('Duplicate package detected.', 'pkgs')); ?>)
            e.preventDefault();
        }
        
    });
    
    
    
        
     // Remove Share button
     jQuery('.removeShare').click(function(){
         if (jQuery('.removeShare').length > 1)
             jQuery(this).parents('tr:first').remove();
     });
     
     
     // Add Share button
     jQuery('#addShare').click(function(){
        shareLine = jQuery('.removeShare:first').parents('tr:first').clone();
        var newline = shareLine.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find('input[type=text]').val('');
         newline.find('textarea').val('');
         newline.find('select').val(null);
//         newline.find('select option:first').attr('selected', 'selected');


         newline.find('.removeShare').click(function(){
            if (jQuery('.removeShare').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });
     
    
    window.package_list = [];
    
    $('#p_api').change(function() {
        
        var papis = <?php print json_encode($papis_by_uuid); ?>;
        
        params = [
            {
                'filter': '',
                'packageapi': papis[$(this).val()],
            },
            0,
            -1
        ]
        
        data = {
            method_name : 'msc.pa_adv_getAllPackages',
            params : params
        }
        
        $.post('<?php print urlStrRedirect("pkgs/pkgs/ajaxXMLRPCCall", array()); ?>', data,
               function(r){
                    // Parse JSON
                    r = JSON.parse(r);
                    var package_list = [];
                    for (i = 0; i< r[0]; i++) {
                        var p = r[1][i][0];
                        console.log(p.label);
                        
                        package_list.push({
                            'value' : p.id,
                            'text' : p.label
                        });
                    }
                    
                    jQuery('select[name*=sub_packages]').replaceOptions(package_list);
                    default_option = jQuery('<option value="" disabled selected></option>').text(<?php print json_encode(_T('Select a package', 'pkgs')); ?>); 
                    jQuery('select[name*=sub_packages]').prepend(default_option);
                }
        );
        
        
    }); 
    default_option = jQuery('<option value="" disabled></option>').text('Select a package'); 
    selected_default_option = jQuery('<option value="" disabled selected></option>').text('Select a package'); 
    if (jQuery('select[name*=sub_packages]').length < 2)
        jQuery('select[name*=sub_packages]').prepend(selected_default_option);
    else
        jQuery('select[name*=sub_packages]').prepend(default_option);

    
});   
   
    
</script>
