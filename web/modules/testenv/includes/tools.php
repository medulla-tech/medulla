<?php
function remove_underscore($string){
    $result = str_replace("_", " ", $string);
    return $result;
}

function add_underscore_for_url($string){
    $result = str_replace(" ", "_", $string);
    return $result;
}

function convertGointoMb($valueInGo) {
    $valueInMb = $valueInGo * 1024;
    $valueInMb = round($valueInMb, 2);
    return strval($valueInMb);
}

function parse_console_output($console_output) {
    $vm_name = '';
    $disk_size = '';
    $status = '';

    preg_match('/\+\s*create-vm\s*--name\s*(\S+)\s*/', $console_output, $matches);
    if (count($matches) > 1) {
        $vm_name = $matches[1] .' en cours de création';
    }
    preg_match('/Allocating\s*\'(\S+)\'\s*\|\s*(\d+)\s+/', $console_output, $matches);
    if (count($matches) > 2) {
        $disk_size = 'Montage du disque '. $matches[2] . ' GB';
    }
    if (strpos($console_output, 'Finished: SUCCESS') !== false) {
        $status = 'La Machine ' . $vm_name . ' a été créée avec succès';
    } else {
        $status = 'La Machine ' . $vm_name . ' n\'a pas été créée';
    }
    sleep(2);
    return array('vm_name' => $vm_name, 'disk_size' => $disk_size, 'status' => $status);
}
?>
