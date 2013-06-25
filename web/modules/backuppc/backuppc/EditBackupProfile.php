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

require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/backuppc/includes/html.inc.php");
require_once("modules/backuppc/includes/functions.php");


// ==================================================================================
// Receiving POST DATA
// ==================================================================================

// Getting Profile ID (if specified) else 0
$ID = intval(@max($_GET['id'],$_POST['id']));

if (isset($_POST['bconfirm'])){
    $cfg = array(
        'profilename' => $_POST['profilename'],
        'encoding' => $_POST['encoding'],
        'sharenames'  => implode("\n",$_POST['sharenames']),
        'excludes'    => implode("||",$_POST["excludes"])
    );
    
    if ($ID) {
        $profile = edit_backup_profile($ID,$cfg);
        // APPLY PROFILE TO ALL CONCERNED HOSTS
        apply_backup_profile($ID);
    }
    else
        $profile = add_backup_profile($cfg);
    
}
else
    if ($ID)
        $profile = edit_backup_profile($ID,array(''=>''));
    else
        $profile = array('profilename'=>'','sharenames'=>'','excludes'=>'');

// ==================================================================================

// Add or Edit
if ($ID)
    $p = new PageGenerator(_T("Edit fileset", "backuppc"));
else 
    $p = new PageGenerator(_T("Add fileset", "backuppc"));

$p->setSideMenu($sidemenu);
$p->display();

// display an edit config form 
$f = new ValidatingForm();
$f->push(new Table());

// Profile name
$f->add(
    new TrFormElement(_T('Name','backuppc'), new InputTpl('profilename')),
    array("value" => $profile['profilename'],"required" => True)
);

// Client host encoding

$sel = new SelectItem("encoding");
$list = array(
    "utf8"=>'UTF8',
    "cp1252" => _T('Windows-1252 - Western europe','backuppc'),
    "cp874" => _T('Windows-874 - Thai','backuppc'),
    "cp932" => _T('Windows-932 - Japanese','backuppc'),
    "cp936" => _T('Windows-936 - Chinese (simplified)','backuppc'),
    "cp949" => _T('Windows-949 - Korean','backuppc'),
    "cp950" => _T('Windows-950 - Chinese (traditional)','backuppc'),
    "cp1250" => _T('Windows-1250 - Latin (Central europe)','backuppc'),
    "cp1251" => _T('Windows-1251 - Cyrillic','backuppc'),
    "cp1253" => _T('Windows-1253 - Greek','backuppc'),
    "cp1254" => _T('Windows-1254 - Turkish','backuppc'),
    "cp1255" => _T('Windows-1255 - Hebrew','backuppc'),
    "cp1256" => _T('Windows-1256 - Arabic','backuppc'),
    "cp1257" => _T('Windows-1257 - Latin (Baltic languages)','backuppc'),
    "cp1258" => _T('Windows-1258 - Vietnamese','backuppc')
    );

$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));
$sel->setSelected($profile['encoding']);

 $f->add(
    new TrFormElement(_T("Client encoding","backuppc"), $sel,
    array())
);

// Exclude lists
$sharenames = explode("\n",$profile['sharenames']);
$i = 0;


$profile['excludes'] = explode('||',$profile['excludes']);

for ($i = 0 ; $i < count($sharenames) ; $i++) {
    
    
    // Fields
    $fields = array(
        new InputTpl('sharenames[]'),
        new textTpl(_T('Excluded files','backuppc')),
        new TextareaTpl('excludes[]'),
        new buttonTpl('removeShare',_T('Remove'),'removeShare')
        );
    
    $values = array(
        $sharenames[$i],
        '',
        $profile['excludes'][$i],
        ''
    );
    
    $f->add(
        new TrFormElement(_T('Folder','backuppc'), new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
}

// Add Share button
$addShareBtn = new buttonTpl('addShare',_T('Add folder','backuppc'));
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

<script src="modules/backuppc/lib/jquery-1.10.1.min.js"></script>
<script type="text/javascript">
// Avoid prototype <> jQuery conflicts
jQuery.noConflict();

jQuery(function(){
    
    shareLine = jQuery('.removeShare:first').parents('tr:first').clone();
        
     // Remove Share button
     jQuery('.removeShare').click(function(){
         if (jQuery('.removeShare').length > 1)
             jQuery(this).parents('tr:first').remove();
     });
     
     
     // Add Share button
     jQuery('#addShare').click(function(){
        var newline = shareLine.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find('input[type=text]').val('');
         newline.find('textarea').val('');

         newline.find('.removeShare').click(function(){
            if (jQuery('.removeShare').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });
    
});   
   
    
</script>
