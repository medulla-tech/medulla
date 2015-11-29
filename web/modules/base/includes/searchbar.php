<?php

require_once("logging-xmlrpc.inc.php");
require_once("includes/auditCodesManager.php");
$auditManager = new AuditCodesManager();

if($_GET["filtertype"] == "object" or $_GET["filtertype"] == "user"){
?>
    
    <span class="searchfield"><input type="text" class="searchfieldreal" style="width : 100px;" name="param" id="param" onkeyup="pushSearch(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onclick="document.getElementById('param').value =''; pushSearch(); return false;" />
    </span>
    
<?php
}
else {
    $lst=array();
    if($_GET["filtertype"]=="action") {   
        $lst=get_action_type(1,0); 
    }
    else if($_GET["filtertype"]=="type") {   
        $lst=get_action_type(0,1);
    }
?>      
    <select style="width:100px; vertical-align: middle;" name="param" id="param" onChange="pushSearch(); return false;">
<?php
    foreach ($lst as $key => $item){
        print "\t<option value=\"".$lst[$key]."\" >".$auditManager->getCode($item)."</option>\n";
    }    
?>
    </select>
<?php
}
