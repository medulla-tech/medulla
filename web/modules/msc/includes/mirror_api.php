<?php


function getMirror($machine) {
    return xmlCall('msc.ma_getMirror', array($machine));
}

function getMirrors($machines) {
    return xmlCall('msc.ma_getMirrors', array($machines));
}

function getFallbackMirror($machine) {
    return xmlCall('msc.ma_getFallbackMirror', array($machine));
}

function getFallbackMirrors($machines) {
    return xmlCall('msc.ma_getFallbackMirrors', array($machines));
}

function getSubPackageMirror($machine) {
    return xmlCall('msc.ma_getSubPackageMirror', array($machine));
}

function getSubPackageMirrors($machines) {
    return xmlCall('msc.ma_getSubPackageMirrors', array($machines));
}


?>
