<?

/* Class for managing audit codes */
class AuditCodesManager {

    var $codes;

    function AuditCodesManager() {
        # global audit codes
        $this->codes = array(
            'MMC_AGENT_SERVICE_START' => _("Daemon start"),
            'MMC_AGENT_SERVICE_STOP' => _("Daemon stop"),
            'MMC-AGENT' => _("mmc-agent"),
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
