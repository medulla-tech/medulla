<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

function formatFileSize($size){
    $size = intval($size);
    if (floor($size/pow(1024,3))>0)
            return sprintf("%2.2f "._T('GB','backuppc'),$size/pow(1024,3));
    else if (floor($size/pow(1024,2))>0)
            return sprintf("%2.2f "._T('MB','backuppc'),$size/pow(1024,2));
    else if (floor($size/1024)>0)
            return sprintf("%2.2f "._T('KB','backuppc'),$size/1024);
    else return sprintf("%d "._T('Bytes','backuppc'),$size);
}

require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/msc/includes/utilities.php");

global $conf;
$maxperpage = 50; //$conf["global"]["maxperpage"];

$filter = array('filter'=> $_GET["filter"], 'location'=> $_GET['location']);
$filter1 = $_GET["filter"]. '##'.$_GET['location'];

if ($_GET['location']) {
    //$filter['packageapi'] = getPApiDetail(base64_decode($_GET['location']));
    print "";
}
if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

if (isset($_GET['host']) && isset($_GET['sharename']) && isset($_GET['backupnum']) ) {
    
    $folder = (isset($_GET['folder']) && $_GET['folder']!='//')?$_GET['folder']:'/'; 
    $response = list_files($_GET['host'],$_GET['backupnum'],$_GET['sharename'],$folder,$_GET['filter']);
    
        // Check if error occured
    if ($response['err']) {
        new NotifyWidgetFailure(nl2br($response['errtext']));
        return;
    }

    $files = $response['data'];
    
    $names = $files[0];
    $paths = $files[1];
    $types = $files[3];
    $sizes = $files[5];
    $cssClasses = array();
    
    $params = array();
    for ($i=0;$i<count($names);$i++){
        $params[] = array('host'=>$_GET['host'], 'backupnum'=>$_GET['backupnum'],'sharename'=>$_GET['sharename'],'dir'=>$paths[$i]);    
        $sizes[$i] = formatFileSize($sizes[$i]);
        if ($types[$i] == 'dir'){
            $names[$i] = '<a href="#" onclick="BrowseDir(\''.$paths[$i].'\')">'.  iconv("UTF-8", "ISO-8859-1",$names[$i])."</a>";
            $cssClasses[$i] = 'folder';
            $sizes[$i] = '';
        }
        else {
            $param_str = "host=".$_GET['host']."&backupnum=".$_GET['backupnum']."&sharename=".$_GET['sharename'];
            $param_str.= "&dir=".$paths[$i];
            $names[$i] = '<a href="#" onclick="RestoreFile(\''.$param_str.'\')">'.iconv("UTF-8", "ISO-8859-1",$names[$i])."</a>";         
            $cssClasses[$i] = 'file';
        }
        $names[$i]=sprintf('<input type="checkbox" name="f%d" value="%s" /> &nbsp;&nbsp;',$i,$paths[$i]).$names[$i];
    }

    if ($folder!='/'){
        $parentfolderlink = '<a href="#" onclick="BrowseDir(\''.dirname($folder).'/\')">.. (Parent dir)</a>';
        $names = array_merge(array($parentfolderlink),$names);   
        $cssClasses = array_merge(array('folder'),$cssClasses);
        $sizes = array_merge(array(''),$sizes);
        $params = array_merge(array(''),$params);
    }
    
    $count = count($names);

    //print($_GET["filter"]."=");
    //print($_GET["location"]);

    $n = new OptimizedListInfos($names,_T("Host name", "backuppc"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($sizes, _T("Size", "backuppc"));
    //$n->addExtraInfo($checkboxes, "");
    $n->setMainActionClasses($cssClasses);
    //$n->setCssClass("machineName");
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter1));
    $n->start = isset($_GET['start'])?$_GET['start']:0;
    $n->end = isset($_GET['end'])?$_GET['end']:$maxperpage;
    $n->setParamInfo($params); // Setting url params
    
    $n->addActionItem(new ActionPopupItem(_T("View all versions"), "viewFileVersions", "display", "dir", "backuppc", "backuppc"));

    print '<br/><br/><form id="restorefiles" method="post" action="">'; 
    printf('<input type="hidden" name="host" value="%s" />',$_GET['host']);
    printf('<input type="hidden" name="backupnum" value="%s" />',$_GET['backupnum']);
    printf('<input type="hidden" name="sharename" value="%s" />',$_GET['sharename']);
    print('<input type="hidden"  name="restoredir" id="restoredir" value=""  />');
    $n->display();
        

}

?>
<input id="btnRestoreZip" type="button" value="<?php print _T('Download selected (ZIP)','backuppc'); ?>" class="btnPrimary" />
<input type="button" value="<?php print _T('Restore to Host','backuppc'); ?>" class="btnPrimary" onclick="showPopup(event,'main.php?module=backuppc&submod=backuppc&action=restorePopup'); return false;" />
</form>

<script type="text/javascript">
jQuery(function(){
    jQuery('input#btnRestoreZip').click(function(){
        form = jQuery('#restorefiles').serialize();
        
        jQuery.ajax({
            type: "POST",
            url: "<?php  echo 'main.php?module=backuppc&submod=backuppc&action=restoreZip'; ?>",
            data: form,

            success: function(data){
                setTimeout("location.reload(true);",5);
        }
        });
        return false;

    });
});

</script>