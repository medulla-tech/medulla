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

require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/backuppc/includes/functions.php");
require_once("modules/backuppc/includes/html.inc.php");

// ===========================================================================
// ===========================================================================

$package = array();

// display an edit config form 
$f = new ValidatingForm();
$f->push(new Table());

$host = $_GET['objectUUID'];


// Get backup Nums =======================================

$response = get_backup_list($host);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

if (count($response['data']))
    $backups = $response['data'][0];
else {
    print _T('There is no backup point for this machine.','backuppc');
    return;
}

// Get all backup shares =================================

$sharenames = array();
// Get all sharenames
foreach ($backups as $backup_num){
    $response = get_share_names($host, $backup_num);
    
    if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
    }
    
    $sharenames = array_merge($sharenames,$response['data']);
}

$sharenames = array_unique($sharenames);

// ========= BUILDING FORM ========================================

$f->add(new HiddenTpl("host"), array("value" => $host, "hide" => True));
 
// =====================================================================
// FILENAME
// =====================================================================
 
$f->add(
    new TrFormElement(_T('File name','backuppc'), new InputTpl('filename')),
    array("value" => isset($_POST['filename'])?$_POST['filename']:'',"required" => True)
);

// =============================================================================
// BACKUP NUM SELECT FIELD  =====================================================
// =============================================================================

$sel = new SelectItem("backupnum");
$list = array();
$list[-1] = _T('All','backuppc');

foreach ($backups as $num)
    $list[intval($num)] = _T('Backup#','backuppc').$num;  #TODO : Change this to backuptime
$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));

if (isset($_POST['backupnum']))
    $sel->setSelected($_POST['backupnum']);
else
    $sel->setSelected(-1);

 $f->add(
    new TrFormElement(_T("Backup point","backuppc"), $sel,
    array())
);

// =============================================================================
// SHARENAME SELECT FIELD  =====================================================
// =============================================================================

$sel = new SelectItem("sharename");
$list = array();
$list[-1] = _T('All','backuppc');

foreach ($sharenames as $sharename)
    $list[$sharename] = $sharename;  #TODO : Change this to backuptime
$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));

if (isset($_POST['sharename']))
    $sel->setSelected($_POST['sharename']);
else
    $sel->setSelected(-1);

 $f->add(
    new TrFormElement(_T("Folder","backuppc"), $sel,
    array())
);


// =====================================================================
// MIN AND MAX FILESIZE
// =====================================================================

$f->add(new HiddenTpl("minsize"), array(
    "value" => isset($_POST['minsize'])?$_POST['minsize']:'-1',
    "hide" => True));
$f->add(new HiddenTpl("maxsize"), array(
    "value" => isset($_POST['maxsize'])?$_POST['maxsize']:'-1',
    "hide" => True));

// =============================================================================
// SHARENAME SELECT FIELD  =====================================================
// =============================================================================

$sel = new SelectItem("filesize");

$sizes = array(
    '0' => _T('Any','backuppc'),
    '1' => _T('Less than 1 Mb','backuppc'),
    '2' => _T('1 Mb to 10 Mb','backuppc'),
    '3' => _T('10 Mb to 100 Mb','backuppc'),
    '4' => _T('Greater than 100 Mb','backuppc')
);
$sel->setElements(array_values($sizes));
$sel->setElementsVal(array_keys($sizes));

if (isset($_POST['filesize']))
    $sel->setSelected($_POST['filesize']);
else
    $sel->setSelected(0);

 $f->add(
    new TrFormElement(_T("File size","backuppc"), $sel,
    array())
);

/*
$f->add(
    new TrFormElement(_T('Minimum file size','backuppc'), new InputTpl('minsize')),
    array("value" => isset($_POST['minsize'])?$_POST['minsize']:'',"required" => True)
);

$f->add(
    new TrFormElement(_T('Maximum file size','backuppc'), new InputTpl('maxsize')),
    array("value" => isset($_POST['maxsize'])?$_POST['maxsize']:'',"required" => True)
);
*/
// =====================================================================

$f->pop();
$f->addButton("bsearch",_T('Search','backuppc'));
$f->display();

// ===== AJAX FILE TABLE ==============================================

$ajax = new AjaxFilterLocation(urlStrRedirect("backuppc/backuppc/ajaxFileSearch"),'container','location',$_POST);

$fils = array('.');
$fils_v = array('.');
$ajax->setElements($fils);
$ajax->setElementsVal($fils_v);
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();

?>

<script src="modules/backuppc/lib/jquery-1.10.1.min.js"></script>
<script type="text/javascript">
// Avoid prototype <> jQuery conflicts
jQuery.noConflict();

jQuery(function(){
    
    // File size selection
    jQuery('select#filesize').change(function(){
        switch (jQuery('select#filesize').val()) {
            case "1":  // Less than 1Mb
                jQuery('input[name=minsize]').val(-1);
                jQuery('input[name=maxsize]').val(1048576);
                break;
            case "2": // 1 Mb to 10 Mb
                jQuery('input[name=minsize]').val(1048576);
                jQuery('input[name=maxsize]').val(10485760);
                break;
            case "3": // 10 Mb to 100Mb
                jQuery('input[name=minsize]').val(10485760);
                jQuery('input[name=maxsize]').val(104857600);
                break;
            case "4": // > 100 Mb
                jQuery('input[name=minsize]').val(104857600);
                jQuery('input[name=maxsize]').val(-1);
                break;
            default: 
                jQuery('input[name=minsize]').val(-1);
                jQuery('input[name=maxsize]').val(-1);
                break;
        }
    });
      
});   
   
</script>



<div id="restoreDiv"></div>

<script type="text/javascript">
function BrowseDir(dir){
    jQuery('#<?php echo  $ajax->divid; ?>').load('<?php echo  $ajax->url; ?>folder='+dir+'<?php echo  $ajax->params ?>');
}

function RestoreFile(paramstr){
    jQuery('#restoreDiv').load('<?php echo urlStrRedirect("backuppc/backuppc/ajaxRestoreFile"); ?>&'+paramstr);
    setTimeout("refresh();",4000);
}

</script>

<?php
// Downloaded files table
include("modules/backuppc/backuppc/ajaxDownloadsTable.php");

?>