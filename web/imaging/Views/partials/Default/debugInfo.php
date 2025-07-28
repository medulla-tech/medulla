##############
# DEBUG INFO #
##############

#
#
# Server Info
#
#
<?php 
if(!empty($datas['datas']['server'])){
    echo '# Id:'.$datas['datas']['server']['id'].'
';
    echo '# Name:'.$datas['datas']['server']['name'].'
';
    echo '# Uuid:'.$datas['datas']['server']['packageserver_uuid'].'
';
    echo '# Entity:'.$datas['datas']['server']['completename'].'
';
    echo '# Location:'.$datas['datas']['server']['uuid'].'
';
    echo '# Url:'.$datas['datas']['server']['url'].'
';
}
?>

#
#
# Menu Info
#
#
<?php
if(!empty($datas['datas']['menu'])){
    echo '# Id : '.$datas['datas']['menu']['id'].'
';
    echo '# Name : '.$datas['datas']['menu']['name'].'
';
    echo '# Timeout : '.$datas['datas']['menu']['timeout'].'
';
    echo '# Default Item Id : '.$datas['datas']['menu']['fk_default_item'].'
';

}

?>

#
#
# Items Info
#
#
<?php
if(!empty($datas['datas']['items'])){
    $countBS=0;
    $countI=0;
    $countV=0;
    $default = "";
    $items = [];
    for($i = 0; $i<count($datas['datas']['items']); $i++ ){
        // for each element add the name in $items array and count them
        if($datas['datas']['items'][$i]['itemid'] == $datas['datas']['menu']['fk_default_item']){
            $default = $datas['datas']['items'][$i]['name'];
            $items[] = $datas['datas']['items'][$i]['name'].' (default)';
        }
        else{
            $items[] = $datas['datas']['items'][$i]['name'];
        }
        $countBS += $datas['datas']['items'][$i]['type'] == 'bootservice' ? 1 : 0;
        if($datas['datas']['items'][$i]['type'] == 'image'){
            $countI ++;
            $countV += count($datas['datas']['items'][$i]['virtuals']);
        }
    }
    echo '# BootServices Count: '.$countBS.'
';
    echo "# Images Count: ".$countI.'
';
    echo "# Virtuals Count: ".$countV.'
';
    echo "# Total Count: ".$countV+$countI+$countBS.'
';
    echo '# Default Item: '.$default.'
';
}
?>


#
#
# Security Info
#
#


#
#
# Inventory info
#
#


#
#
# Template Info
#
#


#
#
# Target Info
#
#


#
#
# Group info
#
#


#
#
# Multicast Info
#
#

