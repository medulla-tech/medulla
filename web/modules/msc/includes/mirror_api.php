<?php


function getMirror($uuid) {
    return xmlCall('msc.ma_getMirror', array($uuid));
}

function getMirrors($uuids) {
    return xmlCall('msc.ma_getMirrors', array($uuids));
}

function getFallbackMirror($uuid) {
    return xmlCall('msc.ma_getFallbackMirror', array($uuid));
}

function getFallbackMirrors($uuids) {
    return xmlCall('msc.ma_getFallbackMirrors', array($uuids));
}

function getSubPackageMirror($uuid) {
    return xmlCall('msc.ma_getSubPackageMirror', array($uuid));
}

function getSubPackageMirrors($uuids) {
    return xmlCall('msc.ma_getSubPackageMirrors', array($uuids));
}


?>
