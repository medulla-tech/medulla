<?php

/**
 * (c) 2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Class for managing audit codes */

class AuditCodesManager {

    var $codes;

    function AuditCodesManager() {
        # global audit codes
        $this->codes = array(
            'MMC_AGENT_SERVICE_START' => _("Daemon start"),
            'MMC_AGENT_SERVICE_STOP' => _("Daemon stop"),
            'MMC-AGENT' => _("MMC agent"),
        );
        # add audit codes for all enabled modules
        foreach($_SESSION["modulesList"] as $module) {
            $auditCodesFile = "modules/$module/includes/auditCodes.php";
            if(file_exists($auditCodesFile)) {
                require_once($auditCodesFile);
                // add codes from plugin file
                // codes array name should be $module_audit_codes
                if(isset($module_audit_codes)) {
                    $this->addCodes($module_audit_codes);
                }
            }
        }
    }

    /* function to add codes for MMC plugins */
    function addCodes($arrayCodes) {
        $this->codes = array_merge($this->codes, $arrayCodes);
    }

    function getCode($code) {
        if(isset($this->codes[$code])) {
            return $this->codes[$code];
        }
        else {
            return $code;
        }
    }
}

/* transform LDAP user uri to a simple string */
function getObjectName($ldap_uri) {
    preg_match('/[a-z]{2,3}=([^,]*)/', $ldap_uri, $matches);
    if(count($matches) > 0) {
        $uid = $matches[1];
        unset($matches);
        return $uid;
    }
    // this is not a ldap uri
    else {
        return $ldap_uri;
    }
}

?>
