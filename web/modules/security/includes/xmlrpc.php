<?php
/**
 * Wrappers XML-RPC pour le module Security
 */

function xmlrpc_results() {
    try {
        $res = xmlCall("security.results", array());
        return is_array($res) ? $res : [];
    } catch (Exception $e) {
        error_log("[Security] xmlrpc_results() failed: " . $e->getMessage());
        return [];
    }
}

function xmlrpc_getDetail($cve) {
    try {
        $res = xmlCall("security.getDetail", array($cve));
        return is_array($res) ? $res : null;
    } catch (Exception $e) {
        error_log("[Security] xmlrpc_getDetail($cve) failed: " . $e->getMessage());
        return null;
    }
}

function xmlrpc_getStats() {
    try {
        $res = xmlCall("security.getStats", array());
        if (!is_array($res)) {
            $res = [];
        }
        // Valeurs par défaut si non renvoyées
        return array_merge([
            'total'     => 0,
            'machines'  => 0,
            'packages'  => 0,
            'last_scan' => '-'
        ], $res);
    } catch (Exception $e) {
        error_log("[Security] xmlrpc_getStats() failed: " . $e->getMessage());
        return [
            'total'     => 0,
            'machines'  => 0,
            'packages'  => 0,
            'last_scan' => '-'
        ];
    }
}
?>
