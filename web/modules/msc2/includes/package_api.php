<?
#
# $Id:
#

function getAllPackages() {
        $ret = xmlCall("msc.pa_getAllPackages");
        return array_map('to_packageApi', $ret);
}

function getAllMirrorPackages($mirror) {
        $ret = xmlCall("msc.pa_getAllMirrorPackages", array($mirror));
        return array_map('to_packageApi', $ret);
}

function getPackageLabel($pid) {
        return xmlCall("msc.pa_getPackageLabel", array($pid));
}

function getPackageVersion($pid) {
        return xmlCall("msc.pa_getPackageVersion", array($pid));
}

function getPackageInstallInit($pid) {
        return xmlCall("msc.pa_getPackageInstallInit", array($pid));
}

function getPackagePreCommand($pid) {
        return xmlCall("msc.pa_getPackagePreCommand", array($pid));
}

function getPackageCommand($pid) {
        return xmlCall("msc.pa_getPackageCommand", array($pid));
}

function getPackagePostCommandSuccess($pid) {
        return xmlCall("msc.pa_getPackagePostCommandSuccess", array($pid));
}

function getPackagePostCommandFailure($pid) {
        return xmlCall("msc.pa_getPackagePostCommandFailure", array($pid));
}

function getPackageFiles($pid) {
        return xmlCall("msc.pa_getPackageFiles", array($pid));
}

function getFileChecksum($file) {
        return xmlCall("msc.pa_getFileChecksum", array($file));
}

function getPackagesIds($label) {
        return xmlCall("msc.pa_getPackagesIds", array($label));
}

function getPackageId($label, $version) {
        return xmlCall("msc.pa_getPackageId", array($label, $version));
}

function isAvailable($pid, $mirror) {
        return xmlCall("msc.pa_isAvailable", array($pid, $mirror));
}

class PackageFile {
    function PackageFile($h_file) {
    }
}
class PackageCommand {
    function PackageCommand($h_cmd) {
        $this->name = $h_cmd{'name'};
        $this->command = $h_cmd{'command'};
    }
}
class PackageApi {
    function PackageApi($h_pkg) {
        $this->label = $h_pkg{'label'};
        $this->version = $h_pkg{'version'};
        $this->checksum = $h_pkg{'checksum'};
        $this->precmd = new PackageCommand($h_pkg{'precmd'});
        $this->cmd = new PackageCommand($h_pkg{'cmd'});
        $this->postcmd_ok = new PackageCommand($h_pkg{'postcmd_ok'});
        $this->postcmd_ko = new PackageCommand($h_pkg{'postcmd_ko'});
        $this->id = $h_pkg{'id'};
    }
}

function to_packageApi($h) {
    return new PackageApi($h);
}

/* advanced functions (not in the api) */
function getPackageDetails($pid) {
    return array(
        'name'=>getPackageLabel($pid),
        'version'=>getPackageVersion($pid),
        'init'=>getPackageInstallInit($pid),
        'pre'=>getPackagePreCommand($pid),
        'command'=>getPackageCommand($pid),
        'success'=>getPackagePostCommandSuccess($pid),
        'failure'=>getPackagePostCommandFailure($pid),
        'files'=>getPackageFiles($pid)
    );
}

function advGetAllPackages($machine, $filter, $start, $end) {
    return xmlCall("msc.pa_adv_getAllPackages", array($machine, $filter, $start, $end));
}

function advCountAllPackages($machine, $filter) {
    return xmlCall("msc.pa_adv_countAllPackages", array($machine, $filter));
}

?>
